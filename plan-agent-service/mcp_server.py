"""MCP Server：将计划网站任务 API 暴露给 Claude Desktop / Cursor 等 MCP 客户端。"""

import asyncio
import os
from datetime import date, timedelta

import httpx
from mcp.server.fastmcp import FastMCP

SPRING_API_BASE = os.getenv("SPRING_API_BASE", "http://localhost:8080").rstrip("/")

mcp = FastMCP("plan-website-tasks")


async def _http_get(path: str, params: dict | None = None) -> list | dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{SPRING_API_BASE}{path}", params=params)
        response.raise_for_status()
        return response.json()


async def _http_post(path: str, payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{SPRING_API_BASE}{path}", json=payload)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_tasks(email: str, task_date: str) -> str:
    """查询指定用户、指定日期的任务列表。task_date 格式 YYYY-MM-DD。"""
    tasks = await _http_get("/api/tasks", {"email": email, "date": task_date})
    if not tasks:
        return f"{task_date} 暂无任务"
    lines = [f"[{'完成' if t.get('completed') else '未完成'}] {t.get('content')}" for t in tasks]
    return f"{task_date}:\n" + "\n".join(lines)


@mcp.tool()
async def get_week_tasks(email: str, week_start: str) -> str:
    """查询从 week_start（周一）起连续 7 天的任务概览。"""
    start = date.fromisoformat(week_start)
    chunks = []
    for offset in range(7):
        current = (start + timedelta(days=offset)).isoformat()
        tasks = await _http_get("/api/tasks", {"email": email, "date": current})
        if not tasks:
            chunks.append(f"{current}: 无任务")
        else:
            summary = "；".join(t.get("content", "") for t in tasks)
            chunks.append(f"{current}: {summary}")
    return "\n".join(chunks)


@mcp.tool()
async def create_task(user_id: int, content: str, task_date: str, plan_type: str = "daily") -> str:
    """创建一条每日或每周任务；每周任务的 task_date 必须是目标周周一。"""
    task = await _http_post(
        "/api/task",
        {
            "content": content,
            "taskDate": task_date,
            "planType": "weekly" if plan_type.lower() == "weekly" else "daily",
            "completed": False,
            "user": {"id": user_id},
        },
    )
    return f"已创建: {task.get('taskDate')} - {task.get('content')}"


if __name__ == "__main__":
    mcp.run()

from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Awaitable, Callable, TypeVar

import httpx

from app.config import settings
from generated.plan_api_client import Client
from generated.plan_api_client import errors as api_errors
from generated.plan_api_client.api.focus_controller import active, delete, sessions, start, stop
from generated.plan_api_client.api.plan_controller import (
    analyze_task,
    complete_subtask,
    create_recurring_task,
    delete_recurring_task,
    delete_task,
    get_recurring_tasks,
    get_tasks,
    save_task,
    update_recurring_task,
    update_task,
    update_task_status,
)
from generated.plan_api_client.api.statistics_controller import statistics
from generated.plan_api_client.models.focus_start_request import FocusStartRequest
from generated.plan_api_client.models.recurring_task import RecurringTask
from generated.plan_api_client.models.task import Task
from generated.plan_api_client.models.update_task_status_status import UpdateTaskStatusStatus

T = TypeVar("T")


class BackendGatewayError(RuntimeError):
    """Stable exception exposed to tools and graph nodes."""


class BackendGateway:
    """Adapter between Agent-friendly dictionaries and the generated OpenAPI client.

    This layer contains no URL paths or HTTP verbs. Regeneration owns transport details;
    the gateway owns DTO conversion, safe response shaping, and stable errors.
    """

    def __init__(self) -> None:
        self.client = Client(
            base_url=settings.spring_api_base.rstrip("/"),
            timeout=httpx.Timeout(30.0),
            raise_on_unexpected_status=True,
        )

    async def _invoke(self, call: Callable[..., Awaitable[T]], **kwargs: Any) -> T:
        try:
            return await call(client=self.client, **kwargs)
        except httpx.ConnectError as exc:
            raise BackendGatewayError(f"无法连接后端服务：{settings.spring_api_base}") from exc
        except httpx.TimeoutException as exc:
            raise BackendGatewayError("后端服务请求超时") from exc
        except api_errors.UnexpectedStatus as exc:
            body = exc.content.decode("utf-8", errors="replace")[:300]
            raise BackendGatewayError(f"后端接口返回异常状态 {exc.status_code}：{body}") from exc

    @staticmethod
    def _safe(value: Any) -> Any:
        """Convert generated models to JSON data and remove sensitive fields recursively."""
        if hasattr(value, "to_dict"):
            value = value.to_dict()
        if isinstance(value, list):
            return [BackendGateway._safe(item) for item in value]
        if isinstance(value, dict):
            return {
                key: BackendGateway._safe(item)
                for key, item in value.items()
                if key.lower() not in {"password", "accesskeysecret", "access_key_secret"}
            }
        return value

    @staticmethod
    def _compact(value: dict[str, Any]) -> dict[str, Any]:
        """Omit optional nulls so generated models serialize them as absent, not invalid values."""
        return {key: item for key, item in value.items() if item is not None}

    @staticmethod
    def _required(value: T | None, operation: str) -> T:
        if value is None:
            raise BackendGatewayError(f"后端接口 {operation} 未返回预期数据")
        return value

    async def get_tasks(self, email: str, task_date: str, plan_type: str = "daily") -> list[dict]:
        result = await self._invoke(get_tasks.asyncio, email=email, date=task_date, plan_type=plan_type)
        return self._safe(result or [])

    async def get_week_tasks(self, email: str, week_start: str) -> dict[str, list[dict]]:
        start_date = date.fromisoformat(week_start)
        return {
            (start_date + timedelta(days=offset)).isoformat(): await self.get_tasks(
                email, (start_date + timedelta(days=offset)).isoformat()
            )
            for offset in range(7)
        }

    async def create_task(self, user_id: int, content: str, task_date: str, plan_type: str = "daily",
                          completed: bool = False,
                          priority: str = "MEDIUM", start_time: str | None = None,
                          end_time: str | None = None, deadline: str | None = None,
                          estimated_minutes: int | None = None) -> dict:
        body = Task.from_dict(self._compact({"content": content, "taskDate": task_date,
            "planType": "weekly" if plan_type.lower() == "weekly" else "daily", "completed": completed,
            "status": "COMPLETED" if completed else "TODO", "priority": priority,
            "startTime": start_time, "endTime": end_time, "deadline": deadline,
            "estimatedMinutes": estimated_minutes, "user": {"id": user_id}}))
        result = self._required(await self._invoke(save_task.asyncio, body=body), "saveTask")
        return self._safe(result)

    async def analyze_task(self, payload: dict[str, Any]) -> dict:
        body = Task.from_dict(self._compact({"id": payload.get("id"), "content": payload["content"],
            "taskDate": payload.get("taskDate") or payload.get("task_date"), "planType": "daily",
            "status": "TODO", "priority": payload.get("priority", "MEDIUM"),
            "startTime": payload.get("startTime") or payload.get("start_time"),
            "endTime": payload.get("endTime") or payload.get("end_time"), "deadline": payload.get("deadline"),
            "estimatedMinutes": payload.get("estimatedMinutes") or payload.get("estimated_minutes"),
            "user": {"id": payload["user_id"]}}))
        result = self._required(await self._invoke(analyze_task.asyncio, body=body), "analyzeTask")
        return self._safe(result)

    async def update_task(self, task_id: int, payload: dict) -> dict:
        result = self._required(await self._invoke(update_task.asyncio, id=task_id,
            body=Task.from_dict(self._compact(payload))), "updateTask")
        return self._safe(result)

    async def set_task_status(self, task_id: int, status: str) -> dict:
        result = self._required(await self._invoke(update_task_status.asyncio, id=task_id,
            status=UpdateTaskStatusStatus(status)), "updateTaskStatus")
        return self._safe(result)

    async def complete_task(self, task_id: int, completed: bool) -> dict:
        result = self._required(await self._invoke(complete_task.asyncio, id=task_id, completed=completed), "completeTask")
        return self._safe(result)

    async def complete_subtask(self, subtask_id: int, completed: bool) -> dict:
        result = self._required(await self._invoke(complete_subtask.asyncio, id=subtask_id, completed=completed), "completeSubtask")
        return self._safe(result)

    async def delete_task(self, task_id: int) -> None:
        await self._invoke(delete_task.asyncio, id=task_id)

    async def get_recurring_tasks(self, email: str) -> list[dict]:
        return self._safe(await self._invoke(get_recurring_tasks.asyncio, email=email) or [])

    async def create_recurring_task(self, payload: dict) -> dict:
        result = self._required(await self._invoke(create_recurring_task.asyncio,
            body=RecurringTask.from_dict(self._compact(payload))), "createRecurringTask")
        return self._safe(result)

    async def update_recurring_task(self, rule_id: int, payload: dict) -> dict:
        result = self._required(await self._invoke(update_recurring_task.asyncio, id=rule_id,
            body=RecurringTask.from_dict(self._compact(payload))), "updateRecurringTask")
        return self._safe(result)

    async def delete_recurring_task(self, rule_id: int) -> None:
        await self._invoke(delete_recurring_task.asyncio, id=rule_id)

    async def get_active_focus(self, email: str) -> dict | None:
        return self._safe(await self._invoke(active.asyncio, email=email))

    async def get_focus_sessions(self, email: str, from_date: str, to_date: str) -> list[dict]:
        return self._safe(await self._invoke(sessions.asyncio, email=email, from_=from_date, to=to_date) or [])

    async def start_focus(self, user_id: int, task_id: int | None, title: str | None) -> dict:
        body = FocusStartRequest.from_dict({"userId": user_id, "taskId": task_id, "title": title})
        return self._safe(self._required(await self._invoke(start.asyncio, body=body), "startFocus"))

    async def stop_focus(self, session_id: int, note: str | None) -> dict:
        return self._safe(self._required(await self._invoke(stop.asyncio, id=session_id, note=note), "stopFocus"))

    async def delete_focus(self, session_id: int) -> None:
        await self._invoke(delete.asyncio, id=session_id)

    async def get_statistics(self, email: str, from_date: str, to_date: str) -> dict:
        result = self._required(await self._invoke(statistics.asyncio, email=email, from_=from_date, to=to_date), "statistics")
        return self._safe(result)


backend_gateway = BackendGateway()

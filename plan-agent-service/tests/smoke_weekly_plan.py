import asyncio
from datetime import date, timedelta

from app.graph import planner_node


async def main() -> None:
    state = {
        "message": (
            "给下一周的每周规划安排任务：1.做完code agent 2.把failcomp的论文初稿写出来 "
            "3.刷leetcode 4.把agent的题刷完 5.进行新idea，如果效果一般就规划一个新的。"
        ),
        "history": [],
        "conversation_summary": "",
        "pending_action": {},
        "existing_tasks": [],
        "plan": {},
        "analyses": [],
        "feedback": "",
        "revision_count": 0,
    }
    result = await planner_node(state)
    plan = result["plan"]
    next_monday = date.today() - timedelta(days=date.today().weekday()) + timedelta(weeks=1)
    assert plan["planning_mode"] == "weekly_goals", plan
    assert len(plan["tasks"]) == 5, plan
    assert all(task["plan_type"] == "weekly" for task in plan["tasks"]), plan
    assert all(task["task_date"] == next_monday.isoformat() for task in plan["tasks"]), plan
    print(plan)


if __name__ == "__main__":
    asyncio.run(main())

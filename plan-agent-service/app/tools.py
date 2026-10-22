import json
from contextvars import ContextVar
from datetime import date, timedelta
from typing import Any, Literal
from langchain_core.tools import tool
from app.backend_gateway import backend_gateway
from app.observability import trace_tool
_context: ContextVar[dict[str, Any]] = ContextVar("request_context", default={})
def set_request_context(email: str, user_id: int):
    return _context.set({"email": email, "user_id": user_id, "data_changes": {}})


def clear_request_context(token=None) -> None:
    if token is not None: _context.reset(token)


def mark_data_changed(resource: str, *dates: str | None) -> None:
    """记录本次 Agent 请求产生的数据变化，供 SSE 在回答后通知前端。"""
    context = _context.get()
    changes = context.setdefault("data_changes", {})
    known_dates = changes.setdefault(resource, set())
    known_dates.update(value for value in dates if value)


def consume_data_changes() -> list[dict[str, Any]]:
    """将本次请求的数据变化合并为每种资源一个业务事件。"""
    changes = _context.get().get("data_changes", {})
    events = [
        {"type": "data_changed", "resource": resource, "dates": sorted(dates)}
        for resource, dates in changes.items()
    ]
    changes.clear()
    return events
def _email() -> str: return str(_context.get()["email"])
def _user_id() -> int: return int(_context.get()["user_id"])
def _json(value: Any) -> str: return json.dumps(value, ensure_ascii=False, default=str)
@tool
@trace_tool
async def get_tasks(task_date: str, plan_type: str = "daily") -> str:
    """查询当前用户指定日期和计划类型的任务。
    Args:
        task_date: 查询日期，格式为 YYYY-MM-DD。plan_type=weekly 时必须传目标自然周的周一日期，
            不能传今天或该周内任意一天；例如查询 2026-09-14 至 2026-09-20，应传 2026-09-14。
        plan_type: 计划类型，daily 表示每日任务，weekly 表示每周规划任务，默认 daily。
    Returns:
        任务列表，每项包含任务 ID、内容、日期、状态、优先级、时间、提醒和子任务等字段。
    Usage:
        用于查询某一天的任务，或在修改、删除、更新状态前查找准确任务 ID。
    Restrictions:
        只读取当前用户的数据，不创建或修改任务；不得猜测不存在的任务 ID。
    """
    return _json(await backend_gateway.get_tasks(_email(), task_date, plan_type))
@tool
@trace_tool
async def get_week_tasks(week_start: str) -> str:
    """查询当前用户一个自然周内的全部每日任务。

    Args:
        week_start: 目标自然周的周一日期，格式为 YYYY-MM-DD，例如 2026-09-07。

    Returns:
        以日期为键的任务字典，覆盖从 week_start 开始连续七天。

    Usage:
        用于本周任务、指定周任务明细及按周汇总；若需要后端计算的完成率、逾期或专注统计，配合 get_statistics 使用。

    Restrictions:
        week_start 应当是星期一；该工具只查询，不修改任务。
    """
    return _json(await backend_gateway.get_week_tasks(_email(), week_start))

@tool
@trace_tool
async def analyze_task(content: str, task_date: str, priority: str = "MEDIUM", start_time: str | None = None,
                       end_time: str | None = None, deadline: str | None = None,
                       estimated_minutes: int | None = None, task_id: int | None = None) -> str:
    """分析一个候选任务的时间安排是否合理，不写入数据库。

    Args:
        content: 候选任务的内容。
        task_date: 任务日期，格式为 YYYY-MM-DD。
        priority: 优先级，可用 LOW、MEDIUM、HIGH、URGENT，默认 MEDIUM。
        start_time: 开始时间，建议使用 HH:mm 或后端接受的时间格式；可为空。
        end_time: 结束时间，必须晚于开始时间；可为空。
        deadline: 截止时间，使用后端接受的 ISO 日期时间格式；可为空。
        estimated_minutes: 预计用时，单位为分钟；可为空。
        task_id: 移动或修改已有任务时传入原任务 ID，避免与自身误判冲突；新任务可为空。

    Returns:
        合理性结果，包括 reasonable、容量、剩余时间以及冲突、负载、休息和截止时间警告。

    Usage:
        创建任务或调整任务时间前优先使用；分析完成不代表任务已经创建。

    Restrictions:
        只执行检测，不创建、更新或删除任何数据。
    """
    payload = {"id": task_id, "user_id": _user_id(), "content": content, "task_date": task_date,
               "priority": priority, "start_time": start_time, "end_time": end_time,
               "deadline": deadline, "estimated_minutes": estimated_minutes}
    return _json(await backend_gateway.analyze_task(payload))

@tool
@trace_tool
async def create_task(content: str, task_date: str, plan_type: Literal["daily", "weekly"] = "daily",
                      priority: str = "MEDIUM", start_time: str | None = None,
                      end_time: str | None = None, deadline: str | None = None,
                      estimated_minutes: int | None = None) -> str:
    """为当前用户创建一个单独任务。
    Args:
        content: 任务内容，不能为空。
        task_date: 任务日期，格式为 YYYY-MM-DD。plan_type=weekly 时必须使用目标自然周的周一日期。
        plan_type: daily 创建每日任务；weekly 创建每周规划目标。用户明确说“每周规划”或“周目标”时使用 weekly。
        priority: 优先级，可用 LOW、MEDIUM、HIGH、URGENT，默认 MEDIUM。
        start_time: 开始时间；可为空。
        end_time: 结束时间；可为空。
        deadline: 截止时间，使用 ISO 日期时间格式；可为空。
        estimated_minutes: 预计用时，单位为分钟；可为空。
    Returns:
        后端创建后的完整任务，包括真实任务 ID。
    Usage:
        仅在用户明确要求创建单项任务时使用；daily 涉及时间安排时先调用 analyze_task。
    Restrictions:
        不用于未经确认的批量规划写入，不得虚构日期、时间或用户要求。
    """
    result = await backend_gateway.create_task(_user_id(), content, task_date, plan_type=plan_type, priority=priority,
        start_time=start_time, end_time=end_time, deadline=deadline, estimated_minutes=estimated_minutes)
    mark_data_changed("tasks", task_date)
    return _json(result)
@tool
@trace_tool
async def update_task(task_id: int, content: str, task_date: str, plan_type: str = "daily", status: str = "TODO",
                      priority: str = "MEDIUM", start_time: str | None = None, end_time: str | None = None,
                      deadline: str | None = None, estimated_minutes: int | None = None,
                      actual_minutes: int | None = None, reminder_enabled: bool = False,
                      reminder_channel: str = "EMAIL", reminder_minutes_before: int = 30,
                      subtasks: list[dict] | None = None) -> str:
    """按照任务 ID 完整更新一个已有任务。

    Args:
        task_id: 要更新的真实任务 ID。
        content: 更新后的完整任务内容。
        task_date: 更新后的任务日期，格式为 YYYY-MM-DD。
        plan_type: 计划类型，daily 或 weekly。
        status: 状态，可用 TODO、IN_PROGRESS、COMPLETED、POSTPONED、CANCELLED。
        priority: 优先级，可用 LOW、MEDIUM、HIGH、URGENT。
        start_time: 更新后的开始时间；可为空。
        end_time: 更新后的结束时间；可为空。
        deadline: 更新后的截止时间；可为空。
        estimated_minutes: 更新后的预计分钟数；可为空。
        actual_minutes: 实际投入分钟数；可为空。
        reminder_enabled: 是否启用提醒。
        reminder_channel: 提醒渠道，EMAIL 或 SMS。
        reminder_minutes_before: 提前提醒分钟数。
        subtasks: 完整的子任务列表；可为空列表。

    Returns:
        更新后的完整任务记录。

    Usage:  
        先调用 get_tasks 或 get_week_tasks 获取真实 ID 和全部现值，再仅修改用户指定字段并保留其他字段。

    Restrictions:
        这是完整更新而非局部 PATCH；不得使用默认值覆盖用户未要求修改的现有字段。
    """
    payload = {"content": content, "taskDate": task_date, "planType": plan_type, "status": status,
        "priority": priority, "startTime": start_time, "endTime": end_time, "deadline": deadline,
        "estimatedMinutes": estimated_minutes, "actualMinutes": actual_minutes, "reminderEnabled": reminder_enabled,
        "reminderChannel": reminder_channel, "reminderMinutesBefore": reminder_minutes_before, "subtasks": subtasks or []}
    result = await backend_gateway.update_task(task_id, payload)
    mark_data_changed("tasks", task_date)
    return _json(result)

@tool
@trace_tool
async def set_task_status(task_id: int, status: str) -> str:
    """修改一个已有任务的状态。
    Args:
        task_id: 要修改的真实任务 ID。
        status: 新状态，只能使用 TODO、IN_PROGRESS、COMPLETED、POSTPONED、CANCELLED。
    Returns:
        状态更新后的完整任务记录。
    Usage:
        用户要求开始、完成、推迟、取消或重新任务时使用；不知道 ID 时先查询任务。
    Restrictions:
        只修改状态，不用于修改任务内容或时间；不得猜测任务 ID。
    """
    result = await backend_gateway.set_task_status(task_id, status.upper())
    mark_data_changed("tasks")
    return _json(result)

@tool
@trace_tool
async def complete_subtask(subtask_id: int, completed: bool = True) -> str:
    """完成或重新打开一个检查清单子任务。

    Args:
        subtask_id: 子任务的真实 ID，不是父任务 ID。
        completed: true 表示完成，false 表示恢复为未完成，默认 true。

    Returns:
        更新后的子任务记录。

    Usage:
        用户明确指定某个检查清单项的完成状态时使用。

    Restrictions:
        不修改父任务的其他字段；必须使用查询结果中的真实子任务 ID。
    """
    result = await backend_gateway.complete_subtask(subtask_id, completed)
    mark_data_changed("tasks")
    return _json(result)

@tool
@trace_tool
async def delete_task(task_id: int) -> str:
    """按照任务 ID 删除一个具体任务。
    Args:
        task_id: 要删除的真实任务 ID。
    Returns:
        删除成功标记及被删除的任务 ID。
    Usage:
        用户明确要求删除可唯一确定的单个任务时使用；应先查询确认 ID。
    Restrictions:
        这是破坏性操作；不得根据模糊描述批量删除，不得猜测 ID，范围不明确时先向用户确认。
    """
    await backend_gateway.delete_task(task_id)
    mark_data_changed("tasks")
    return _json({"deleted": True, "task_id": task_id})

@tool
@trace_tool
async def get_recurring_tasks() -> str:
    """查询当前用户的全部重复任务规则。
    Args:
        无。用户身份从当前请求上下文获取。
    Returns:
        重复任务规则列表，包含规则 ID、内容、起止日期、星期区间、时间、优先级、提醒和启用状态。
    Usage:
        用于展示重复任务，或在修改、删除重复规则前获得准确 rule_id 和完整现值。
    Restrictions:
        只查询当前用户的规则，不修改规则或已生成任务。
    """
    return _json(await backend_gateway.get_recurring_tasks(_email()))

def _rule(content, start_date, weekdays, end_date, active, priority, start_time, end_time,
          estimated_minutes, reminder_enabled, reminder_channel, reminder_minutes_before):
    return {"content": content, "startDate": start_date, "endDate": end_date, "weekdays": weekdays,
        "active": active, "priority": priority, "startTime": start_time, "endTime": end_time,
        "estimatedMinutes": estimated_minutes, "reminderEnabled": reminder_enabled,
        "reminderChannel": reminder_channel, "reminderMinutesBefore": reminder_minutes_before,
        "user": {"id": _user_id()}}

@tool
@trace_tool
async def create_recurring_task(content: str, start_date: str, weekdays: str, end_date: str | None = None,
        active: bool = True, priority: str = "MEDIUM", start_time: str | None = None, end_time: str | None = None,
        estimated_minutes: int | None = None, reminder_enabled: bool = False, reminder_channel: str = "EMAIL",
        reminder_minutes_before: int = 30) -> str:
    """创建一条按星期重复的任务规则，并由后端生成对应任务实例。

    Args:
        content: 重复任务内容。
        start_date: 规则开始日期，格式为 YYYY-MM-DD。
        weekdays: ISO 星期数字的逗号分隔字符串，1=周一、7=周日，例如周一到周四为 1,2,3,4。
        end_date: 规则结束日期；可为空，表示不设置固定结束日。
        active: 是否立即启用规则，默认 true。
        priority: 优先级，可用 LOW、MEDIUM、HIGH、URGENT。
        start_time: 每次任务的开始时间；可为空。
        end_time: 每次任务的结束时间；可为空。
        estimated_minutes: 每次任务预计用时，单位为分钟；可为空。
        reminder_enabled: 是否启用提醒。
        reminder_channel: 提醒渠道，EMAIL 或 SMS。
        reminder_minutes_before: 提前提醒分钟数。

    Returns:
        创建后的完整重复任务规则及真实规则 ID。

    Usage:
        用户明确要求建立周期性任务时使用，而不是为每天分别调用 create_task。

    Restrictions:
        weekdays 必须使用 1 到 7；日期和执行区间应来自用户要求，不得擅自扩大重复范围。
    """
    result = await backend_gateway.create_recurring_task(_rule(content, start_date, weekdays, end_date, active,
        priority, start_time, end_time, estimated_minutes, reminder_enabled, reminder_channel, reminder_minutes_before))
    mark_data_changed("recurring_tasks", start_date, end_date)
    mark_data_changed("tasks", start_date, end_date)
    return _json(result)
@tool
@trace_tool
async def update_recurring_task(rule_id: int, content: str, start_date: str, weekdays: str,
        end_date: str | None = None, active: bool = True, priority: str = "MEDIUM", start_time: str | None = None,
        end_time: str | None = None, estimated_minutes: int | None = None, reminder_enabled: bool = False,
        reminder_channel: str = "EMAIL", reminder_minutes_before: int = 30) -> str:
    """完整更新一条重复任务规则，并让后端重新生成未来任务实例。

    Args:
        rule_id: 要修改的真实重复规则 ID。
        content: 更新后的完整任务内容。
        start_date: 更新后的开始日期，格式为 YYYY-MM-DD。
        weekdays: ISO 星期数字的逗号分隔字符串，1=周一、7=周日。
        end_date: 更新后的结束日期；可为空。
        active: 是否启用规则。
        priority: 更新后的优先级。
        start_time: 更新后的开始时间；可为空。
        end_time: 更新后的结束时间；可为空。
        estimated_minutes: 更新后的预计分钟数；可为空。
        reminder_enabled: 是否启用提醒。
        reminder_channel: 提醒渠道，EMAIL 或 SMS。
        reminder_minutes_before: 提前提醒分钟数。

    Returns:
        更新后的完整重复任务规则。

    Usage:
        先调用 get_recurring_tasks 获取 rule_id 和全部现值，再修改用户指定字段并保留其他字段。

    Restrictions:
        更新可能影响未来任务实例；不得猜测 rule_id，也不得用默认值覆盖未要求修改的现有字段。
    """
    result = await backend_gateway.update_recurring_task(rule_id, _rule(content, start_date, weekdays, end_date,
        active, priority, start_time, end_time, estimated_minutes, reminder_enabled, reminder_channel, reminder_minutes_before))
    mark_data_changed("recurring_tasks", start_date, end_date)
    mark_data_changed("tasks", start_date, end_date)
    return _json(result)

@tool
@trace_tool
async def delete_recurring_task(rule_id: int) -> str:
    """删除一条重复任务规则及其未来任务实例。

    Args:
        rule_id: 要删除的真实重复规则 ID。

    Returns:
        删除成功标记及被删除的规则 ID。

    Usage:
        用户明确要求删除可唯一确定的重复规则时使用；应先调用 get_recurring_tasks 查询确认。

    Restrictions:
        这是影响多个未来实例的破坏性操作；范围不明确时必须先确认，不得猜测 rule_id。
    """
    await backend_gateway.delete_recurring_task(rule_id)
    mark_data_changed("recurring_tasks")
    mark_data_changed("tasks")
    return _json({"deleted": True, "rule_id": rule_id})

@tool
@trace_tool
async def get_active_focus() -> str:
    """查询当前用户正在进行的专注会话。

    Args:
        无。用户身份从当前请求上下文获取。

    Returns:
        当前活动专注会话的完整信息；没有活动会话时返回空值。

    Usage:
        用户询问当前专注状态，或停止专注前查找真实 session_id 时使用。

    Restrictions:
        只查询，不开始或停止专注计时。
    """
    return _json(await backend_gateway.get_active_focus(_email()))

@tool
@trace_tool
async def get_focus_sessions(from_date: str, to_date: str) -> str:
    """查询当前用户在指定日期范围内的专注记录。

    Args:
        from_date: 起始日期，格式为 YYYY-MM-DD，包含当天。
        to_date: 结束日期，格式为 YYYY-MM-DD，包含当天。

    Returns:
        日期范围内的专注会话列表，包括时长、标题、备注及关联任务等信息。

    Usage:
        用于查看专注历史和复盘具体专注记录；聚合统计可使用 get_statistics。

    Restrictions:
        from_date 不应晚于 to_date；该工具只查询，不修改专注记录。
    """
    return _json(await backend_gateway.get_focus_sessions(_email(), from_date, to_date))

@tool
@trace_tool
async def start_focus(title: str | None = None, task_id: int | None = None) -> str:
    """为当前用户开始一次专注计时，可选关联已有任务。

    Args:
        title: 本次专注标题；可为空。
        task_id: 要关联的真实任务 ID；不关联任务时可为空。

    Returns:
        新建的活动专注会话，包括真实 session_id 和开始时间。

    Usage:
        用户明确要求开始专注时使用；需要关联任务但不知道 ID 时先查询任务。

    Restrictions:
        不得猜测 task_id；如果已有活动专注会话，应根据后端结果提示用户，不重复创建。
    """
    return _json(await backend_gateway.start_focus(_user_id(), task_id, title))

@tool
@trace_tool
async def stop_focus(session_id: int, note: str | None = None) -> str:
    """结束指定的活动专注会话，并由后端累计关联任务的实际用时。

    Args:
        session_id: 要结束的真实专注会话 ID。
        note: 本次专注备注；可为空。

    Returns:
        已结束的完整专注会话，包括结束时间和实际时长。

    Usage:
        用户要求结束当前专注时使用；不知道 session_id 时先调用 get_active_focus。

    Restrictions:
        不得猜测 session_id，不应重复结束已经结束的会话。
    """
    return _json(await backend_gateway.stop_focus(session_id, note))

@tool
@trace_tool
async def delete_focus(session_id: int) -> str:
    """按照会话 ID 删除一条专注记录。

    Args:
        session_id: 要删除的真实专注会话 ID。

    Returns:
        删除成功标记及被删除的会话 ID。

    Usage:
        用户明确要求删除可唯一确定的专注历史记录时使用。

    Restrictions:
        这是破坏性操作；应先查询确认记录，不得根据模糊描述批量删除或猜测 session_id。
    """
    await backend_gateway.delete_focus(session_id)
    return _json({"deleted": True, "session_id": session_id})

@tool
@trace_tool
async def get_statistics(from_date: str, to_date: str) -> str:
    """查询当前用户在指定日期范围内的任务和专注聚合统计。

    Args:
        from_date: 统计起始日期，格式为 YYYY-MM-DD，包含当天。
        to_date: 统计结束日期，格式为 YYYY-MM-DD，包含当天。

    Returns:
        后端计算的统计对象，包括任务总数、完成数、完成率、逾期数、预计与实际分钟数、专注时长和状态分布等。

    Usage:
        用户询问完成率、逾期、任务状态分布、优先级分布或专注汇总时使用；需要任务明细时配合 get_tasks 或 get_week_tasks。

    Restrictions:
        from_date 不应晚于 to_date；应以工具返回的后端统计为准，不自行编造指标。
    """
    return _json(await backend_gateway.get_statistics(_email(), from_date, to_date))

PLAN_TOOLS = [get_tasks, get_week_tasks, analyze_task, create_task, update_task, set_task_status,
              complete_subtask, delete_task, get_recurring_tasks, create_recurring_task,
              update_recurring_task, delete_recurring_task, get_active_focus, get_focus_sessions,
              start_focus, stop_focus, delete_focus, get_statistics]

async def run_tool_by_name(name: str, args: dict) -> str:
    selected = {item.name: item for item in PLAN_TOOLS}.get(name)
    return str(await selected.ainvoke(args)) if selected else f"未知工具: {name}"

def today_iso() -> str: return date.today().isoformat()
def monday_of_week(value: date | None = None) -> str:
    current = value or date.today()
    return (current - timedelta(days=current.weekday())).isoformat()
def format_tool_result(name: str, payload: dict) -> str: return _json({"tool": name, "args": payload})

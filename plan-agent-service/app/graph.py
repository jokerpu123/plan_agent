import asyncio
import json
import logging
import re
from datetime import date, timedelta
from time import perf_counter
from typing import Literal, TypedDict
from langchain_core.exceptions import OutputParserException
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command, interrupt
from pydantic import BaseModel, Field
from app.config import settings
from app.backend_gateway import backend_gateway
from app.observability import bind_trace, log_event, reset_trace
from app.tools import (PLAN_TOOLS, clear_request_context, consume_data_changes,
                       mark_data_changed, set_request_context)

class RouteDecision(BaseModel):
    mode: Literal["react", "plan"]
    reason: str = ""

class PlanTask(BaseModel):
    content: str
    task_date: str
    plan_type: Literal["daily", "weekly"] = "daily"
    priority: Literal["LOW", "MEDIUM", "HIGH", "URGENT"] = "MEDIUM"
    start_time: str | None = None
    end_time: str | None = None
    deadline: str | None = None
    estimated_minutes: int | None = None

class PlanOutput(BaseModel):
    planning_mode: Literal["daily_schedule", "weekly_goals"] = "daily_schedule"
    summary: str = ""
    tasks: list[PlanTask] = Field(max_length=50)

class AgentState(TypedDict, total=False):
    message: str
    email: str
    user_id: int
    history: list[dict]
    conversation_summary: str
    pending_action: dict
    route: str
    route_reason: str
    existing_tasks: list[dict]
    plan: dict
    analyses: list[dict]
    revision_count: int
    feedback: str
    response: str

ROUTER_PROMPT = """你是计划安排系统的意图路由器，需要判断用户请求应交给哪种 Agent。在任务到来的使用你需要判断任务是否能直接使用提供的tools解决
react：适用于问答、查询，以及通过组合若干原子工具即可完成的具体操作。
plan：适用于需要把目标拆成多个相关任务，并进行跨天统筹、整体排期、冲突协调或批量规划的请求。
你会收到最近对话。当前消息若是对上一轮澄清问题的简短确认、修改意见、对象选择或信息补充，必须结合上一轮语境判断，不能把它当成独立的新目标。
若上一轮是在澄清一个原子查询或原子写操作，后续回答仍应路由到 react；只有用户确实要求拆解并统筹多个任务时才路由到 plan。
请根据完成请求所需的推理和执行规模判断，不要使用关键词机械匹配。
输出必须符合给定的 JSON Schema，reason 使用简短中文说明判断依据。"""

REACT_PROMPT = """你是计划安排系统的操作助手。今天是 {today}。
你可以自主组合原子工具完成用户请求，并以工具返回的后端真实数据为准。
修改或删除前应先查询以获得准确 ID，不得编造记录。
用户明确要求的单项写操作可以执行；含糊的破坏性操作必须先向用户澄清。
请使用简洁的中文回答。"""

PLANNER_PROMPT = """你是计划安排系统的 Plan-and-Execute 规划器。今天是 {today}。
请把用户目标拆解成可执行的多项任务，并结合已有任务和冲突检测反馈进行安排。
首先判断用户要的是 daily_schedule（具体每日排期）还是 weekly_goals（每周规划栏目中的周目标）。
如果用户明确说“每周规划”“周目标”“添加到下一周/本周的每周规划”，必须使用 weekly_goals：
1. 保留用户明确列出的顶层目标，一项目标对应一个任务，不得擅自拆成每日步骤。
2. 每个任务的 plan_type 必须为 weekly，task_date 必须是目标自然周的周一。
3. start_time、end_time、deadline 和 estimated_minutes 保持为空，除非用户明确要求这些字段。
4. 只有用户明确要求分配到每天、制定日程或具体排期时，才使用 daily_schedule 并拆解任务。
existing_tasks 只用于避让时间冲突、评估负载和提供排期参考。
绝对不要把 existing_tasks 中的已有任务复制、改写或原样放进 PlanOutput。
PlanOutput.tasks 只能包含本次用户在当前对话中明确要求新建的任务。
如果用户只是回答上一轮的澄清问题，必须结合最近对话恢复其完整意图，不得把这句简短回答扩展成无关计划。
任务必须使用明确日期，避免时间重叠和重复任务，任务之间保留合理休息时间，并控制每日负载。
你只负责生成或修订计划，不执行任何写操作。
输出必须严格符合给定的 JSON Schema。"""

_graph = None
_checkpointer = None
_graph_lock = asyncio.Lock()

def _llm() -> ChatOpenAI:
    return ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key,
                      base_url=settings.openai_api_base or None, temperature=0.2)

def _structured(schema):
    return _llm().with_structured_output(schema, method="json_mode")


async def _structured_invoke(schema, messages: list, max_retries: int = 2):
    """调用结构化模型；JSON 解析失败时携带纠错指令最多重试两次。"""
    current_messages = list(messages)
    for attempt in range(max_retries + 1):
        try:
            return await _structured(schema).ainvoke(current_messages)
        except OutputParserException as exc:
            log_event(
                "structured_output.retry",
                level=logging.WARNING,
                schema=schema.__name__,
                attempt=attempt + 1,
                max_attempts=max_retries + 1,
                error=str(exc),
            )
            if attempt >= max_retries:
                raise
            current_messages.append(SystemMessage(
                content="上一输出不是有效JSON，只返回JSON对象。不要输出解释、Markdown或代码块。"
            ))


def _history_messages(history: list[dict], limit: int = 10) -> list:
    messages = []
    for item in history[-limit:]:
        kind = HumanMessage if item.get("role") == "user" else AIMessage
        messages.append(kind(content=item.get("content", "")))
    return messages


def _memory_context(state: AgentState) -> str:
    return (f"会话滚动摘要：{state.get('conversation_summary') or '无'}\n"
            f"待处理动作：{state.get('pending_action') or '无'}")

async def route_node(state: AgentState) -> dict:
    started = perf_counter()
    prompt = ROUTER_PROMPT + "\nJSON Schema: " + json.dumps(RouteDecision.model_json_schema())
    messages = [SystemMessage(content=prompt + "\n" + _memory_context(state)),
        # Few-shot 使用独立的 Human/AI 消息模拟真实分类过程，
        # 比把示例混在系统规则中更容易让模型区分“示例输入”和“示例答案”。
        HumanMessage(content="查询本周任务和完成情况。"),
        AIMessage(content='{"mode":"react","reason":"该请求可以通过原子查询工具完成。"}'),
        HumanMessage(content="结合已有任务，制定未来两周的考试复习计划。"),
        AIMessage(content='{"mode":"plan","reason":"该请求需要跨天拆解目标并协调多个任务。"}'),
    ]
    messages.extend(_history_messages(state.get("history", [])))
    messages.append(HumanMessage(content=state["message"]))
    decision = await _structured_invoke(RouteDecision, messages)
    log_event("router.decided", mode=decision.mode, reason=decision.reason,
              duration_ms=round((perf_counter() - started) * 1000, 1))
    return {"route": decision.mode, "route_reason": decision.reason}

def route_edge(state: AgentState) -> str:
    return state["route"]

async def react_node(state: AgentState) -> dict:
    started = perf_counter()
    log_event("react.started", history_count=min(len(state.get("history", [])), 10))
    agent = create_react_agent(
        _llm(), PLAN_TOOLS,
        prompt=REACT_PROMPT.format(today=date.today().isoformat()) + "\n" + _memory_context(state),
    )
    messages = _history_messages(state.get("history", []))
    messages.append(HumanMessage(content=state["message"]))
    result = await agent.ainvoke({"messages": messages})
    response = str(result["messages"][-1].content)
    log_event("react.completed", duration_ms=round((perf_counter() - started) * 1000, 1),
              response_length=len(response))
    return {"response": response}

async def load_context_node(state: AgentState) -> dict:
    started = perf_counter()
    tasks = []
    for offset in range(30):
        day = (date.today() + timedelta(days=offset)).isoformat()
        tasks.extend(await backend_gateway.get_tasks(state["email"], day))
    current_monday = date.today() - timedelta(days=date.today().weekday())
    for week_offset in range(6):
        week_start = (current_monday + timedelta(weeks=week_offset)).isoformat()
        tasks.extend(await backend_gateway.get_tasks(state["email"], week_start, "weekly"))
    log_event("plan.context_loaded", days=30, weekly_windows=6, task_count=len(tasks),
              duration_ms=round((perf_counter() - started) * 1000, 1))
    return {"existing_tasks": tasks, "revision_count": 0, "analyses": []}


async def planner_node(state: AgentState) -> dict:
    started = perf_counter()
    log_event("plan.planner_started", revision=state.get("revision_count", 0))
    prompt = (PLANNER_PROMPT.format(today=date.today().isoformat()) + "\nJSON Schema: "
              + json.dumps(PlanOutput.model_json_schema()))
    recent_history = state.get("history", [])[-10:]
    user_input = (f"{_memory_context(state)}\n最近对话：{recent_history}\n当前用户消息：{state['message']}\n"
                  f"existing_tasks（仅作约束，禁止输出）：{state.get('existing_tasks', [])}\n"
                  f"上一版计划：{state.get('plan', {})}\n检测或用户反馈："
                  f"{state.get('feedback') or state.get('analyses', [])}")
    result = await _structured_invoke(PlanOutput, [
        SystemMessage(content=prompt), HumanMessage(content=user_input)
    ])
    plan = result.model_dump()
    log_event("plan.planner_completed", task_count=len(plan["tasks"]),
              duration_ms=round((perf_counter() - started) * 1000, 1))
    return {"plan": plan, "feedback": ""}


async def analyze_node(state: AgentState) -> dict:
    started = perf_counter()
    results = []
    for task in state["plan"]["tasks"]:
        if task.get("plan_type") == "weekly":
            # 周目标没有具体时段，不适用每日任务的时间重叠和容量检测。
            results.append({"reasonable": True, "warnings": []})
        else:
            results.append(await backend_gateway.analyze_task({**task, "user_id": state["user_id"]}))
    warning_count = sum(len(item.get("warnings", [])) for item in results)
    log_event("plan.analysis_completed", task_count=len(results), warning_count=warning_count,
              duration_ms=round((perf_counter() - started) * 1000, 1))
    return {"analyses": results}


def analysis_edge(state: AgentState) -> str:
    warnings = [warning for result in state["analyses"] for warning in result.get("warnings", [])]
    if warnings and state.get("revision_count", 0) < settings.plan_max_revisions:
        return "revise"
    return "approval"


def auto_revise_node(state: AgentState) -> dict:
    log_event("plan.auto_revision", revision=state.get("revision_count", 0) + 1)
    return {"revision_count": state.get("revision_count", 0) + 1,
            "feedback": f"请消除以下任务合理性检测警告：{state['analyses']}"}


def _preview(state: AgentState) -> str:
    lines = ["已生成计划预览（尚未写入）：", "",
             state["plan"].get("summary", ""), ""]
    for index, task in enumerate(state["plan"]["tasks"], 1):
        if task.get("plan_type") == "weekly":
            lines.append(f"{index}. {task['task_date']} | 每周规划 | {task['content']}")
        else:
            period = task.get("start_time") or "未定时间"
            if task.get("end_time"):
                period += "-" + task["end_time"]
            lines.append(f"{index}. {task['task_date']} {period} | {task['content']} | {task.get('estimated_minutes') or 0} min")
        for warning in state.get("analyses", [])[index - 1].get("warnings", []):
            lines.append(f"   ! {warning}")
    lines.extend(["", "请回复确认、修改意见或取消。确认后才会批量写入任务。"])
    return "\n".join(lines)


def _approval_action(answer: str) -> Literal["approve", "revise", "cancel"]:
    normalized = re.sub(r"[\s，。！？、,.!?]", "", answer.strip()).lower()
    approve_replies = {"确认", "确认执行", "同意", "同意执行", "批准", "按此执行", "approve"}
    cancel_replies = {"取消", "取消计划", "不执行", "拒绝", "cancel"}
    if normalized in approve_replies:
        return "approve"
    if normalized in cancel_replies:
        return "cancel"
    return "revise"


async def approval_node(state: AgentState) -> Command[Literal["execute", "planner", "cancel"]]:
    log_event("plan.approval_requested", task_count=len(state["plan"]["tasks"]))
    answer = interrupt({"type": "plan_approval", "preview": _preview(state)})
    raw_answer = str(answer).strip()
    # 审批属于高风险写操作：只有明确且完整匹配的短确认词才允许执行。
    # 任何计划内容、补充说明或新请求都视为修改意见，必须重新生成预览后再次确认。
    action = _approval_action(raw_answer)
    if action == "approve":
        log_event("plan.approval_decided", action="approve", feedback="")
        return Command(goto="execute")
    if action == "cancel":
        log_event("plan.approval_decided", action="cancel", feedback="")
        return Command(goto="cancel")
    log_event("plan.approval_decided", action="revise", feedback=raw_answer)
    return Command(update={"feedback": raw_answer,
                           "revision_count": state.get("revision_count", 0) + 1}, goto="planner")


async def execute_node(state: AgentState) -> dict:
    started = perf_counter()
    log_event("plan.execution_started", task_count=len(state["plan"]["tasks"]))
    created = []
    try:
        for task in state["plan"]["tasks"]:
            created.append(await backend_gateway.create_task(
                state["user_id"], task["content"], task["task_date"],
                plan_type=task.get("plan_type", "daily"),
                priority=task.get("priority", "MEDIUM"), start_time=task.get("start_time"),
                end_time=task.get("end_time"), deadline=task.get("deadline"),
                estimated_minutes=task.get("estimated_minutes")))
    except Exception as exc:
        log_event("plan.execution_rollback", level=logging.ERROR, created_count=len(created),
                  error_type=type(exc).__name__, error=str(exc))
        for task in created:
            try:
                await backend_gateway.delete_task(task["id"])
            except Exception:
                pass
        raise
    log_event("plan.execution_completed", created_count=len(created),
              duration_ms=round((perf_counter() - started) * 1000, 1))
    for task in state["plan"]["tasks"]:
        mark_data_changed("tasks", task.get("task_date"))
    return {"response": f"计划执行完成，共创建 {len(created)} 项任务。"}


def cancel_node(state: AgentState) -> dict:
    log_event("plan.cancelled")
    return {"response": "已取消该计划，没有创建任务。"}


def build_graph(checkpointer):
    builder = StateGraph(AgentState)
    for name, node in (("route", route_node), ("react", react_node), ("load_context", load_context_node),
                       ("planner", planner_node), ("analyze", analyze_node), ("auto_revise", auto_revise_node),
                       ("approval", approval_node), ("execute", execute_node), ("cancel", cancel_node)):
        builder.add_node(name, node)
    builder.add_edge(START, "route")
    builder.add_conditional_edges("route", route_edge, {"react": "react", "plan": "load_context"})
    builder.add_edge("react", END)
    builder.add_edge("load_context", "planner")
    builder.add_edge("planner", "analyze")
    builder.add_conditional_edges("analyze", analysis_edge, {"revise": "auto_revise", "approval": "approval"})
    builder.add_edge("auto_revise", "planner")
    builder.add_edge("execute", END)
    builder.add_edge("cancel", END)
    return builder.compile(checkpointer=checkpointer)


async def get_graph():
    global _graph, _checkpointer
    if _graph is not None:
        return _graph
    async with _graph_lock:
        if _graph is None:
            log_event("graph.initializing", redis_url=settings.redis_url)
            _checkpointer = AsyncRedisSaver(redis_url=settings.redis_url,
                ttl={"default_ttl": 30, "refresh_on_read": True})
            await _checkpointer.setup()
            _graph = build_graph(_checkpointer)
            log_event("graph.initialized")
    return _graph


async def run_agent(message: str, email: str, user_id: int, history: list[dict],
                    conversation_id: str, conversation_summary: str = "",
                    pending_action: dict | None = None):
    _, trace_token = bind_trace(user_id)
    started = perf_counter()
    request_token = None
    try:
        log_event("request.received", message=message, history_count=len(history))
        graph = await get_graph()
        config = {"configurable": {"thread_id": f"plan-conversation-{conversation_id}"}}
        request_token = set_request_context(email, user_id)
        snapshot = await graph.aget_state(config)
        # 只有人工审批 interrupt 才允许把新消息当作 resume 输入。
        # 普通节点异常遗留的 pending 状态不能污染用户的下一次请求。
        awaiting_approval = "approval" in snapshot.next
        if awaiting_approval:
            log_event("graph.resuming", pending_nodes=list(snapshot.next))
            result = await graph.ainvoke(Command(resume=message), config=config)
        else:
            if snapshot.next:
                log_event("graph.stale_state_ignored", pending_nodes=list(snapshot.next))
            log_event("graph.starting")
            result = await graph.ainvoke({"message": message, "email": email, "user_id": user_id,
                "history": history, "conversation_summary": conversation_summary,
                "pending_action": pending_action or {}, "response": "", "plan": {},
                "analyses": [], "feedback": ""}, config=config)
        if "__interrupt__" in result:
            log_event("request.interrupted", duration_ms=round((perf_counter() - started) * 1000, 1))
            yield result["__interrupt__"][0].value["preview"]
        else:
            log_event("request.completed", route=result.get("route"),
                      duration_ms=round((perf_counter() - started) * 1000, 1))
            yield result.get("response", "完成。")
        for event in consume_data_changes():
            log_event("sse.business_event", event_type=event["type"], resource=event["resource"],
                      dates=event["dates"])
            yield event
    except Exception as exc:
        log_event("request.failed", level=logging.ERROR,
                  duration_ms=round((perf_counter() - started) * 1000, 1),
                  error_type=type(exc).__name__, error=str(exc))
        raise
    finally:
        if request_token is not None:
            clear_request_context(request_token)
        reset_trace(trace_token)

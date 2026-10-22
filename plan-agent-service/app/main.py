import json
from typing import AsyncIterator
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from redis.asyncio import Redis

from app.config import settings
from app.observability import log_event
from app.conversation_store import conversation_store

from app.graph import run_agent

app = FastAPI(title="Plan Agent Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8082",
        "http://localhost:8080",
        "http://localhost:6888",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    email: str = Field(..., min_length=1)
    user_id: int = Field(..., ge=1)
    history: list[ChatMessage] = Field(default_factory=list)
    conversation_id: str | None = None


class ConversationCreateRequest(BaseModel):
    user_id: int = Field(..., ge=1)
    title: str = "新对话"


def _sse_pack(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


async def _chat_stream(body: ChatRequest) -> AsyncIterator[str]:
    try:
        conversation = (await conversation_store.get(body.conversation_id, body.user_id)
                        if body.conversation_id else None)
        if not conversation:
            conversation = await conversation_store.create(body.user_id)
        conversation_id = conversation["id"]
        context = await conversation_store.select_context(conversation_id, body.user_id)
        # 兼容旧前端传入的 history；有会话记忆后以服务端存储为准。
        history = [{"role": item["role"], "content": item["content"]}
                   for item in context["messages"]]
        await conversation_store.append_message(conversation_id, body.user_id, "user", body.message)
        yield _sse_pack({"type": "conversation", "conversation_id": conversation_id})
        response_parts = []
        async for event in run_agent(body.message, body.email, body.user_id, history, conversation_id,
                                     context["summary"], context["pending_action"]):
            if isinstance(event, dict):
                yield _sse_pack(event)
            elif event:
                response_parts.append(event)
                yield _sse_pack({"type": "token", "content": event})
        assistant_response = "".join(response_parts)
        if assistant_response:
            await conversation_store.append_message(
                conversation_id, body.user_id, "assistant", assistant_response)
            asks_clarification = any(marker in assistant_response for marker in
                                     ("请确认", "请选择", "请问", "是否", "还是改"))
            pending = ({"status": "WAITING_CLARIFICATION", "originating_request": body.message,
                        "assistant_question": assistant_response, "created_at": "now"}
                       if asks_clarification else None)
            await conversation_store.set_pending_action(conversation_id, body.user_id, pending)
        yield _sse_pack({"type": "done"})
    except Exception as exc:
        message = str(exc).strip() or exc.__class__.__name__
        log_event("sse.error_sent", error_type=type(exc).__name__)
        yield _sse_pack({"type": "error", "content": message})
        yield _sse_pack({"type": "done"})


@app.get("/health")
async def health() -> dict:
    redis_ok = False
    try:
        client = Redis.from_url(settings.redis_url)
        redis_ok = bool(await client.ping())
        await client.aclose()
    except Exception:
        pass
    return {"status": "ok" if redis_ok else "degraded", "service": "plan-agent-service",
            "dependencies": {"redis": "ok" if redis_ok else "unavailable"}}


@app.post("/api/ai/chat")
async def chat(body: ChatRequest) -> StreamingResponse:
    if not body.message.strip():
        raise HTTPException(status_code=400, detail="message 不能为空")
    return StreamingResponse(
        _chat_stream(body),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/ai/conversations")
async def list_conversations(user_id: int) -> list[dict]:
    return await conversation_store.list(user_id)


@app.post("/api/ai/conversations")
async def create_conversation(body: ConversationCreateRequest) -> dict:
    return await conversation_store.create(body.user_id, body.title)


@app.get("/api/ai/conversations/{conversation_id}")
async def get_conversation(conversation_id: str, user_id: int) -> dict:
    value = await conversation_store.get(conversation_id, user_id)
    if not value:
        raise HTTPException(status_code=404, detail="会话不存在")
    return value


@app.delete("/api/ai/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, user_id: int) -> dict:
    if not await conversation_store.delete(conversation_id, user_id):
        raise HTTPException(status_code=404, detail="会话不存在")
    return {"deleted": True, "conversation_id": conversation_id}

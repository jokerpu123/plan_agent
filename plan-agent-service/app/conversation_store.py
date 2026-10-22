import json
from datetime import datetime, timezone
from uuid import uuid4

from redis.asyncio import Redis

from app.config import settings


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ConversationStore:
    """Redis-backed conversation, session memory and pending-action repository."""

    ttl_seconds = 90 * 24 * 60 * 60

    def __init__(self):
        self.redis = Redis.from_url(settings.redis_url, decode_responses=True)

    def _key(self, conversation_id: str) -> str:
        return f"plan:conversation:{conversation_id}"

    def _index(self, user_id: int) -> str:
        return f"plan:user:{user_id}:conversations"

    async def create(self, user_id: int, title: str = "新对话") -> dict:
        conversation_id = uuid4().hex
        now = _now()
        value = {
            "id": conversation_id,
            "user_id": user_id,
            "title": title.strip()[:60] or "新对话",
            "created_at": now,
            "updated_at": now,
            "summary": "",
            "pending_action": None,
            "messages": [],
        }
        await self._save(value)
        return value

    async def _save(self, value: dict) -> None:
        key = self._key(value["id"])
        timestamp = datetime.fromisoformat(value["updated_at"]).timestamp()
        pipe = self.redis.pipeline()
        pipe.set(key, json.dumps(value, ensure_ascii=False), ex=self.ttl_seconds)
        pipe.zadd(self._index(int(value["user_id"])), {value["id"]: timestamp})
        pipe.expire(self._index(int(value["user_id"])), self.ttl_seconds)
        await pipe.execute()

    async def get(self, conversation_id: str, user_id: int) -> dict | None:
        raw = await self.redis.get(self._key(conversation_id))
        if not raw:
            return None
        value = json.loads(raw)
        return value if int(value["user_id"]) == user_id else None

    async def list(self, user_id: int) -> list[dict]:
        ids = await self.redis.zrevrange(self._index(user_id), 0, 49)
        values = await self.redis.mget([self._key(item) for item in ids]) if ids else []
        return [
            {key: value[key] for key in ("id", "title", "created_at", "updated_at")}
            for raw in values if raw and (value := json.loads(raw))
        ]

    async def delete(self, conversation_id: str, user_id: int) -> bool:
        if not await self.get(conversation_id, user_id):
            return False
        pipe = self.redis.pipeline()
        pipe.delete(self._key(conversation_id))
        pipe.zrem(self._index(user_id), conversation_id)
        await pipe.execute()
        return True

    async def append_message(self, conversation_id: str, user_id: int, role: str, content: str) -> dict:
        value = await self.get(conversation_id, user_id)
        if not value:
            raise KeyError("会话不存在")
        value["messages"].append({"role": role, "content": content, "created_at": _now()})
        value["updated_at"] = _now()
        if value["title"] == "新对话" and role == "user":
            value["title"] = content.strip().replace("\n", " ")[:24] or "新对话"
        await self._compress(value)
        await self._save(value)
        return value

    async def set_pending_action(self, conversation_id: str, user_id: int, action: dict | None) -> None:
        value = await self.get(conversation_id, user_id)
        if not value:
            return
        value["pending_action"] = action
        value["updated_at"] = _now()
        await self._save(value)

    async def select_context(self, conversation_id: str, user_id: int, limit: int = 12) -> dict:
        value = await self.get(conversation_id, user_id)
        if not value:
            raise KeyError("会话不存在")
        return {
            "summary": value.get("summary", ""),
            "pending_action": value.get("pending_action"),
            "messages": value.get("messages", [])[-limit:],
        }

    async def _compress(self, value: dict) -> None:
        """Keep a sliding window and roll older dialogue into a compact traceable summary."""
        messages = value["messages"]
        if len(messages) <= 24:
            return
        archived, value["messages"] = messages[:-16], messages[-16:]
        fragments = [f"{item['role']}: {item['content'][:240]}" for item in archived]
        previous = value.get("summary", "")
        value["summary"] = (previous + "\n" + "\n".join(fragments)).strip()[-6000:]


conversation_store = ConversationStore()

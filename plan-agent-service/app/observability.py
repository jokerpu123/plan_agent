import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime, timezone
from functools import wraps
from time import perf_counter
from typing import Any, Awaitable, Callable
from uuid import uuid4


_trace_context: ContextVar[dict[str, Any]] = ContextVar("trace_context", default={})
_SENSITIVE_KEYS = {"access_key", "accesskey", "api_key", "apikey", "authorization",
                   "email", "password", "secret", "token"}
_MAX_TEXT = 240

# Windows 后台重定向时默认可能使用系统代码页，显式固定为 UTF-8。
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "time": datetime.now(timezone.utc).astimezone().isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "event": getattr(record, "event", "log"),
            **_trace_context.get(),
            **getattr(record, "fields", {}),
        }
        if record.getMessage():
            payload["message"] = record.getMessage()
        return json.dumps(payload, ensure_ascii=False, default=str, separators=(",", ":"))


logger = logging.getLogger("plan_agent")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_JsonFormatter())
    logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False


def bind_trace(user_id: int) -> tuple[str, object]:
    request_id = uuid4().hex[:12]
    token = _trace_context.set({"request_id": request_id, "user_id": user_id})
    return request_id, token


def reset_trace(token: object) -> None:
    _trace_context.reset(token)


def _redact(value: Any, key: str = "") -> Any:
    normalized = key.lower().replace("-", "_")
    if any(part in normalized for part in _SENSITIVE_KEYS):
        return "***"
    if isinstance(value, dict):
        return {str(k): _redact(v, str(k)) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_redact(item) for item in value[:20]]
    if isinstance(value, str):
        return value if len(value) <= _MAX_TEXT else value[:_MAX_TEXT] + "…"
    return value


def log_event(event: str, level: int = logging.INFO, **fields: Any) -> None:
    logger.log(level, "", extra={"event": event, "fields": _redact(fields)})


def summarize_result(value: Any) -> dict[str, Any]:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (TypeError, json.JSONDecodeError):
            return {"result_type": "text", "result_length": len(value)}
    if isinstance(value, list):
        return {"result_type": "list", "result_count": len(value)}
    if isinstance(value, dict):
        return {"result_type": "object", "result_keys": list(value)[:12]}
    return {"result_type": type(value).__name__}


def trace_tool(function: Callable[..., Awaitable[Any]]):
    @wraps(function)
    async def wrapped(*args, **kwargs):
        started = perf_counter()
        tool_call_id = uuid4().hex[:10]
        log_event("tool.started", tool=function.__name__, tool_call_id=tool_call_id,
                  arguments=kwargs)
        try:
            result = await function(*args, **kwargs)
            log_event("tool.completed", tool=function.__name__, tool_call_id=tool_call_id,
                      duration_ms=round((perf_counter() - started) * 1000, 1),
                      **summarize_result(result))
            return result
        except Exception as exc:
            log_event("tool.failed", level=logging.ERROR, tool=function.__name__,
                      tool_call_id=tool_call_id,
                      duration_ms=round((perf_counter() - started) * 1000, 1),
                      error_type=type(exc).__name__, error=str(exc))
            raise
    return wrapped

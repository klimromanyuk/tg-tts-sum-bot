"""Chat message buffer using deque for summarization."""

from collections import deque
from datetime import datetime
from config import MESSAGE_BUFFER_SIZE

_buffers: dict[int, deque] = {}

def get_buffer(chat_id: int) -> deque:
    if chat_id not in _buffers:
        _buffers[chat_id] = deque(maxlen=MESSAGE_BUFFER_SIZE)
    return _buffers[chat_id]

def add_message(chat_id: int, user_id: int, username: str, text: str, message_id: int, date: datetime = None):
    buf = get_buffer(chat_id)
    buf.append({
        "user_id": user_id,
        "username": username,
        "text": text,
        "message_id": message_id,
        "date": date or datetime.now(),
    })

def collect_up(chat_id: int, max_tokens: int, max_count: int = None) -> list[dict]:
    """Собрать от новых к старым, вернуть от старых к новым."""
    buf = get_buffer(chat_id)
    result = []
    tokens = 0
    for msg in reversed(buf):
        line = f"{msg['username']}: {msg['text']}"
        t = len(line) / 3.5
        if tokens + t > max_tokens:
            break
        result.append(msg)
        tokens += t
        if max_count and len(result) >= max_count:
            break
    result.reverse()
    return result

def collect_down(chat_id: int, from_message_id: int, max_tokens: int, max_count: int = None) -> list[dict]:
    """Собрать от указанного message_id к новым."""
    buf = get_buffer(chat_id)
    started = False
    result = []
    tokens = 0
    for msg in buf:
        if msg["message_id"] == from_message_id:
            started = True
        if not started:
            continue
        line = f"{msg['username']}: {msg['text']}"
        t = len(line) / 3.5
        if tokens + t > max_tokens:
            break
        result.append(msg)
        tokens += t
        if max_count and len(result) >= max_count:
            break
    return result
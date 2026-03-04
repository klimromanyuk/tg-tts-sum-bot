"""In-memory chat history for DM dialog mode."""

_histories: dict[int, list] = {}
_system_prompts: dict[int, str] = {}
_chat_mode: dict[int, bool] = {}

def get_history(user_id: int) -> list:
    return _histories.setdefault(user_id, [])

def add_message(user_id: int, role: str, content: str):
    h = get_history(user_id)
    h.append({"role": role, "content": content})

def clear(user_id: int):
    _histories[user_id] = []

def get_system(user_id: int) -> str:
    return _system_prompts.get(user_id, "")

def set_system(user_id: int, prompt: str):
    _system_prompts[user_id] = prompt

def is_chat_mode(user_id: int) -> bool:
    return _chat_mode.get(user_id, False)

def toggle_chat(user_id: int) -> bool:
    _chat_mode[user_id] = not _chat_mode.get(user_id, False)
    return _chat_mode[user_id]

def trim_history(user_id: int, max_tokens: int):
    h = get_history(user_id)
    total = 0
    keep = []
    for msg in reversed(h):
        t = len(msg["content"]) / 3.5
        if total + t > max_tokens:
            break
        keep.append(msg)
        total += t
    keep.reverse()
    _histories[user_id] = keep
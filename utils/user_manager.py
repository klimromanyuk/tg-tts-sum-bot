"""CRUD for users.json — per-user settings."""

import json, os
from config import USERS_FILE, DEFAULT_QWEN_VOICE, DEFAULT_EDGE_VOICE, DEFAULT_TTS_ENGINE, DEFAULT_AUTO_VOICE

_cache = None

def _load():
    global _cache
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            _cache = json.load(f)
    else:
        _cache = {}
    return _cache

def _save():
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(_cache, f, indent=2, ensure_ascii=False)

def get_user(user_id: int) -> dict:
    if _cache is None:
        _load()
    uid = str(user_id)
    if uid not in _cache:
        return None
    return _cache[uid]

def ensure_user(user_id: int, username: str = "") -> dict:
    if _cache is None:
        _load()
    uid = str(user_id)
    if uid not in _cache:
        _cache[uid] = {
            "username": username,
            "qwen_voice": DEFAULT_QWEN_VOICE,
            "edge_voice": DEFAULT_EDGE_VOICE,
            "tts_engine": DEFAULT_TTS_ENGINE,
            "auto_voice": DEFAULT_AUTO_VOICE,
        }
        _save()
    elif username and _cache[uid].get("username") != username:
        _cache[uid]["username"] = username
        _save()
    return _cache[uid]

def update_user(user_id: int, **kwargs):
    if _cache is None:
        _load()
    uid = str(user_id)
    if uid in _cache:
        _cache[uid].update(kwargs)
        _save()
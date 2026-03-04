"""CRUD for settings.json."""
import json, os
from config import SETTINGS_FILE, DEFAULT_SETTINGS, _DM_USERS_ENV

_cache = None

def _load():
    global _cache
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            _cache = json.load(f)
        for k, v in DEFAULT_SETTINGS.items():
            if k not in _cache:
                _cache[k] = v
        # Merge .env users into settings
        for uid in _DM_USERS_ENV:
            if uid not in _cache.get("allowed_dm_users", []):
                _cache.setdefault("allowed_dm_users", []).append(uid)
    else:
        _cache = dict(DEFAULT_SETTINGS)
        _save()
    return _cache

def _save():
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(_cache, f, indent=2, ensure_ascii=False)

def get() -> dict:
    if _cache is None:
        _load()
    return _cache

def set_value(key: str, value):
    s = get()
    s[key] = value
    _save()

def get_owner_id() -> int:
    s = get()
    dm = s.get("allowed_dm_users", [])
    return dm[0] if dm else 0

def is_dm_allowed(user_id: int) -> bool:
    return user_id in get().get("allowed_dm_users", [])

def add_dm_user(user_id: int) -> bool:
    s = get()
    if user_id in s["allowed_dm_users"]:
        return False
    s["allowed_dm_users"].append(user_id)
    _save()
    return True
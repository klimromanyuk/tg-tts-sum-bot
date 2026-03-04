import os
from config import VOICES_DIR, QWEN_VOICES, EDGE_VOICES

def get_qwen_prompt_path(voice_id: str) -> str:
    p = os.path.join(VOICES_DIR, voice_id, "prompt.qvp")
    if not os.path.exists(p):
        raise FileNotFoundError(f"Voice prompt not found: {p}")
    return p

def get_edge_voice_id(voice_key: str) -> str:
    v = EDGE_VOICES.get(voice_key)
    if v:
        return v["voice_id"]
    # maybe it's already a full voice_id
    for k, val in EDGE_VOICES.items():
        if val["voice_id"] == voice_key:
            return voice_key
    raise KeyError(f"Edge voice not found: {voice_key}")

def list_qwen_voices() -> dict:
    return QWEN_VOICES

def list_edge_voices() -> dict:
    return EDGE_VOICES

def voice_exists(voice_id: str, engine: str) -> bool:
    if engine == "qwen":
        return voice_id in QWEN_VOICES and os.path.exists(os.path.join(VOICES_DIR, voice_id, "prompt.qvp"))
    elif engine == "edge":
        return voice_id in EDGE_VOICES
    return False
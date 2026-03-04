import asyncio
from services.llm_service import unload_model as ollama_unload, get_loaded_models
from services.tts_service import load_model as tts_load, unload_model as tts_unload, is_loaded as tts_is_loaded

_state = "idle"  # "idle" | "ollama" | "tts"
_lock = asyncio.Lock()

def get_state() -> str:
    return _state

async def ensure_ollama():
    global _state
    async with _lock:
        if _state == "tts":
            tts_unload()
        _state = "ollama"

async def ensure_tts():
    global _state
    async with _lock:
        if _state == "ollama":
            models = await get_loaded_models()
            for m in models:
                await ollama_unload(m.get("name", m.get("model", "")))
        if not tts_is_loaded():
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, tts_load)
        _state = "tts"

async def unload_all():
    global _state
    async with _lock:
        if _state == "tts" or tts_is_loaded():
            tts_unload()
        models = await get_loaded_models()
        for m in models:
            await ollama_unload(m.get("name", m.get("model", "")))
        _state = "idle"
"""Ollama API client with streaming and think-block parsing."""
import aiohttp, asyncio, json, re, logging
from config import OLLAMA_URL

log = logging.getLogger(__name__)

async def generate_stream(model: str, prompt: str, system: str = "", options: dict = None,
                          think: bool = False, keep_alive: int = -1):
    """Yields (type, text). type: 'thinking' or 'answer'.
    Handles both Ollama's native 'thinking' field AND <think> tags in response."""
    url = f"{OLLAMA_URL}/api/generate"
    body = {"model": model, "prompt": prompt, "stream": True, "keep_alive": keep_alive}
    if system:
        body["system"] = system
    if options:
        body["options"] = options
    if think:
        body["think"] = True

    in_think = False
    tag_buf = ""

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=600)) as session:
        async with session.post(url, json=body) as resp:
            line_buf = ""
            async for raw in resp.content:
                if not raw:
                    continue
                line_buf += raw.decode("utf-8", errors="ignore")
                while "\n" in line_buf:
                    line, line_buf = line_buf.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if data.get("done"):
                        # Flush remaining tag_buf as answer
                        if tag_buf:
                            yield ("thinking" if in_think else "answer", tag_buf)
                            tag_buf = ""
                        return

                    # Ollama native thinking field
                    if "thinking" in data and data["thinking"]:
                        yield ("thinking", data["thinking"])
                        continue

                    token = data.get("response", "")
                    if not token:
                        continue

                    # Parse <think>...</think> from token stream
                    tag_buf += token
                    while tag_buf:
                        if not in_think:
                            idx = tag_buf.find("<think>")
                            if idx == -1:
                                # Check for partial tag at end
                                partial = _partial_tag_match(tag_buf, "<think>")
                                if partial > 0:
                                    emit = tag_buf[:-partial]
                                    if emit:
                                        yield ("answer", emit)
                                    tag_buf = tag_buf[-partial:]
                                    break
                                else:
                                    if tag_buf:
                                        yield ("answer", tag_buf)
                                    tag_buf = ""
                            else:
                                if idx > 0:
                                    yield ("answer", tag_buf[:idx])
                                tag_buf = tag_buf[idx + 7:]
                                in_think = True
                        else:
                            idx = tag_buf.find("</think>")
                            if idx == -1:
                                partial = _partial_tag_match(tag_buf, "</think>")
                                if partial > 0:
                                    emit = tag_buf[:-partial]
                                    if emit:
                                        yield ("thinking", emit)
                                    tag_buf = tag_buf[-partial:]
                                    break
                                else:
                                    if tag_buf:
                                        yield ("thinking", tag_buf)
                                    tag_buf = ""
                            else:
                                if idx > 0:
                                    yield ("thinking", tag_buf[:idx])
                                tag_buf = tag_buf[idx + 8:]
                                in_think = False
                        if not tag_buf:
                            break

def _partial_tag_match(text: str, tag: str) -> int:
    """Check if text ends with a partial match of tag. Returns length of partial match."""
    for i in range(min(len(tag) - 1, len(text)), 0, -1):
        if tag.startswith(text[-i:]):
            return i
    return 0

async def generate_full(model: str, prompt: str, system: str = "", options: dict = None,
                        think: bool = False, keep_alive: int = -1) -> str:
    parts = []
    async for typ, text in generate_stream(model, prompt, system, options, think, keep_alive):
        if typ == "answer":
            parts.append(text)
    return "".join(parts)

async def unload_model(model: str):
    url = f"{OLLAMA_URL}/api/generate"
    body = {"model": model, "prompt": "", "keep_alive": 0}
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            async with session.post(url, json=body) as resp:
                await resp.read()
    except Exception:
        pass

async def get_loaded_models() -> list:
    url = f"{OLLAMA_URL}/api/ps"
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get(url) as resp:
                data = await resp.json()
                return data.get("models", [])
    except Exception:
        return []
    
async def get_available_models() -> list[str]:
    """Get all models from Ollama /api/tags."""
    url = f"{OLLAMA_URL}/api/tags"
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get(url) as resp:
                data = await resp.json()
                return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []
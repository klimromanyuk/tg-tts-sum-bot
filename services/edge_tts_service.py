"""Edge-TTS cloud synthesis. No GPU required."""

import edge_tts, io

async def generate(text: str, voice: str = "ru-RU-DmitryNeural") -> bytes:
    communicate = edge_tts.Communicate(text=text, voice=voice)
    buffer = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            buffer.write(chunk["data"])
    data = buffer.getvalue()
    if not data:
        raise RuntimeError("Edge-TTS returned empty audio")
    return data
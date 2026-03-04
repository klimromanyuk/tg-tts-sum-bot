"""WAV to OGG Opus conversion via ffmpeg pipes (no temp files)."""

import subprocess, io
from config import FFMPEG_PATH

def wav_to_ogg(wav_bytes: bytes) -> bytes:
    result = subprocess.run(
        [FFMPEG_PATH, "-i", "pipe:0", "-c:a", "libopus", "-b:a", "64k", "-f", "ogg", "pipe:1"],
        input=wav_bytes, capture_output=True, timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg error: {result.stderr.decode()}")
    return result.stdout

def wav_bytes_from_numpy(wav_array, sr: int) -> bytes:
    import soundfile as sf
    buf = io.BytesIO()
    sf.write(buf, wav_array, sr, format='WAV')
    return buf.getvalue()
"""Constants and configuration. Runtime settings are in settings.json."""
import os
from dotenv import load_dotenv

load_dotenv()

# --- From .env ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
ALLOWED_CHAT_IDS = [int(x.strip()) for x in os.getenv("ALLOWED_CHAT_IDS", "").split(",") if x.strip()]
_DM_USERS_ENV = [int(x.strip()) for x in os.getenv("ALLOWED_DM_USERS", "").split(",") if x.strip()]
FFMPEG_PATH = os.getenv("FFMPEG_PATH", r"D:\programs\youtube downloader\ffmpeg_bin\ffmpeg.exe")

# --- Paths ---
TTS_MODEL_ID = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"
VOICES_DIR = "./voices/"
USERS_FILE = "./users.json"
SETTINGS_FILE = "./settings.json"
LOG_DIR = "./logs/"

# --- Timers & limits ---
MESSAGE_BUFFER_SIZE = 2000
COOLDOWN_SECONDS = 10
TTS_CHUNK_TIMEOUT = 120
TTS_MAX_CHUNK_CHARS = 150
STREAM_EDIT_THROTTLE_MS = 3000
VOICE_CALLBACK_TTL = 1800
PENDING_VOICE_CLEANUP_INTERVAL = 300
OLLAMA_URL = "http://localhost:11434"

# --- User defaults ---
DEFAULT_QWEN_VOICE = "warm_female"
DEFAULT_EDGE_VOICE = "en-US-AndrewMultilingualNeural"
DEFAULT_TTS_ENGINE = "qwen"
DEFAULT_AUTO_VOICE = False

# --- Ollama models ---
OLLAMA_MODELS = {
    "huihui_ai/qwen3-abliterated:14b-v2-q4_K_M": {"name": "Qwen3 14B Abliterated", "thinking": True},
    "dolphin-mistral-nemo-12b:latest": {"name": "Dolphin Mistral Nemo 12B", "thinking": False},
    "dolphin-qwen2-7b:latest": {"name": "Dolphin Qwen2 7B", "thinking": False},
}

# --- Qwen TTS voices (id -> display info) ---
QWEN_VOICES = {
    "warm_female": {"name": "Тёплый женский", "emoji": "👩"},
    "narrator":    {"name": "Рассказчик", "emoji": "👴"},
}

# --- Edge TTS voices ---
# Full list: https://speech.microsoft.com/portal/voicegallery
EDGE_VOICES = {
    "andrew": {"name": "Andrew", "emoji": "🧔", "voice_id": "en-US-AndrewMultilingualNeural"},
    "ava": {"name": "Ava", "emoji": "👱‍♀️", "voice_id": "en-US-AvaMultilingualNeural"},
    "brian": {"name": "Brian", "emoji": "🧑", "voice_id": "en-US-BrianMultilingualNeural"},
    "emma": {"name": "Emma", "emoji": "👩‍🦰", "voice_id": "en-US-EmmaMultilingualNeural"},
}

# --- Default settings.json (created if missing) ---
DEFAULT_SETTINGS = {
    "context_tokens": 8192,
    "temperature": 0.8,
    "max_tokens": 2048,
    "tts_max_tokens": 1024,
    "response_reserve": 1024,
    "thinking_sum": False,
    "thinking_resp": True,
    "tts_language": None,
    "ollama_model": "huihui_ai/qwen3-abliterated:14b-v2-q4_K_M",
    "allowed_dm_users": _DM_USERS_ENV,
}
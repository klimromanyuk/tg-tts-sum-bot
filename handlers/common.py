"""Handlers: /help, /start, /status"""
import time
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import config, texts
from utils.user_manager import ensure_user
from utils.settings_manager import get as get_settings
from utils.message_buffer import get_buffer
from services import gpu_manager, queue_manager

_start_time = time.time()

async def cmd_start_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    qv = "\n".join(f"  <code>{k}</code> {v['emoji']} {v['name']}" for k, v in config.QWEN_VOICES.items())
    ev = "\n".join(f"  <code>{k}</code> {v['emoji']} {v['name']}" for k, v in config.EDGE_VOICES.items())
    await update.message.reply_text(
        texts.MSG_HELP.format(qwen_voices=qv, edge_voices=ev),
        parse_mode=ParseMode.HTML,
    )

def _format_uptime() -> str:
    secs = int(time.time() - _start_time)
    days, secs = divmod(secs, 86400)
    hours, secs = divmod(secs, 3600)
    mins, secs = divmod(secs, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if mins:
        parts.append(f"{mins}m")
    parts.append(f"{secs}s")
    return " ".join(parts)

async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user = ensure_user(uid, update.effective_user.first_name)
    s = get_settings()
    voice = user["qwen_voice"] if user["tts_engine"] == "qwen" else user["edge_voice"]
    chat_id = update.effective_chat.id

    buf = get_buffer(chat_id)
    buf_size = len(buf)

    await update.message.reply_text(texts.MSG_STATUS.format(
        gpu_state=gpu_manager.get_state(),
        ollama_model=s["ollama_model"],
        engine=user["tts_engine"],
        voice=voice,
        auto="✅" if user["auto_voice"] else "❌",
        queue=queue_manager.qsize(),
        uptime=_format_uptime(),
        buffer=buf_size,
    ))
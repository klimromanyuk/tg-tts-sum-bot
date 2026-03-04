"""Handlers: /set, /settings, /unload, /allow, /model"""
import json
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import texts
from utils.settings_manager import get as get_settings, set_value, get_owner_id, is_dm_allowed, add_dm_user
import config
from services import gpu_manager

def is_owner(user_id: int) -> bool:
    return user_id == get_owner_id()

async def cmd_model(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_dm_allowed(uid):
        await update.message.reply_text(texts.MSG_ACCESS_DENIED.format(user_id=uid))
        return
    args = update.message.text.partition(" ")[2].strip()
    s = get_settings()

    if not args:
        # Get models from Ollama + merge with config
        from services.llm_service import get_available_models
        available = await get_available_models()

        # Merge: config models + any extra from Ollama
        all_models = dict(config.OLLAMA_MODELS)
        for m in available:
            if m not in all_models:
                all_models[m] = {"name": m, "thinking": False}

        lines = []
        for mid, info in all_models.items():
            check = "✅ " if mid == s["ollama_model"] else "  "
            think = "🧠" if info.get("thinking") else ""
            lines.append(f"{check}{think}<code>{mid}</code> — {info['name']}")

        await update.message.reply_text(
            texts.MSG_MODEL_LIST.format(models="\n".join(lines)),
            parse_mode=ParseMode.HTML,
        )
        return

    # Allow setting any model (not just from config)
    set_value("ollama_model", args)
    await update.message.reply_text(texts.MSG_MODEL_CHANGED.format(model=args))

async def cmd_unload(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text(texts.MSG_OWNER_ONLY)
        return
    await gpu_manager.unload_all()
    await update.message.reply_text(texts.MSG_UNLOADED)

async def cmd_settings(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text(texts.MSG_OWNER_ONLY)
        return
    s = get_settings()
    await update.message.reply_text(
        texts.MSG_SETTINGS_DISPLAY.format(settings=json.dumps(s, indent=2, ensure_ascii=False)),
        parse_mode=ParseMode.HTML,
    )

async def cmd_set(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text(texts.MSG_OWNER_ONLY)
        return
    args = update.message.text.partition(" ")[2].strip()
    if not args or len(args.split(None, 1)) < 2:
        await update.message.reply_text(texts.MSG_SET_USAGE)
        return
    key, val = args.split(None, 1)
    mapping = {
        "context": ("context_tokens", int),
        "temperature": ("temperature", float),
        "max_tokens": ("max_tokens", int),
        "tts_max_tokens": ("tts_max_tokens", int),
        "response_reserve": ("response_reserve", int),
        "thinking_sum": ("thinking_sum", lambda v: v.lower() in ("on", "true", "1")),
        "thinking_resp": ("thinking_resp", lambda v: v.lower() in ("on", "true", "1")),
        "show_thinking": ("thinking_resp", lambda v: v.lower() in ("on", "true", "1")),
        "tts_language": ("tts_language", lambda v: None if v.lower() in ("auto", "null", "none") else v),
    }
    if key not in mapping:
        await update.message.reply_text(texts.MSG_UNKNOWN_SETTING.format(key=key))
        return
    real_key, converter = mapping[key]
    try:
        converted = converter(val)
        set_value(real_key, converted)
        await update.message.reply_text(texts.MSG_SETTING_CHANGED.format(key=real_key, value=converted))
    except Exception as e:
        await update.message.reply_text(texts.MSG_SETTING_INVALID.format(error=str(e)))

async def cmd_allow(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text(texts.MSG_OWNER_ONLY)
        return
    args = update.message.text.partition(" ")[2].strip()
    if not args.isdigit():
        await update.message.reply_text(texts.MSG_ALLOW_USAGE)
        return
    uid = int(args)
    if add_dm_user(uid):
        await update.message.reply_text(texts.MSG_ALLOWED.format(user_id=uid))
    else:
        await update.message.reply_text(texts.MSG_ALREADY_ALLOWED.format(user_id=uid))
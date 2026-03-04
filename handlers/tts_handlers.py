"""Handlers: /tts, /voice, /autovoice"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import config, texts
from utils.user_manager import ensure_user, update_user
from services import queue_manager
from handlers.helpers import (
    check_cooldown, do_tts_for_user, send_voice_msg, send_typing,
    retry_send, log,
)

async def cmd_tts(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    cd = check_cooldown(uid)
    if cd:
        await update.message.reply_text(texts.MSG_COOLDOWN.format(sec=cd))
        return
    ensure_user(uid, update.effective_user.first_name)
    args = update.message.text.partition(" ")[2].strip()
    voice_override = None
    text = ""
    reply = update.message.reply_to_message
    if args:
        parts = args.split(None, 1)
        first = parts[0]
        if first in config.QWEN_VOICES or first in config.EDGE_VOICES:
            voice_override = first
            text = parts[1] if len(parts) > 1 else ""
        else:
            text = args
    if not text and reply:
        text = reply.text or reply.caption or ""
    if not text:
        await update.message.reply_text(texts.MSG_EMPTY_TEXT)
        return
    user = ensure_user(uid)
    engine = user["tts_engine"]
    if voice_override:
        engine = "qwen" if voice_override in config.QWEN_VOICES else "edge"
    chat_id = update.effective_chat.id
    msg_id = update.message.message_id

    if engine == "edge":
        try:
            status = await retry_send(ctx.bot, chat_id, texts.MSG_VOICING, reply_to=msg_id)
            await send_typing(ctx.bot, chat_id)
            audio, fmt = await do_tts_for_user(uid, text, voice_override)
            try:
                await status.delete()
            except Exception:
                pass
            await send_voice_msg(ctx.bot, chat_id, audio, fmt, reply_to=msg_id)
        except Exception as e:
            log.error(f"edge tts error: {e}")
            await update.message.reply_text(texts.MSG_EDGE_ERROR)
    else:
        async def task():
            try:
                status = await retry_send(ctx.bot, chat_id, texts.MSG_VOICING, reply_to=msg_id)
                await send_typing(ctx.bot, chat_id)
                audio, fmt = await do_tts_for_user(uid, text, voice_override)
                try:
                    await status.delete()
                except Exception:
                    pass
                await send_voice_msg(ctx.bot, chat_id, audio, fmt, reply_to=msg_id)
            except TimeoutError:
                await retry_send(ctx.bot, chat_id, texts.MSG_TTS_TIMEOUT, reply_to=msg_id)
            except Exception as e:
                log.error(f"qwen tts error: {e}")
                await retry_send(ctx.bot, chat_id, texts.MSG_TTS_ERROR.format(error=str(e)), reply_to=msg_id)
            return None

        ok = await queue_manager.put(task(), None)
        if not ok:
            await update.message.reply_text(texts.MSG_QUEUE_FULL)

async def cmd_voice(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user = ensure_user(uid, update.effective_user.first_name)
    kb = build_voice_keyboard(uid, user["tts_engine"])
    await update.message.reply_text(texts.MSG_CHOOSE_VOICE, reply_markup=kb)

def build_voice_keyboard(user_id: int, engine: str) -> InlineKeyboardMarkup:
    user = ensure_user(user_id)
    rows = []
    eq = texts.BTN_ENGINE_QWEN_SEL if engine == "qwen" else texts.BTN_ENGINE_QWEN
    ee = texts.BTN_ENGINE_EDGE_SEL if engine == "edge" else texts.BTN_ENGINE_EDGE
    rows.append([
        InlineKeyboardButton(eq, callback_data=f"veng_{user_id}_qwen"),
        InlineKeyboardButton(ee, callback_data=f"veng_{user_id}_edge"),
    ])
    if engine == "qwen":
        current = user["qwen_voice"]
        for vid, info in config.QWEN_VOICES.items():
            check = "✅ " if vid == current else ""
            rows.append([InlineKeyboardButton(
                f"{check}{info['emoji']} {info['name']} ({vid})",
                callback_data=f"vsel_{user_id}_qwen_{vid}"
            )])
    else:
        current = user["edge_voice"]
        for vid, info in config.EDGE_VOICES.items():
            check = "✅ " if vid == current else ""
            rows.append([InlineKeyboardButton(
                f"{check}{info['emoji']} {info['name']} ({vid})",
                callback_data=f"vsel_{user_id}_edge_{vid}"
            )])
    return InlineKeyboardMarkup(rows)

async def cmd_autovoice(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user = ensure_user(uid, update.effective_user.first_name)
    new_val = not user["auto_voice"]
    update_user(uid, auto_voice=new_val)
    await update.message.reply_text(texts.MSG_AUTOVOICE_ON if new_val else texts.MSG_AUTOVOICE_OFF)
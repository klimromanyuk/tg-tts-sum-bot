"""Callback query handlers."""
import time
from telegram import Update
from telegram.ext import ContextTypes
import config, texts
from utils.user_manager import ensure_user, update_user
from services import queue_manager
from handlers.helpers import (
    pending_voice, do_tts_for_user, send_voice_msg, send_typing,
    retry_send, get_voice_btn, log,
)
from handlers.tts_handlers import build_voice_keyboard

async def callback_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    uid = query.from_user.id
    ensure_user(uid, query.from_user.first_name)

    if data.startswith("veng_"):
        parts = data.split("_")
        target_uid = int(parts[1])
        engine = parts[2]
        if uid != target_uid:
            await query.answer(texts.MSG_NOT_FOR_YOU, show_alert=True)
            return
        update_user(uid, tts_engine=engine)
        kb = build_voice_keyboard(uid, engine)
        try:
            await query.edit_message_reply_markup(reply_markup=kb)
        except Exception:
            pass
        await query.answer()
        return

    if data.startswith("vsel_"):
        parts = data.split("_")
        target_uid = int(parts[1])
        engine = parts[2]
        voice_id = "_".join(parts[3:])
        if uid != target_uid:
            await query.answer(texts.MSG_NOT_FOR_YOU, show_alert=True)
            return
        if engine == "qwen":
            update_user(uid, qwen_voice=voice_id, tts_engine="qwen")
        else:
            update_user(uid, edge_voice=voice_id, tts_engine="edge")
        kb = build_voice_keyboard(uid, engine)
        try:
            await query.edit_message_reply_markup(reply_markup=kb)
        except Exception:
            pass
        vname = config.QWEN_VOICES.get(voice_id, config.EDGE_VOICES.get(voice_id, {})).get("name", voice_id)
        await query.answer(texts.MSG_VOICE_SELECTED.format(voice=vname))
        return

    if data.startswith("tts_"):
        pid = data[4:]
        if pid not in pending_voice:
            await query.answer(texts.MSG_TIMEOUT, show_alert=True)
            return
        entry = pending_voice[pid]
        if time.time() - entry["timestamp"] > config.VOICE_CALLBACK_TTL:
            del pending_voice[pid]
            await query.answer(texts.MSG_TIMEOUT, show_alert=True)
            return
        text = entry["text"]
        reply_to = entry.get("message_id")
        await query.answer(texts.MSG_VOICING)
        chat_id = query.message.chat.id
        user = ensure_user(uid)

        if user["tts_engine"] == "edge":
            try:
                await send_typing(ctx.bot, chat_id)
                audio, fmt = await do_tts_for_user(uid, text)
                await send_voice_msg(ctx.bot, chat_id, audio, fmt, reply_to=reply_to)
            except Exception as e:
                log.error(f"edge callback error: {e}")
                await retry_send(ctx.bot, chat_id, texts.MSG_EDGE_ERROR)
        else:
            async def task():
                try:
                    await send_typing(ctx.bot, chat_id)
                    audio, fmt = await do_tts_for_user(uid, text)
                    await send_voice_msg(ctx.bot, chat_id, audio, fmt, reply_to=reply_to)
                except TimeoutError:
                    await retry_send(ctx.bot, chat_id, texts.MSG_TTS_TIMEOUT, reply_to=reply_to)
                except Exception as e:
                    log.error(f"qwen callback error: {e}", exc_info=True)
                    await retry_send(ctx.bot, chat_id, texts.MSG_TTS_ERROR.format(error=str(e)), reply_to=reply_to)
                return None

            ok = await queue_manager.put(task(), None)
            if not ok:
                await retry_send(ctx.bot, chat_id, texts.MSG_QUEUE_FULL)
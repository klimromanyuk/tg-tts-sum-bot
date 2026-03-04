"""Handlers: /joke, /ask, /q, /chat, /newchat, /system"""
from telegram import Update
from telegram.ext import ContextTypes
import texts
from utils.user_manager import ensure_user
from utils.settings_manager import get as get_settings, is_dm_allowed
from utils.chat_memory import (
    get_history, add_message as mem_add, clear as mem_clear,
    get_system, set_system, is_chat_mode, toggle_chat, trim_history,
)
from utils.text_processor import est_tokens
from services import queue_manager
from handlers.helpers import (
    check_cooldown, stream_llm_response, handle_llm_result,
    retry_send, log,
)

async def cmd_joke(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    cd = check_cooldown(uid)
    if cd:
        await update.message.reply_text(texts.MSG_COOLDOWN.format(sec=cd))
        return
    user = ensure_user(uid, update.effective_user.first_name)
    chat_id = update.effective_chat.id
    msg_id = update.message.message_id
    extra = update.message.text.partition(" ")[2].strip()
    reply_text = ""
    if update.message.reply_to_message:
        reply_text = update.message.reply_to_message.text or update.message.reply_to_message.caption or ""

    prompt = texts.PROMPT_JOKE_USER
    if extra:
        prompt += f" ({extra})"
    if reply_text:
        prompt += f"\n\nContext:\n{reply_text}"

    async def task():
        try:
            s = get_settings()
            result = await stream_llm_response(
                ctx.bot, chat_id, prompt, texts.PROMPT_JOKE_SYSTEM,
                reply_to=msg_id, think_enabled=s["thinking_resp"],
            )
            await handle_llm_result(ctx.bot, chat_id, result, user, uid, msg_id)
        except Exception as e:
            log.error(f"joke error: {e}")
            await retry_send(ctx.bot, chat_id, texts.MSG_OLLAMA_ERROR, reply_to=msg_id)
        return None

    ok = await queue_manager.put(task(), None)
    if not ok:
        await update.message.reply_text(texts.MSG_QUEUE_FULL)
    elif queue_manager.qsize() > 1:
        await update.message.reply_text(texts.MSG_QUEUE_POS.format(pos=queue_manager.qsize()))

async def cmd_ask(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    cd = check_cooldown(uid)
    if cd:
        await update.message.reply_text(texts.MSG_COOLDOWN.format(sec=cd))
        return
    question = update.message.text.partition(" ")[2].strip()
    reply_text = ""
    if update.message.reply_to_message:
        reply_text = update.message.reply_to_message.text or update.message.reply_to_message.caption or ""

    if not question and not reply_text:
        await update.message.reply_text(texts.MSG_EMPTY_TEXT)
        return

    prompt = ""
    if question and reply_text:
        prompt = f"{question}\n\nContext:\n{reply_text}"
    elif question:
        prompt = question
    else:
        prompt = reply_text

    user = ensure_user(uid, update.effective_user.first_name)
    chat_id = update.effective_chat.id
    msg_id = update.message.message_id

    async def task():
        try:
            s = get_settings()
            result = await stream_llm_response(
                ctx.bot, chat_id, prompt, "",
                reply_to=msg_id, think_enabled=s["thinking_resp"],
            )
            await handle_llm_result(ctx.bot, chat_id, result, user, uid, msg_id)
        except Exception as e:
            log.error(f"ask error: {e}")
            await retry_send(ctx.bot, chat_id, texts.MSG_OLLAMA_ERROR, reply_to=msg_id)
        return None

    ok = await queue_manager.put(task(), None)
    if not ok:
        await update.message.reply_text(texts.MSG_QUEUE_FULL)

async def cmd_q(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_dm_allowed(uid):
        await update.message.reply_text(texts.MSG_ACCESS_DENIED.format(user_id=uid))
        return
    question = update.message.text.partition(" ")[2].strip()
    if not question:
        await update.message.reply_text(texts.MSG_EMPTY_TEXT)
        return
    user = ensure_user(uid, update.effective_user.first_name)
    chat_id = update.effective_chat.id
    msg_id = update.message.message_id

    async def task():
        try:
            s = get_settings()
            result = await stream_llm_response(
                ctx.bot, chat_id, question, "",
                reply_to=msg_id, think_enabled=s["thinking_resp"],
            )
            await handle_llm_result(ctx.bot, chat_id, result, user, uid, msg_id)
        except Exception as e:
            log.error(f"q error: {e}")
            await retry_send(ctx.bot, chat_id, texts.MSG_OLLAMA_ERROR, reply_to=msg_id)
        return None

    ok = await queue_manager.put(task(), None)
    if not ok:
        await update.message.reply_text(texts.MSG_QUEUE_FULL)

async def cmd_chat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_dm_allowed(uid):
        await update.message.reply_text(texts.MSG_ACCESS_DENIED.format(user_id=uid))
        return
    on = toggle_chat(uid)
    await update.message.reply_text(texts.MSG_CHAT_ON if on else texts.MSG_CHAT_OFF)

async def cmd_newchat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_dm_allowed(uid):
        await update.message.reply_text(texts.MSG_ACCESS_DENIED.format(user_id=uid))
        return
    mem_clear(uid)
    await update.message.reply_text(texts.MSG_NEWCHAT)

async def cmd_system(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_dm_allowed(uid):
        await update.message.reply_text(texts.MSG_ACCESS_DENIED.format(user_id=uid))
        return
    prompt = update.message.text.partition(" ")[2].strip()
    set_system(uid, prompt)
    await update.message.reply_text(texts.MSG_SYSTEM_SET if prompt else texts.MSG_SYSTEM_RESET)
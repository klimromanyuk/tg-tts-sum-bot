"""Handlers: /sum, /sumone"""
from telegram import Update
from telegram.ext import ContextTypes
import texts
from utils.user_manager import ensure_user
from utils.settings_manager import get as get_settings
from utils.text_processor import est_tokens, format_messages_for_prompt
from utils.message_buffer import collect_up, collect_down
from services import queue_manager
from handlers.helpers import (
    check_cooldown, stream_llm_response, safe_send, retry_send, log,
)

async def cmd_sum(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    cd = check_cooldown(uid)
    if cd:
        await update.message.reply_text(texts.MSG_COOLDOWN.format(sec=cd))
        return
    ensure_user(uid, update.effective_user.first_name)
    chat_id = update.effective_chat.id
    msg_id = update.message.message_id
    args = update.message.text.partition(" ")[2].strip()
    max_n = None
    style = ""
    if args:
        parts = args.split(None, 1)
        if parts[0].isdigit():
            max_n = int(parts[0])
            style = parts[1] if len(parts) > 1 else ""
        else:
            style = args
    s = get_settings()
    sys_prompt = texts.PROMPT_SUM_SYSTEM
    if style:
        sys_prompt += f"\n{texts.PROMPT_SUM_STYLE_PREFIX}{style}"
    available = s["context_tokens"] - est_tokens(sys_prompt) - s["response_reserve"]
    reply = update.message.reply_to_message
    if reply:
        msgs = collect_down(chat_id, reply.message_id, available, max_n)
        if not msgs:
            await update.message.reply_text(texts.MSG_REPLY_NOT_IN_BUFFER)
            return
    else:
        msgs = collect_up(chat_id, available, max_n)
    if not msgs:
        await update.message.reply_text(texts.MSG_BUFFER_EMPTY)
        return
    prompt_text = format_messages_for_prompt(msgs)
    actual = len(msgs)
    last = msgs[-1]
    last_info = f"[{last['username']}]: {last['text'][:50]}..."

    async def task():
        try:
            result = await stream_llm_response(
                ctx.bot, chat_id, prompt_text, sys_prompt,
                reply_to=msg_id, think_enabled=s["thinking_sum"],
            )
            text = result[0] if isinstance(result, tuple) else result
            if text:
                header = texts.MSG_SUM_RESULT.format(count=actual)
                if max_n and actual < max_n:
                    header = texts.MSG_SUM_TRUNCATED.format(
                        requested=max_n, actual=actual, last_msg=last_info)
                await safe_send(ctx.bot, chat_id, f"{header}\n\n{text}", reply_to=msg_id)
            else:
                await retry_send(ctx.bot, chat_id, texts.MSG_OLLAMA_ERROR, reply_to=msg_id)
        except Exception as e:
            log.error(f"sum error: {e}")
            await retry_send(ctx.bot, chat_id, texts.MSG_OLLAMA_ERROR, reply_to=msg_id)
        return None

    ok = await queue_manager.put(task(), None)
    if not ok:
        await update.message.reply_text(texts.MSG_QUEUE_FULL)

async def cmd_sumone(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text(texts.MSG_NO_REPLY)
        return
    uid = update.effective_user.id
    cd = check_cooldown(uid)
    if cd:
        await update.message.reply_text(texts.MSG_COOLDOWN.format(sec=cd))
        return
    ensure_user(uid, update.effective_user.first_name)
    reply = update.message.reply_to_message
    text_to_sum = reply.text or reply.caption or ""
    if not text_to_sum:
        await update.message.reply_text(texts.MSG_EMPTY_TEXT)
        return
    style = update.message.text.partition(" ")[2].strip()
    s = get_settings()
    sys_prompt = texts.PROMPT_SUMONE_SYSTEM
    if style:
        sys_prompt += f"\n{texts.PROMPT_SUM_STYLE_PREFIX}{style}"
    chat_id = update.effective_chat.id
    msg_id = update.message.message_id

    async def task():
        try:
            result = await stream_llm_response(
                ctx.bot, chat_id, text_to_sum, sys_prompt,
                reply_to=msg_id, think_enabled=s["thinking_resp"],
            )
            text = result[0] if isinstance(result, tuple) else result
            if text:
                await safe_send(ctx.bot, chat_id, text, reply_to=msg_id)
            else:
                await retry_send(ctx.bot, chat_id, texts.MSG_OLLAMA_ERROR, reply_to=msg_id)
        except Exception as e:
            log.error(f"sumone error: {e}")
            await retry_send(ctx.bot, chat_id, texts.MSG_OLLAMA_ERROR, reply_to=msg_id)
        return None

    ok = await queue_manager.put(task(), None)
    if not ok:
        await update.message.reply_text(texts.MSG_QUEUE_FULL)
"""Entry point. Registers handlers, starts polling."""
import asyncio, logging, os
from logging.handlers import RotatingFileHandler
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters,
)
import config
import texts
from utils.user_manager import ensure_user
from utils.settings_manager import is_dm_allowed
from utils.message_buffer import add_message as buf_add
from utils.chat_memory import (
    get_history, add_message as mem_add, is_chat_mode, get_system, trim_history,
)
from utils.text_processor import est_tokens
from services import queue_manager, gpu_manager
from handlers.helpers import (
    stream_llm_response, handle_llm_result, retry_send,
    start_cleanup, stop_cleanup, log,
)
from handlers.common import cmd_start_help, cmd_status
from handlers.llm import cmd_joke, cmd_ask, cmd_q, cmd_chat, cmd_newchat, cmd_system
from handlers.summarize import cmd_sum, cmd_sumone
from handlers.tts_handlers import cmd_tts, cmd_voice, cmd_autovoice
from handlers.admin import cmd_model, cmd_unload, cmd_settings, cmd_set, cmd_allow
from handlers.callbacks import callback_handler
from handlers.access import group_or_dm, dm_only, group_only
from utils.settings_manager import get as get_settings

os.makedirs(config.LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler(
            os.path.join(config.LOG_DIR, "bot.log"),
            maxBytes=5*1024*1024, backupCount=3, encoding="utf-8",
        ),
    ],
)

def is_group(update: Update) -> bool:
    return update.effective_chat.type in ("group", "supergroup")

def is_allowed_group(chat_id: int) -> bool:
    return chat_id in config.ALLOWED_CHAT_IDS

async def message_handler(update: Update, ctx):
    if not update.message or not update.message.text:
        return
    uid = update.effective_user.id
    chat_id = update.effective_chat.id
    username = update.effective_user.first_name or str(uid)
    ensure_user(uid, username)

    if is_group(update) and is_allowed_group(chat_id):
        buf_add(chat_id, uid, username, update.message.text,
                update.message.message_id, update.message.date)
        return

    if update.effective_chat.type == "private":
        if not is_dm_allowed(uid):
            await update.message.reply_text(texts.MSG_ACCESS_DENIED.format(user_id=uid))
            return
        if not is_chat_mode(uid):
            return
        s = get_settings()
        user = ensure_user(uid, username)
        mem_add(uid, "user", update.message.text)
        sys = get_system(uid)
        ctx_budget = s["context_tokens"] - est_tokens(sys) - s["response_reserve"]
        trim_history(uid, ctx_budget)
        history = get_history(uid)
        prompt = "\n".join(f"{m['role']}: {m['content']}" for m in history)
        msg_id = update.message.message_id

        async def task():
            try:
                result = await stream_llm_response(
                    ctx.bot, chat_id, prompt, sys,
                    reply_to=msg_id, think_enabled=s["thinking_resp"],
                )
                text = result[0] if isinstance(result, tuple) else result
                if text:
                    mem_add(uid, "assistant", text)
                    await handle_llm_result(ctx.bot, chat_id, result, user, uid, msg_id)
                else:
                    await retry_send(ctx.bot, chat_id, texts.MSG_OLLAMA_ERROR, reply_to=msg_id)
            except Exception as e:
                log.error(f"chat error: {e}")
                await retry_send(ctx.bot, chat_id, texts.MSG_OLLAMA_ERROR, reply_to=msg_id)
            return None

        ok = await queue_manager.put(task(), None)
        if not ok:
            await update.message.reply_text(texts.MSG_QUEUE_FULL)

async def post_init(app: Application):
    queue_manager.init(maxsize=10)
    asyncio.create_task(queue_manager.worker())
    start_cleanup()
    log.info("Bot started")

async def post_shutdown(app: Application):
    stop_cleanup()
    queue_manager.stop()
    await gpu_manager.unload_all()
    log.info("Bot shutdown")

def main():
    if not config.TELEGRAM_TOKEN:
        print("ERROR: Set TELEGRAM_TOKEN in config.py (or .env)!")
        return
    app = (Application.builder()
           .token(config.TELEGRAM_TOKEN)
           .post_init(post_init)
           .post_shutdown(post_shutdown)
           .build())
    
    # Public (groups + allowed DM)
    app.add_handler(CommandHandler("help", group_or_dm(cmd_start_help)))
    app.add_handler(CommandHandler("start", group_or_dm(cmd_start_help)))
    app.add_handler(CommandHandler("joke", group_or_dm(cmd_joke)))
    app.add_handler(CommandHandler("ask", group_or_dm(cmd_ask)))
    app.add_handler(CommandHandler("sum", group_or_dm(cmd_sum)))
    app.add_handler(CommandHandler("sumone", group_or_dm(cmd_sumone)))
    app.add_handler(CommandHandler("tts", group_or_dm(cmd_tts)))
    app.add_handler(CommandHandler("voice", group_or_dm(cmd_voice)))
    app.add_handler(CommandHandler("autovoice", group_or_dm(cmd_autovoice)))
    app.add_handler(CommandHandler("status", group_or_dm(cmd_status)))

    # DM only (access check inside handlers)
    app.add_handler(CommandHandler("q", dm_only(cmd_q)))
    app.add_handler(CommandHandler("chat", dm_only(cmd_chat)))
    app.add_handler(CommandHandler("newchat", dm_only(cmd_newchat)))
    app.add_handler(CommandHandler("system", dm_only(cmd_system)))
    app.add_handler(CommandHandler("model", dm_only(cmd_model)))

    # Owner only (access check inside handlers)
    app.add_handler(CommandHandler("unload", cmd_unload))
    app.add_handler(CommandHandler("settings", cmd_settings))
    app.add_handler(CommandHandler("set", cmd_set))
    app.add_handler(CommandHandler("allow", cmd_allow))

    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
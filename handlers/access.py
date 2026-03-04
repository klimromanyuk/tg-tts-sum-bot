"""Access control wrapper for handlers."""
from telegram import Update
from telegram.ext import ContextTypes
import config, texts
from utils.settings_manager import is_dm_allowed

def is_group(update: Update) -> bool:
    return update.effective_chat.type in ("group", "supergroup")

def is_private(update: Update) -> bool:
    return update.effective_chat.type == "private"

def group_or_dm(handler):
    """Allow in allowed groups + allowed DM users."""
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if is_group(update):
            if update.effective_chat.id in config.ALLOWED_CHAT_IDS:
                return await handler(update, ctx)
            return
        if is_private(update):
            if is_dm_allowed(update.effective_user.id):
                return await handler(update, ctx)
            await update.message.reply_text(
                texts.MSG_ACCESS_DENIED.format(user_id=update.effective_user.id))
            return
    return wrapper

def dm_only(handler):
    """Allow only for allowed DM users."""
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not is_private(update):
            return
        if is_dm_allowed(update.effective_user.id):
            return await handler(update, ctx)
        await update.message.reply_text(
            texts.MSG_ACCESS_DENIED.format(user_id=update.effective_user.id))
    return wrapper

def group_only(handler):
    """Allow only in allowed groups."""
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if is_group(update) and update.effective_chat.id in config.ALLOWED_CHAT_IDS:
            return await handler(update, ctx)
    return wrapper
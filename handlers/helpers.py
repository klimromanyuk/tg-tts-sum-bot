"""Shared helpers for all handlers."""
import asyncio, io, time, logging, uuid, aiohttp
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.error import RetryAfter
import config
import texts
from utils.text_processor import md_to_html, clean_for_tts
from utils.user_manager import ensure_user
from utils.settings_manager import get as get_settings
from services import gpu_manager, voice_manager, tts_service, edge_tts_service
from utils.audio_converter import wav_to_ogg, wav_bytes_from_numpy

log = logging.getLogger(__name__)

pending_voice = {}
_cooldowns = {}

def check_cooldown(user_id: int) -> int:
    now = time.time()
    last = _cooldowns.get(user_id, 0)
    diff = config.COOLDOWN_SECONDS - (now - last)
    if diff > 0:
        return int(diff) + 1
    _cooldowns[user_id] = now
    return 0

def escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

async def send_typing(bot: Bot, chat_id: int, action: str = "typing"):
    try:
        await bot.send_chat_action(chat_id, action)
    except Exception:
        pass

def get_voice_btn(msg_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(texts.BTN_VOICE, callback_data=f"tts_{msg_id}")]
    ])

def make_pending_id() -> str:
    return uuid.uuid4().hex[:12]

async def retry_send(bot: Bot, chat_id: int, text: str, parse_mode=None,
                     reply_to: int = None, reply_markup=None):
    for attempt in range(3):
        try:
            return await bot.send_message(
                chat_id, text, parse_mode=parse_mode,
                reply_to_message_id=reply_to, reply_markup=reply_markup,
            )
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after + 1)
        except Exception:
            if attempt == 2:
                raise
            await asyncio.sleep(2)

async def safe_send(bot: Bot, chat_id: int, text: str, reply_to: int = None, reply_markup=None):
    try:
        return await retry_send(bot, chat_id, md_to_html(text),
                                parse_mode=ParseMode.HTML, reply_to=reply_to, reply_markup=reply_markup)
    except Exception:
        return await retry_send(bot, chat_id, text, reply_to=reply_to, reply_markup=reply_markup)

async def safe_edit(msg, text, raw_html=False):
    try:
        content = text if raw_html else md_to_html(text)
        await msg.edit_text(content, parse_mode=ParseMode.HTML)
        return True
    except RetryAfter as e:
        await asyncio.sleep(e.retry_after + 1)
        try:
            content = text if raw_html else md_to_html(text)
            await msg.edit_text(content, parse_mode=ParseMode.HTML)
            return True
        except Exception:
            return False
    except Exception:
        try:
            import re
            plain = re.sub(r'<[^>]+>', '', text)
            await msg.edit_text(plain)
            return True
        except Exception:
            return False

async def do_tts_for_user(user_id: int, text: str, bot: Bot = None, chat_id: int = None,
                          voice_override: str = None) -> tuple[bytes, str]:
    """Generate TTS audio. Sends typing indicator if bot and chat_id provided."""
    user = ensure_user(user_id)
    engine = user["tts_engine"]
    if voice_override:
        if voice_override in config.QWEN_VOICES:
            engine = "qwen"
        elif voice_override in config.EDGE_VOICES:
            engine = "edge"

    typing_task = None
    if bot and chat_id:
        typing_task = asyncio.create_task(_typing_loop(bot, chat_id))

    try:
        if engine == "edge":
            voice_key = voice_override or user["edge_voice"]
            vid = voice_manager.get_edge_voice_id(voice_key)
            clean = clean_for_tts(text)
            mp3 = await edge_tts_service.generate(clean, vid)
            return mp3, "mp3"
        else:
            await gpu_manager.ensure_tts()
            voice_key = voice_override or user["qwen_voice"]
            prompt_path = voice_manager.get_qwen_prompt_path(voice_key)
            s = get_settings()
            lang = s.get("tts_language")
            wav_arr, sr = await tts_service.generate(text, prompt_path, s["tts_max_tokens"], language=lang)
            wav_bytes = wav_bytes_from_numpy(wav_arr, sr)
            try:
                ogg = wav_to_ogg(wav_bytes)
                return ogg, "ogg"
            except Exception:
                return wav_bytes, "wav"
    finally:
        if typing_task:
            typing_task.cancel()
            try:
                await typing_task
            except asyncio.CancelledError:
                pass

async def _typing_loop(bot, chat_id):
    """Send typing indicator every 4 seconds until cancelled."""
    try:
        while True:
            await send_typing(bot, chat_id, "upload_voice")
            await asyncio.sleep(4)
    except asyncio.CancelledError:
        pass

async def send_voice_msg(bot: Bot, chat_id: int, audio_bytes: bytes, fmt: str,
                         caption: str = None, reply_to: int = None):
    buf = io.BytesIO(audio_bytes)
    buf.name = {"ogg": "voice.ogg", "mp3": "voice.mp3", "wav": "voice.wav"}.get(fmt, "voice.ogg")
    if fmt == "wav":
        await bot.send_document(chat_id, document=buf, caption=caption, reply_to_message_id=reply_to)
    elif caption and len(caption) > 1024:
        msg = await retry_send(bot, chat_id, caption, reply_to=reply_to)
        await bot.send_voice(chat_id, voice=buf, reply_to_message_id=msg.message_id)
    else:
        await bot.send_voice(chat_id, voice=buf, caption=caption, reply_to_message_id=reply_to)

async def stream_llm_response(bot: Bot, chat_id: int, prompt: str, system: str = "",
                               reply_to: int = None, think_enabled: bool = True):
    """Stream LLM response. Tries sendMessageDraft first, falls back to editMessage."""
    from services import llm_service
    s = get_settings()
    model = s["ollama_model"]
    model_info = config.OLLAMA_MODELS.get(model, {"thinking": False})
    use_think = think_enabled and model_info.get("thinking", False)
    options = {
        "num_ctx": s["context_tokens"],
        "temperature": s["temperature"],
        "num_predict": s["max_tokens"],
    }
    await gpu_manager.ensure_ollama()

    status_msg = await retry_send(bot, chat_id,
                                  texts.MSG_THINKING if use_think else texts.MSG_GENERATING,
                                  reply_to=reply_to)

    answer_text = ""
    think_text = ""
    last_edit = time.time()
    throttle_sec = config.STREAM_EDIT_THROTTLE_MS / 1000.0
    draft_works = None  # None = untested, True/False = tested

    last_typing = time.time()

    async for typ, fragment in llm_service.generate_stream(
        model, prompt, system, options, think=use_think,
    ):
        # Periodic typing indicator
        now = time.time()
        if now - last_typing >= 4:
            await send_typing(bot, chat_id)
            last_typing = now

        if typ == "thinking":
            if use_think:
                think_text += fragment
                if (now - last_edit) >= throttle_sec:
                    display = texts.MSG_THINKING + f"\n\n<blockquote>{escape_html(think_text[-500:])}</blockquote>"
                    try:
                        await status_msg.edit_text(display, parse_mode=ParseMode.HTML)
                        last_edit = time.time()
                    except Exception:
                        pass
            # When thinking disabled — silently discard thinking tokens

        elif typ == "answer":
            answer_text += fragment
            if (now - last_edit) >= throttle_sec and answer_text.strip():
                display = ""
                if think_text:
                    short = think_text[-300:] if len(think_text) > 300 else think_text
                    display = f"<blockquote>💭 {escape_html(short)}</blockquote>\n\n"
                display += md_to_html(answer_text)

                if draft_works is None:
                    draft_works = await _try_send_draft(bot, chat_id, display, reply_to)
                    if draft_works:
                        last_edit = time.time()
                        continue

                if draft_works:
                    await _try_send_draft(bot, chat_id, display, reply_to)
                    last_edit = time.time()
                else:
                    ok = await safe_edit(status_msg, display, raw_html=True)
                    if ok:
                        last_edit = time.time()

    # Delete streaming message
    for attempt in range(3):
        try:
            await status_msg.delete()
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after + 1)
        except Exception:
            break

    return answer_text.strip(), think_text.strip()

async def _try_send_draft(bot: Bot, chat_id: int, text: str, reply_to: int = None) -> bool:
    """Try sendMessageDraft. Only works in private chats (chat_id > 0)."""
    if chat_id < 0:
        return False
    url = f"https://api.telegram.org/bot{bot.token}/sendMessageDraft"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "draft_id": 1,
    }
    if reply_to:
        payload["reply_parameters"] = {"message_id": reply_to}
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            async with session.post(url, json=payload) as resp:
                data = await resp.json()
                if data.get("ok"):
                    return True
                return False
    except Exception:
        return False

async def handle_llm_result(bot, chat_id, result, user, uid, reply_to):
    """Send LLM result. Text always stays visible. Voice is reply to text."""
    if isinstance(result, tuple):
        text, think = result
    else:
        text, think = result, ""
    if not text:
        await retry_send(bot, chat_id, texts.MSG_OLLAMA_ERROR, reply_to=reply_to)
        return

    # Build display with collapsed thinking
    s = get_settings()
    show_think = s.get("thinking_resp", True)

    display = ""
    if think and show_think:
        short = think if len(think) <= 500 else think[:200] + "\n...\n" + think[-200:]
        display = f"<blockquote>💭 {escape_html(short)}</blockquote>\n\n"
    display += md_to_html(text)

    pid = make_pending_id()

    if user["auto_voice"]:
        # Send text WITHOUT button first
        text_msg = await retry_send(bot, chat_id, display,
                                     parse_mode=ParseMode.HTML, reply_to=reply_to)

        # Try TTS
        try:
            audio, fmt = await do_tts_for_user(uid, text, bot=bot, chat_id=chat_id)
            await send_voice_msg(bot, chat_id, audio, fmt, reply_to=text_msg.message_id)
        except Exception as e:
            log.error(f"Auto-TTS failed: {e}")
            # TTS failed — add button so user can retry
            pending_voice[pid] = {"text": text, "timestamp": time.time(), "message_id": text_msg.message_id}
            try:
                await text_msg.edit_reply_markup(reply_markup=get_voice_btn(pid))
            except Exception:
                pass
    else:
        text_msg = await retry_send(bot, chat_id, display,
                                     parse_mode=ParseMode.HTML, reply_to=reply_to,
                                     reply_markup=get_voice_btn(pid))
        pending_voice[pid] = {"text": text, "timestamp": time.time(), "message_id": text_msg.message_id}

_cleanup_task = None

async def cleanup_pending_voice():
    try:
        while True:
            await asyncio.sleep(config.PENDING_VOICE_CLEANUP_INTERVAL)
            now = time.time()
            expired = [k for k, v in pending_voice.items()
                       if now - v["timestamp"] > config.VOICE_CALLBACK_TTL]
            for k in expired:
                del pending_voice[k]
            if expired:
                log.info(f"Cleaned {len(expired)} expired pending_voice entries")
    except asyncio.CancelledError:
        pass

def start_cleanup():
    global _cleanup_task
    _cleanup_task = asyncio.create_task(cleanup_pending_voice())

def stop_cleanup():
    global _cleanup_task
    if _cleanup_task:
        _cleanup_task.cancel()
        now = time.time()
        expired = [k for k, v in pending_voice.items()
                   if now - v["timestamp"] > config.VOICE_CALLBACK_TTL]
        for k in expired:
            del pending_voice[k]
        if expired:
            log.info(f"Cleaned {len(expired)} expired pending_voice entries")
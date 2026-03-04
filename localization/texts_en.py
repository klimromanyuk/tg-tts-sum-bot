"""English localization."""

# --- Buttons ---
BTN_VOICE = "🔊 Voice"
BTN_ENGINE_QWEN = "🧠 Qwen"
BTN_ENGINE_EDGE = "⚡ Edge"
BTN_ENGINE_QWEN_SEL = "✅ 🧠 Qwen"
BTN_ENGINE_EDGE_SEL = "✅ ⚡ Edge"

# --- Status messages ---
MSG_QUEUE_POS = "⏳ In queue (position {pos})..."
MSG_GENERATING = "⏳ Generating..."
MSG_VOICING = "⏳ Voicing..."
MSG_THINKING = "🤔 Thinking..."
MSG_DONE = "✅ Done"
MSG_TIMEOUT = "⌛ Timed out, please send the command again"
MSG_COOLDOWN = "⏳ Please wait {sec} sec."

# --- Errors ---
MSG_NOT_FOR_YOU = "❌ This keyboard is not for you"
MSG_ACCESS_DENIED = "⛔ Access denied. Your ID: {user_id}. Contact the administrator."
MSG_QUEUE_FULL = "❌ Too many requests, please try again later"
MSG_OLLAMA_ERROR = "⚠️ Ollama is not responding after several attempts."
MSG_TTS_ERROR = "⚠️ Voice generation error: {error}"
MSG_TTS_TIMEOUT = "⚠️ Voice generation took too long. Try shorter text."
MSG_EDGE_ERROR = "⚠️ Edge-TTS is unavailable. Use /voice to switch to Qwen."
MSG_FFMPEG_FALLBACK = "⚠️ Audio conversion error, sending WAV."
MSG_OWNER_ONLY = "❌ Bot owner only."
MSG_EMPTY_TEXT = "ℹ️ Provide text or reply to a message."
MSG_NO_REPLY = "ℹ️ Reply to a message with the /sumone command."
MSG_BUFFER_EMPTY = "ℹ️ Message buffer is empty."
MSG_REPLY_NOT_IN_BUFFER = "⚠️ This message was not found in the buffer. The buffer only contains messages received after the bot started."

# --- Summarization ---
MSG_SUM_RESULT = "📊 Summarization: {count} messages processed"
MSG_SUM_TRUNCATED = "⚠️ Requested {requested}, processed {actual} (context full).\nLast processed: {last_msg}"

# --- Settings & admin ---
MSG_MODEL_CHANGED = "✅ Model changed: {model}"
MSG_MODEL_NOT_FOUND = "❌ Model not found. Available:\n{models}"
MSG_MODEL_LIST = "📋 Ollama models:\n{models}"
MSG_SETTING_CHANGED = "✅ {key} = {value}"
MSG_THINKING_SHOW_ON = "🧠 Thinking display enabled"
MSG_THINKING_SHOW_OFF = "🧠 Thinking display hidden"
MSG_SETTING_INVALID = "❌ Invalid value: {error}"
MSG_UNKNOWN_SETTING = "❌ Unknown setting: {key}"
MSG_UNLOADED = "✅ GPU cleared, state: idle"
MSG_SETTINGS_DISPLAY = "⚙️ Settings:\n<pre>{settings}</pre>"
MSG_ALLOWED = "✅ User {user_id} added to allowed_dm_users."
MSG_ALREADY_ALLOWED = "ℹ️ User {user_id} is already in the list."
MSG_SET_USAGE = "Usage: /set <key> <value>"
MSG_ALLOW_USAGE = "Usage: /allow <user_id>"

# --- Voice & TTS ---
MSG_VOICE_SELECTED = "✅ Voice selected: {voice}"
MSG_AUTOVOICE_ON = "🔊 Auto-voice enabled"
MSG_AUTOVOICE_OFF = "🔇 Auto-voice disabled"
MSG_CHOOSE_VOICE = "🎙 Choose a voice:"

# --- Chat mode ---
MSG_CHAT_ON = "💬 Chat mode enabled. Send messages."
MSG_CHAT_OFF = "💬 Chat mode disabled."
MSG_NEWCHAT = "🔄 Dialog context cleared. Chat messages preserved."
MSG_SYSTEM_SET = "✅ System prompt set."
MSG_SYSTEM_RESET = "✅ System prompt reset."

# --- Status ---
MSG_STATUS = ("📊 Status:\n"
    "GPU: {gpu_state}\n"
    "Ollama model: {ollama_model}\n"
    "Your engine: {engine}\n"
    "Your voice: {voice}\n"
    "Auto-voice: {auto}\n"
    "Queue: {queue}\n"
    "Buffer: {buffer} messages\n"
    "Uptime: {uptime}")

# --- Help ---
MSG_HELP = """📖 <b>Bot Help</b>

<b>Commands for groups and DMs:</b>
/joke — joke from LLM (optional topic / reply)
/ask &lt;question&gt; — ask the LLM (reply for context)
/sum — chat summarization
/sumone — summarize a single message (reply)
/tts &lt;text&gt; — voice text
/tts (reply) — voice a message
/tts voice_id &lt;text&gt; — voice with a specific voice
/voice — choose voice and engine
/autovoice — toggle auto-voice
/status — bot status
/help — this help

<b>Summarization /sum:</b>
/sum — all messages (as many as fit)
/sum 50 — up to 50 messages
/sum tell it like a fairy tale — with style
/sum 50 tell it like a fairy tale — max 50 + style
Reply: summarize FROM that message to newer ones

<b>Direct messages:</b>
/q &lt;text&gt; — single question
/chat — toggle dialog mode
/newchat — clear context
/system &lt;text&gt; — system prompt
/model — list/change model

<b>Qwen voices:</b>
{qwen_voices}

<b>Edge voices:</b>
{edge_voices}
"""

# --- LLM Prompts ---
PROMPT_JOKE_SYSTEM = "You are a witty joke teller. Tell a funny joke. Respond only with the joke, no preamble. Respond in the same language as the user's request."
PROMPT_JOKE_USER = "Tell me a joke"
PROMPT_SUM_SYSTEM = "You are a summarization assistant. Provide a concise summary of the chat messages below. Respond in the same language as the messages."
PROMPT_SUM_STYLE_PREFIX = "Style: "
PROMPT_SUMONE_SYSTEM = "You are an assistant. Provide a concise summary or explanation of the following message. Respond in the same language as the message."
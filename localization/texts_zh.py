"""Chinese Simplified localization."""

# --- Buttons ---
BTN_VOICE = "🔊 朗读"
BTN_ENGINE_QWEN = "🧠 Qwen"
BTN_ENGINE_EDGE = "⚡ Edge"
BTN_ENGINE_QWEN_SEL = "✅ 🧠 Qwen"
BTN_ENGINE_EDGE_SEL = "✅ ⚡ Edge"

# --- Status messages ---
MSG_QUEUE_POS = "⏳ 排队中（第 {pos} 位）..."
MSG_GENERATING = "⏳ 生成中..."
MSG_VOICING = "⏳ 语音合成中..."
MSG_THINKING = "🤔 思考中..."
MSG_DONE = "✅ 完成"
MSG_TIMEOUT = "⌛ 超时，请重新发送命令"
MSG_COOLDOWN = "⏳ 请等待 {sec} 秒"

# --- Errors ---
MSG_NOT_FOR_YOU = "❌ 此菜单不适用于您"
MSG_ACCESS_DENIED = "⛔ 访问被拒绝。您的 ID：{user_id}。请联系管理员。"
MSG_QUEUE_FULL = "❌ 请求过多，请稍后再试"
MSG_OLLAMA_ERROR = "⚠️ Ollama 在多次尝试后无响应。"
MSG_TTS_ERROR = "⚠️ 语音生成错误：{error}"
MSG_TTS_TIMEOUT = "⚠️ 语音生成时间过长。请尝试较短的文本。"
MSG_EDGE_ERROR = "⚠️ Edge-TTS 不可用。请使用 /voice 切换到 Qwen。"
MSG_FFMPEG_FALLBACK = "⚠️ 音频转换错误，发送 WAV 文件。"
MSG_OWNER_ONLY = "❌ 仅限机器人所有者。"
MSG_EMPTY_TEXT = "ℹ️ 请输入文本或回复一条消息。"
MSG_NO_REPLY = "ℹ️ 请用 /sumone 命令回复一条消息。"
MSG_BUFFER_EMPTY = "ℹ️ 消息缓冲区为空。"
MSG_REPLY_NOT_IN_BUFFER = "⚠️ 在缓冲区中未找到此消息。缓冲区仅包含机器人启动后接收到的消息。"

# --- Summarization ---
MSG_SUM_RESULT = "📊 摘要：已处理 {count} 条消息"
MSG_SUM_TRUNCATED = "⚠️ 请求 {requested} 条，处理了 {actual} 条（上下文已满）。\n最后处理的：{last_msg}"

# --- Settings & admin ---
MSG_MODEL_CHANGED = "✅ 模型已更改：{model}"
MSG_MODEL_NOT_FOUND = "❌ 未找到模型。可用模型：\n{models}"
MSG_MODEL_LIST = "📋 Ollama 模型：\n{models}"
MSG_SETTING_CHANGED = "✅ {key} = {value}"
MSG_THINKING_SHOW_ON = "🧠 思考显示已开启"
MSG_THINKING_SHOW_OFF = "🧠 思考显示已隐藏"
MSG_SETTING_INVALID = "❌ 无效值：{error}"
MSG_UNKNOWN_SETTING = "❌ 未知设置：{key}"
MSG_UNLOADED = "✅ GPU 已清理，状态：idle"
MSG_SETTINGS_DISPLAY = "⚙️ 设置：\n<pre>{settings}</pre>"
MSG_ALLOWED = "✅ 用户 {user_id} 已添加到 allowed_dm_users。"
MSG_ALREADY_ALLOWED = "ℹ️ 用户 {user_id} 已在列表中。"
MSG_SET_USAGE = "用法：/set <键> <值>"
MSG_ALLOW_USAGE = "用法：/allow <user_id>"

# --- Voice & TTS ---
MSG_VOICE_SELECTED = "✅ 已选择语音：{voice}"
MSG_AUTOVOICE_ON = "🔊 自动语音已开启"
MSG_AUTOVOICE_OFF = "🔇 自动语音已关闭"
MSG_CHOOSE_VOICE = "🎙 请选择语音："

# --- Chat mode ---
MSG_CHAT_ON = "💬 聊天模式已开启。请发送消息。"
MSG_CHAT_OFF = "💬 聊天模式已关闭。"
MSG_NEWCHAT = "🔄 对话上下文已清除。聊天消息已保留。"
MSG_SYSTEM_SET = "✅ System prompt 已设置。"
MSG_SYSTEM_RESET = "✅ System prompt 已重置。"

# --- Status ---
MSG_STATUS = ("📊 状态：\n"
    "GPU：{gpu_state}\n"
    "Ollama 模型：{ollama_model}\n"
    "您的引擎：{engine}\n"
    "您的语音：{voice}\n"
    "自动语音：{auto}\n"
    "队列：{queue}\n"
    "缓冲区：{buffer} 条消息\n"
    "运行时间：{uptime}")

# --- Help ---
MSG_HELP = """📖 <b>机器人帮助</b>

<b>群组和私聊命令：</b>
/joke — LLM 讲笑话（可选主题 / 回复）
/ask &lt;问题&gt; — 向 LLM 提问（回复以提供上下文）
/sum — 聊天摘要
/sumone — 摘要单条消息（回复）
/tts &lt;文本&gt; — 朗读文本
/tts（回复）— 朗读消息
/tts 语音ID &lt;文本&gt; — 使用指定语音朗读
/voice — 选择语音和引擎
/autovoice — 开关自动语音
/status — 机器人状态
/help — 此帮助

<b>摘要 /sum：</b>
/sum — 所有消息（尽可能多）
/sum 50 — 最多 50 条消息
/sum 用童话风格讲述 — 带风格
/sum 50 用童话风格讲述 — 最多 50 + 风格
回复：从该消息到较新消息的摘要

<b>私聊：</b>
/q &lt;文本&gt; — 单个问题
/chat — 开关对话模式
/newchat — 清除上下文
/system &lt;文本&gt; — 系统提示词
/model — 列出/更改模型

<b>Qwen 语音：</b>
{qwen_voices}

<b>Edge 语音：</b>
{edge_voices}
"""

# --- LLM Prompts ---
PROMPT_JOKE_SYSTEM = "你是一个风趣的笑话讲述者。讲一个好笑的笑话。只回复笑话本身，不要有任何前言。用与用户请求相同的语言回复。"
PROMPT_JOKE_USER = "给我讲个笑话"
PROMPT_SUM_SYSTEM = "你是一个摘要助手。请对以下聊天消息提供简洁的摘要。用与消息相同的语言回复。"
PROMPT_SUM_STYLE_PREFIX = "风格："
PROMPT_SUMONE_SYSTEM = "你是一个助手。请对以下消息提供简洁的摘要或解释。用与消息相同的语言回复。"
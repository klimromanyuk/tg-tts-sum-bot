"""Russian localization."""

# --- Buttons ---
BTN_VOICE = "🔊 Озвучить"
BTN_ENGINE_QWEN = "🧠 Qwen"
BTN_ENGINE_EDGE = "⚡ Edge"
BTN_ENGINE_QWEN_SEL = "✅ 🧠 Qwen"
BTN_ENGINE_EDGE_SEL = "✅ ⚡ Edge"

# --- Status messages ---
MSG_QUEUE_POS = "⏳ В очереди (позиция {pos})..."
MSG_GENERATING = "⏳ Генерирую..."
MSG_VOICING = "⏳ Озвучиваю..."
MSG_THINKING = "🤔 Думаю..."
MSG_DONE = "✅ Готово"
MSG_TIMEOUT = "⌛ Время истекло, отправьте команду заново"
MSG_COOLDOWN = "⏳ Подождите {sec} сек."

# --- Errors ---
MSG_NOT_FOR_YOU = "❌ Эта клавиатура не для вас"
MSG_ACCESS_DENIED = "⛔ Доступ запрещён. Ваш ID: {user_id}. Обратитесь к администратору."
MSG_QUEUE_FULL = "❌ Слишком много запросов, попробуйте позже"
MSG_OLLAMA_ERROR = "⚠️ Ollama не отвечает после нескольких попыток."
MSG_TTS_ERROR = "⚠️ Ошибка генерации голоса: {error}"
MSG_TTS_TIMEOUT = "⚠️ Генерация голоса заняла слишком долго. Попробуйте короче текст."
MSG_EDGE_ERROR = "⚠️ Edge-TTS недоступен. Используйте /voice для переключения на Qwen."
MSG_FFMPEG_FALLBACK = "⚠️ Ошибка конвертации аудио, отправляю WAV."
MSG_OWNER_ONLY = "❌ Только для владельца бота."
MSG_EMPTY_TEXT = "ℹ️ Укажите текст или ответьте на сообщение."
MSG_NO_REPLY = "ℹ️ Ответьте на сообщение командой /sumone."
MSG_BUFFER_EMPTY = "ℹ️ Буфер сообщений пуст."
MSG_REPLY_NOT_IN_BUFFER = "⚠️ Это сообщение не найдено в буфере. Буфер содержит только сообщения, полученные после запуска бота."

# --- Summarization ---
MSG_SUM_RESULT = "📊 Суммаризация: учтено {count} сообщений"
MSG_SUM_TRUNCATED = "⚠️ Запрошено {requested}, учтено {actual} (контекст заполнен).\nПоследнее учтённое: {last_msg}"

# --- Settings & admin ---
MSG_MODEL_CHANGED = "✅ Модель изменена: {model}"
MSG_MODEL_NOT_FOUND = "❌ Модель не найдена. Доступные:\n{models}"
MSG_MODEL_LIST = "📋 Модели Ollama:\n{models}"
MSG_SETTING_CHANGED = "✅ {key} = {value}"
MSG_THINKING_SHOW_ON = "🧠 Отображение мыслей включено"
MSG_THINKING_SHOW_OFF = "🧠 Отображение мыслей выключено (мысли скрыты)"
MSG_SETTING_INVALID = "❌ Неверное значение: {error}"
MSG_UNKNOWN_SETTING = "❌ Неизвестная настройка: {key}"
MSG_UNLOADED = "✅ GPU очищен, состояние: idle"
MSG_SETTINGS_DISPLAY = "⚙️ Настройки:\n<pre>{settings}</pre>"
MSG_ALLOWED = "✅ Пользователь {user_id} добавлен в allowed_dm_users."
MSG_ALREADY_ALLOWED = "ℹ️ Пользователь {user_id} уже в списке."
MSG_SET_USAGE = "Использование: /set <ключ> <значение>"
MSG_ALLOW_USAGE = "Использование: /allow <user_id>"

# --- Voice & TTS ---
MSG_VOICE_SELECTED = "✅ Голос выбран: {voice}"
MSG_AUTOVOICE_ON = "🔊 Автоозвучка включена"
MSG_AUTOVOICE_OFF = "🔇 Автоозвучка выключена"
MSG_CHOOSE_VOICE = "🎙 Выберите голос:"

# --- Chat mode ---
MSG_CHAT_ON = "💬 Режим чата включён. Пишите сообщения."
MSG_CHAT_OFF = "💬 Режим чата выключён."
MSG_NEWCHAT = "🔄 Контекст диалога очищен. Сообщения в чате сохранены."
MSG_SYSTEM_SET = "✅ System prompt установлен."
MSG_SYSTEM_RESET = "✅ System prompt сброшен."

# --- Status ---
MSG_STATUS = ("📊 Статус:\n"
    "GPU: {gpu_state}\n"
    "Модель Ollama: {ollama_model}\n"
    "Ваш движок: {engine}\n"
    "Ваш голос: {voice}\n"
    "Автоозвучка: {auto}\n"
    "Очередь: {queue}\n"
    "Буфер: {buffer} сообщений\n"
    "Uptime: {uptime}")

# --- Help ---
MSG_HELP = """📖 <b>Справка по боту</b>

<b>Команды для групп и ЛС:</b>
/joke — анекдот от LLM (доп. тема / реплай)
/ask &lt;вопрос&gt; — вопрос к LLM (реплай для контекста)
/sum — суммаризация чата
/sumone — суммаризация одного сообщения (реплай)
/tts &lt;текст&gt; — озвучить текст
/tts (реплай) — озвучить сообщение
/tts голос_id &lt;текст&gt; — озвучить конкретным голосом
/voice — выбрать голос и движок
/autovoice — вкл/выкл автоозвучку
/status — состояние бота
/help — эта справка

<b>Суммаризация /sum:</b>
/sum — все сообщения (сколько влезет)
/sum 50 — максимум 50 сообщений
/sum расскажи как сказку — со стилем
/sum 50 расскажи как сказку — макс 50 + стиль
Реплай: суммаризация ОТ него к новым

<b>Личные сообщения:</b>
/q &lt;текст&gt; — одиночный вопрос
/chat — вкл/выкл диалог
/newchat — очистить контекст
/system &lt;текст&gt; — системный промпт
/model — список/смена модели

<b>Голоса Qwen:</b>
{qwen_voices}

<b>Голоса Edge:</b>
{edge_voices}
"""

# --- LLM Prompts (Russian) ---
PROMPT_JOKE_SYSTEM = "Ты остроумный рассказчик анекдотов. Расскажи смешной анекдот. Отвечай только анекдотом, без вступлений. Отвечай на том же языке, на котором написан запрос пользователя."
PROMPT_JOKE_USER = "Расскажи анекдот"
PROMPT_SUM_SYSTEM = "Ты помощник для суммаризации. Предоставь краткое изложение сообщений чата ниже. Отвечай на том же языке, на котором написаны сообщения."
PROMPT_SUM_STYLE_PREFIX = "Стиль: "
PROMPT_SUMONE_SYSTEM = "Ты помощник. Предоставь краткое изложение или объяснение следующего сообщения. Отвечай на том же языке, на котором написано сообщение."
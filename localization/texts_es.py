"""Spanish localization."""

# --- Buttons ---
BTN_VOICE = "🔊 Voz"
BTN_ENGINE_QWEN = "🧠 Qwen"
BTN_ENGINE_EDGE = "⚡ Edge"
BTN_ENGINE_QWEN_SEL = "✅ 🧠 Qwen"
BTN_ENGINE_EDGE_SEL = "✅ ⚡ Edge"

# --- Status messages ---
MSG_QUEUE_POS = "⏳ En cola (posición {pos})..."
MSG_GENERATING = "⏳ Generando..."
MSG_VOICING = "⏳ Vocalizando..."
MSG_THINKING = "🤔 Pensando..."
MSG_DONE = "✅ Listo"
MSG_TIMEOUT = "⌛ Tiempo agotado, envíe el comando de nuevo"
MSG_COOLDOWN = "⏳ Espere {sec} seg."

# --- Errors ---
MSG_NOT_FOR_YOU = "❌ Este teclado no es para usted"
MSG_ACCESS_DENIED = "⛔ Acceso denegado. Su ID: {user_id}. Contacte al administrador."
MSG_QUEUE_FULL = "❌ Demasiadas solicitudes, intente más tarde"
MSG_OLLAMA_ERROR = "⚠️ Ollama no responde después de varios intentos."
MSG_TTS_ERROR = "⚠️ Error de generación de voz: {error}"
MSG_TTS_TIMEOUT = "⚠️ La generación de voz tardó demasiado. Intente con un texto más corto."
MSG_EDGE_ERROR = "⚠️ Edge-TTS no disponible. Use /voice para cambiar a Qwen."
MSG_FFMPEG_FALLBACK = "⚠️ Error de conversión de audio, enviando WAV."
MSG_OWNER_ONLY = "❌ Solo para el propietario del bot."
MSG_EMPTY_TEXT = "ℹ️ Indique el texto o responda a un mensaje."
MSG_NO_REPLY = "ℹ️ Responda a un mensaje con el comando /sumone."
MSG_BUFFER_EMPTY = "ℹ️ El búfer de mensajes está vacío."
MSG_REPLY_NOT_IN_BUFFER = "⚠️ Este mensaje no se encontró en el búfer. El búfer solo contiene mensajes recibidos después del inicio del bot."

# --- Summarization ---
MSG_SUM_RESULT = "📊 Resumen: {count} mensajes procesados"
MSG_SUM_TRUNCATED = "⚠️ Solicitados {requested}, procesados {actual} (contexto lleno).\nÚltimo procesado: {last_msg}"

# --- Settings & admin ---
MSG_MODEL_CHANGED = "✅ Modelo cambiado: {model}"
MSG_MODEL_NOT_FOUND = "❌ Modelo no encontrado. Disponibles:\n{models}"
MSG_MODEL_LIST = "📋 Modelos Ollama:\n{models}"
MSG_SETTING_CHANGED = "✅ {key} = {value}"
MSG_THINKING_SHOW_ON = "🧠 Visualización del razonamiento activada"
MSG_THINKING_SHOW_OFF = "🧠 Visualización del razonamiento oculta"
MSG_SETTING_INVALID = "❌ Valor no válido: {error}"
MSG_UNKNOWN_SETTING = "❌ Configuración desconocida: {key}"
MSG_UNLOADED = "✅ GPU liberada, estado: idle"
MSG_SETTINGS_DISPLAY = "⚙️ Configuración:\n<pre>{settings}</pre>"
MSG_ALLOWED = "✅ Usuario {user_id} añadido a allowed_dm_users."
MSG_ALREADY_ALLOWED = "ℹ️ El usuario {user_id} ya está en la lista."
MSG_SET_USAGE = "Uso: /set <clave> <valor>"
MSG_ALLOW_USAGE = "Uso: /allow <user_id>"

# --- Voice & TTS ---
MSG_VOICE_SELECTED = "✅ Voz seleccionada: {voice}"
MSG_AUTOVOICE_ON = "🔊 Voz automática activada"
MSG_AUTOVOICE_OFF = "🔇 Voz automática desactivada"
MSG_CHOOSE_VOICE = "🎙 Elija una voz:"

# --- Chat mode ---
MSG_CHAT_ON = "💬 Modo chat activado. Escriba mensajes."
MSG_CHAT_OFF = "💬 Modo chat desactivado."
MSG_NEWCHAT = "🔄 Contexto del diálogo borrado. Los mensajes del chat se conservan."
MSG_SYSTEM_SET = "✅ System prompt establecido."
MSG_SYSTEM_RESET = "✅ System prompt restablecido."

# --- Status ---
MSG_STATUS = ("📊 Estado:\n"
    "GPU: {gpu_state}\n"
    "Modelo Ollama: {ollama_model}\n"
    "Su motor: {engine}\n"
    "Su voz: {voice}\n"
    "Voz automática: {auto}\n"
    "Cola: {queue}\n"
    "Búfer: {buffer} mensajes\n"
    "Tiempo de actividad: {uptime}")

# --- Help ---
MSG_HELP = """📖 <b>Ayuda del bot</b>

<b>Comandos para grupos y mensajes directos:</b>
/joke — chiste del LLM (tema opcional / respuesta)
/ask &lt;pregunta&gt; — pregunta al LLM (respuesta para contexto)
/sum — resumen del chat
/sumone — resumir un mensaje (respuesta)
/tts &lt;texto&gt; — vocalizar texto
/tts (respuesta) — vocalizar un mensaje
/tts id_voz &lt;texto&gt; — vocalizar con una voz específica
/voice — elegir voz y motor
/autovoice — activar/desactivar voz automática
/status — estado del bot
/help — esta ayuda

<b>Resumen /sum:</b>
/sum — todos los mensajes (los que quepan)
/sum 50 — máximo 50 mensajes
/sum cuéntalo como un cuento — con estilo
/sum 50 cuéntalo como un cuento — máx 50 + estilo
Respuesta: resumir DESDE ese mensaje hacia los más nuevos

<b>Mensajes directos:</b>
/q &lt;texto&gt; — pregunta única
/chat — activar/desactivar modo diálogo
/newchat — borrar contexto
/system &lt;texto&gt; — prompt del sistema
/model — listar/cambiar modelo

<b>Voces Qwen:</b>
{qwen_voices}

<b>Voces Edge:</b>
{edge_voices}
"""

# --- LLM Prompts ---
PROMPT_JOKE_SYSTEM = "Eres un contador de chistes ingenioso. Cuenta un chiste gracioso. Responde solo con el chiste, sin preámbulos. Responde en el mismo idioma que la solicitud del usuario."
PROMPT_JOKE_USER = "Cuéntame un chiste"
PROMPT_SUM_SYSTEM = "Eres un asistente de resumen. Proporciona un resumen conciso de los mensajes del chat a continuación. Responde en el mismo idioma que los mensajes."
PROMPT_SUM_STYLE_PREFIX = "Estilo: "
PROMPT_SUMONE_SYSTEM = "Eres un asistente. Proporciona un resumen o explicación concisa del siguiente mensaje. Responde en el mismo idioma que el mensaje."
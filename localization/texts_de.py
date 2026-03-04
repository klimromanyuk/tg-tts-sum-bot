"""German localization."""

# --- Buttons ---
BTN_VOICE = "🔊 Vorlesen"
BTN_ENGINE_QWEN = "🧠 Qwen"
BTN_ENGINE_EDGE = "⚡ Edge"
BTN_ENGINE_QWEN_SEL = "✅ 🧠 Qwen"
BTN_ENGINE_EDGE_SEL = "✅ ⚡ Edge"

# --- Status messages ---
MSG_QUEUE_POS = "⏳ In der Warteschlange (Position {pos})..."
MSG_GENERATING = "⏳ Generiere..."
MSG_VOICING = "⏳ Vertone..."
MSG_THINKING = "🤔 Denke nach..."
MSG_DONE = "✅ Fertig"
MSG_TIMEOUT = "⌛ Zeitüberschreitung, bitte senden Sie den Befehl erneut"
MSG_COOLDOWN = "⏳ Bitte warten Sie {sec} Sek."

# --- Errors ---
MSG_NOT_FOR_YOU = "❌ Diese Tastatur ist nicht für Sie"
MSG_ACCESS_DENIED = "⛔ Zugriff verweigert. Ihre ID: {user_id}. Kontaktieren Sie den Administrator."
MSG_QUEUE_FULL = "❌ Zu viele Anfragen, bitte versuchen Sie es später"
MSG_OLLAMA_ERROR = "⚠️ Ollama antwortet nach mehreren Versuchen nicht."
MSG_TTS_ERROR = "⚠️ Fehler bei der Sprachgenerierung: {error}"
MSG_TTS_TIMEOUT = "⚠️ Die Sprachgenerierung hat zu lange gedauert. Versuchen Sie einen kürzeren Text."
MSG_EDGE_ERROR = "⚠️ Edge-TTS nicht verfügbar. Verwenden Sie /voice, um zu Qwen zu wechseln."
MSG_FFMPEG_FALLBACK = "⚠️ Fehler bei der Audiokonvertierung, sende WAV."
MSG_OWNER_ONLY = "❌ Nur für den Bot-Besitzer."
MSG_EMPTY_TEXT = "ℹ️ Geben Sie Text ein oder antworten Sie auf eine Nachricht."
MSG_NO_REPLY = "ℹ️ Antworten Sie auf eine Nachricht mit dem Befehl /sumone."
MSG_BUFFER_EMPTY = "ℹ️ Der Nachrichtenpuffer ist leer."
MSG_REPLY_NOT_IN_BUFFER = "⚠️ Diese Nachricht wurde im Puffer nicht gefunden. Der Puffer enthält nur Nachrichten, die nach dem Start des Bots empfangen wurden."

# --- Summarization ---
MSG_SUM_RESULT = "📊 Zusammenfassung: {count} Nachrichten verarbeitet"
MSG_SUM_TRUNCATED = "⚠️ Angefordert {requested}, verarbeitet {actual} (Kontext voll).\nLetzte verarbeitete: {last_msg}"

# --- Settings & admin ---
MSG_MODEL_CHANGED = "✅ Modell geändert: {model}"
MSG_MODEL_NOT_FOUND = "❌ Modell nicht gefunden. Verfügbare:\n{models}"
MSG_MODEL_LIST = "📋 Ollama-Modelle:\n{models}"
MSG_SETTING_CHANGED = "✅ {key} = {value}"
MSG_THINKING_SHOW_ON = "🧠 Anzeige des Denkprozesses aktiviert"
MSG_THINKING_SHOW_OFF = "🧠 Anzeige des Denkprozesses ausgeblendet"
MSG_SETTING_INVALID = "❌ Ungültiger Wert: {error}"
MSG_UNKNOWN_SETTING = "❌ Unbekannte Einstellung: {key}"
MSG_UNLOADED = "✅ GPU freigegeben, Zustand: idle"
MSG_SETTINGS_DISPLAY = "⚙️ Einstellungen:\n<pre>{settings}</pre>"
MSG_ALLOWED = "✅ Benutzer {user_id} zu allowed_dm_users hinzugefügt."
MSG_ALREADY_ALLOWED = "ℹ️ Benutzer {user_id} ist bereits in der Liste."
MSG_SET_USAGE = "Verwendung: /set <Schlüssel> <Wert>"
MSG_ALLOW_USAGE = "Verwendung: /allow <user_id>"

# --- Voice & TTS ---
MSG_VOICE_SELECTED = "✅ Stimme ausgewählt: {voice}"
MSG_AUTOVOICE_ON = "🔊 Automatische Vertonung aktiviert"
MSG_AUTOVOICE_OFF = "🔇 Automatische Vertonung deaktiviert"
MSG_CHOOSE_VOICE = "🎙 Wählen Sie eine Stimme:"

# --- Chat mode ---
MSG_CHAT_ON = "💬 Chat-Modus aktiviert. Schreiben Sie Nachrichten."
MSG_CHAT_OFF = "💬 Chat-Modus deaktiviert."
MSG_NEWCHAT = "🔄 Dialogkontext gelöscht. Chat-Nachrichten bleiben erhalten."
MSG_SYSTEM_SET = "✅ System-Prompt gesetzt."
MSG_SYSTEM_RESET = "✅ System-Prompt zurückgesetzt."

# --- Status ---
MSG_STATUS = ("📊 Status:\n"
    "GPU: {gpu_state}\n"
    "Ollama-Modell: {ollama_model}\n"
    "Ihre Engine: {engine}\n"
    "Ihre Stimme: {voice}\n"
    "Auto-Vertonung: {auto}\n"
    "Warteschlange: {queue}\n"
    "Puffer: {buffer} Nachrichten\n"
    "Laufzeit: {uptime}")

# --- Help ---
MSG_HELP = """📖 <b>Bot-Hilfe</b>

<b>Befehle für Gruppen und Direktnachrichten:</b>
/joke — Witz vom LLM (optionales Thema / Antwort)
/ask &lt;Frage&gt; — Frage an das LLM (Antwort für Kontext)
/sum — Chat-Zusammenfassung
/sumone — einzelne Nachricht zusammenfassen (Antwort)
/tts &lt;Text&gt; — Text vertonen
/tts (Antwort) — Nachricht vertonen
/tts stimme_id &lt;Text&gt; — mit einer bestimmten Stimme vertonen
/voice — Stimme und Engine wählen
/autovoice — Auto-Vertonung ein-/ausschalten
/status — Bot-Status
/help — diese Hilfe

<b>Zusammenfassung /sum:</b>
/sum — alle Nachrichten (so viele wie passen)
/sum 50 — maximal 50 Nachrichten
/sum erzähl es wie ein Märchen — mit Stil
/sum 50 erzähl es wie ein Märchen — max 50 + Stil
Antwort: Zusammenfassung VON dieser Nachricht zu neueren

<b>Direktnachrichten:</b>
/q &lt;Text&gt; — einzelne Frage
/chat — Dialogmodus ein-/ausschalten
/newchat — Kontext löschen
/system &lt;Text&gt; — System-Prompt
/model — Modelle auflisten/wechseln

<b>Qwen-Stimmen:</b>
{qwen_voices}

<b>Edge-Stimmen:</b>
{edge_voices}
"""

# --- LLM Prompts ---
PROMPT_JOKE_SYSTEM = "Du bist ein witziger Witzeerzähler. Erzähle einen lustigen Witz. Antworte nur mit dem Witz, ohne Einleitung. Antworte in derselben Sprache wie die Anfrage des Benutzers."
PROMPT_JOKE_USER = "Erzähl mir einen Witz"
PROMPT_SUM_SYSTEM = "Du bist ein Zusammenfassungsassistent. Erstelle eine prägnante Zusammenfassung der folgenden Chat-Nachrichten. Antworte in derselben Sprache wie die Nachrichten."
PROMPT_SUM_STYLE_PREFIX = "Stil: "
PROMPT_SUMONE_SYSTEM = "Du bist ein Assistent. Erstelle eine prägnante Zusammenfassung oder Erklärung der folgenden Nachricht. Antworte in derselben Sprache wie die Nachricht."
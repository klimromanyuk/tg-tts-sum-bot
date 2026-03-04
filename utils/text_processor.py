"""Text processing: tokenization, chunking, markdown conversion."""
import re

def est_tokens(text: str) -> int:
    """Estimate token count. ~3.5 chars per token for Russian/Qwen."""
    return int(len(text) / 3.5)

def chunk_text(text: str, max_chars: int = 300) -> list[str]:
    """Split text by sentence boundaries. Never cuts words."""
    sentences = re.split(r'(?<=[.!?…»";\n])\s+', text)
    if len(sentences) == 1 and len(text) > max_chars:
        words = text.split()
        chunks = []
        current = ""
        for w in words:
            if len(current) + len(w) + 1 > max_chars and current:
                chunks.append(current.strip())
                current = w
            else:
                current = current + " " + w if current else w
        if current.strip():
            chunks.append(current.strip())
        return chunks
    chunks = []
    current = ""
    for s in sentences:
        if len(current) + len(s) + 1 > max_chars and current:
            chunks.append(current.strip())
            current = s
        else:
            current = current + " " + s if current else s
    if current.strip():
        chunks.append(current.strip())
    return chunks if chunks else [text]

def clean_for_tts(text: str) -> str:
    """Strip markdown/HTML for TTS input."""
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def _escape_html(text: str) -> str:
    """Escape HTML special chars."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def md_to_html(text: str) -> str:
    """Convert markdown to Telegram-compatible HTML.
    Escapes &<> FIRST, then applies formatting tags."""
    # Remove think blocks
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)

    # Extract code blocks before escaping
    code_blocks = []
    def _save_code(m):
        code_blocks.append(m.group(2))
        return f"\x00CODEBLOCK{len(code_blocks)-1}\x00"
    text = re.sub(r'```(\w*)\n([\s\S]*?)```', _save_code, text)

    inline_codes = []
    def _save_inline(m):
        inline_codes.append(m.group(1))
        return f"\x00INLINE{len(inline_codes)-1}\x00"
    text = re.sub(r'`(.+?)`', _save_inline, text)

    # Escape HTML
    text = _escape_html(text)

    # Restore code blocks (already escaped content)
    for i, code in enumerate(code_blocks):
        text = text.replace(f"\x00CODEBLOCK{i}\x00", f"<pre>{_escape_html(code)}</pre>")
    for i, code in enumerate(inline_codes):
        text = text.replace(f"\x00INLINE{i}\x00", f"<code>{_escape_html(code)}</code>")

    # Apply formatting
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
    text = re.sub(r'(?<!\w)\*(.+?)\*(?!\w)', r'<i>\1</i>', text)
    text = re.sub(r'(?<!\w)_(.+?)_(?!\w)', r'<i>\1</i>', text)
    text = re.sub(r'~~(.+?)~~', r'<s>\1</s>', text)

    return text.strip()

def format_messages_for_prompt(messages: list[dict]) -> str:
    """Format chat messages for LLM prompt."""
    lines = []
    for m in messages:
        lines.append(f"{m['username']}: {m['text']}")
    return "\n".join(lines)
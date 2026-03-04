import torch, gc, asyncio, numpy as np
from concurrent.futures import ThreadPoolExecutor
from config import TTS_MODEL_ID, TTS_CHUNK_TIMEOUT, TTS_MAX_CHUNK_CHARS
from utils.text_processor import chunk_text, clean_for_tts
import logging

log = logging.getLogger(__name__)
_model = None
_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="tts")

def is_loaded() -> bool:
    return _model is not None

def load_model():
    global _model
    if _model is not None:
        return
    from qwen_tts import Qwen3TTSModel
    log.info("Loading TTS model...")
    _model = Qwen3TTSModel.from_pretrained(
        TTS_MODEL_ID, device_map="cuda:0", dtype=torch.bfloat16, attn_implementation="sdpa",
    )
    log.info("TTS model loaded")

def unload_model():
    global _model
    if _model is None:
        return
    log.info("Unloading TTS model...")
    del _model
    _model = None
    torch.cuda.empty_cache()
    gc.collect()
    log.info("TTS model unloaded")

def _generate_one_chunk(text: str, prompt, max_tokens: int, language=None) -> tuple:
    log.info(f"TTS chunk: {len(text)} chars, max_tokens={max_tokens}, lang={language}")
    kwargs = {"text": text, "voice_clone_prompt": prompt, "max_new_tokens": max_tokens}
    if language:
        kwargs["language"] = language
    else:
        kwargs["language"] = "English"
    wavs, sr = _model.generate_voice_clone(**kwargs)
    return wavs[0], sr

async def generate(text: str, prompt_path: str, max_tokens: int = 4096, language: str = None) -> tuple:
    clean = clean_for_tts(text)
    if not clean:
        raise ValueError("Empty text after cleaning")

    prompt = torch.load(prompt_path, weights_only=False)
    chunks = chunk_text(clean, TTS_MAX_CHUNK_CHARS)
    log.info(f"TTS: {len(chunks)} chunks from {len(clean)} chars")

    loop = asyncio.get_event_loop()
    all_wavs = []
    sr = None

    for i, chunk in enumerate(chunks):
        log.info(f"TTS chunk {i+1}/{len(chunks)}: '{chunk[:60]}...'")
        retry_tokens = max_tokens
        success = False
        for attempt in range(3):
            try:
                wav, chunk_sr = await asyncio.wait_for(
                    loop.run_in_executor(
                        _executor, _generate_one_chunk, chunk, prompt, retry_tokens, language
                    ),
                    timeout=TTS_CHUNK_TIMEOUT,
                )
                all_wavs.append(wav)
                sr = chunk_sr
                success = True
                break
            except asyncio.TimeoutError:
                retry_tokens = retry_tokens // 2
                log.warning(f"TTS chunk {i+1} timeout (attempt {attempt+1}), retry with {retry_tokens} tokens")
                if attempt == 2:
                    log.error(f"TTS chunk {i+1} failed after 3 attempts")
            except Exception as e:
                log.error(f"TTS chunk {i+1} error: {e}")
                if attempt == 2:
                    raise
                retry_tokens = retry_tokens // 2

        if not success:
            if all_wavs:
                log.warning(f"Returning partial audio: {len(all_wavs)}/{len(chunks)} chunks")
                break
            else:
                raise TimeoutError(f"TTS failed on first chunk")

    if not all_wavs:
        raise RuntimeError("No audio generated")

    full_wav = np.concatenate(all_wavs) if len(all_wavs) > 1 else all_wavs[0]
    log.info(f"TTS complete: {len(full_wav)} samples total")
    return full_wav, sr
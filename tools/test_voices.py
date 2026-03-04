"""
Voice testing tool. Run from project root:
    python -m tools.test_voices
Or directly:
    cd D:\\projects\\tg-voice-bot && python tools\\test_voices.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import io, asyncio, subprocess, torch, numpy as np, soundfile as sf
from config import QWEN_VOICES, EDGE_VOICES, VOICES_DIR, TTS_MODEL_ID, FFMPEG_PATH

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..")

qwen_model = None

def load_qwen():
    global qwen_model
    if qwen_model:
        return
    print("\n⏳ Loading Qwen3-TTS...")
    from qwen_tts import Qwen3TTSModel
    qwen_model = Qwen3TTSModel.from_pretrained(
        TTS_MODEL_ID, device_map="cuda:0", dtype=torch.bfloat16, attn_implementation="sdpa",
    )
    print("✅ Model loaded.\n")

def unload_qwen():
    global qwen_model
    if not qwen_model:
        return
    del qwen_model
    qwen_model = None
    torch.cuda.empty_cache()
    import gc
    gc.collect()
    print("🗑 Qwen unloaded.")

def generate_qwen(voice_id: str, text: str, language: str = "English"):
    load_qwen()
    qvp_path = os.path.join(VOICES_DIR, voice_id, "prompt.qvp")
    if not os.path.exists(qvp_path):
        print(f"❌ Not found: {qvp_path}. Run prepare_voices.py first.")
        return
    prompt = torch.load(qvp_path, weights_only=False)
    print(f"⏳ Generating ({language})...")
    wavs, sr = qwen_model.generate_voice_clone(
        text=text, language=language, voice_clone_prompt=prompt,
    )
    audio = np.concatenate(wavs) if len(wavs) > 1 else wavs[0]

    # Try OGG first
    ogg_path = os.path.join(OUTPUT_DIR, "test_output.ogg")
    buf = io.BytesIO()
    sf.write(buf, audio, sr, format='WAV')
    result = subprocess.run(
        [FFMPEG_PATH, "-y", "-i", "pipe:0", "-c:a", "libopus", "-b:a", "64k", "-f", "ogg", ogg_path],
        input=buf.getvalue(), capture_output=True,
    )
    if result.returncode == 0:
        print(f"✅ Saved: {ogg_path}")
        os.startfile(ogg_path)
    else:
        print(f"⚠️ ffmpeg error: {result.stderr.decode()[:200]}")
        # Fallback to WAV
        wav_path = os.path.join(OUTPUT_DIR, "test_output.wav")
        sf.write(wav_path, audio, sr)
        print(f"💾 Saved WAV: {wav_path}")
        os.startfile(wav_path)

def generate_edge(voice_id: str, text: str):
    voice_data = EDGE_VOICES[voice_id]
    tts_voice = voice_data["voice_id"]

    async def _gen():
        import edge_tts
        mp3_path = os.path.join(OUTPUT_DIR, "test_output.mp3")
        communicate = edge_tts.Communicate(text=text, voice=tts_voice)
        await communicate.save(mp3_path)
        return mp3_path

    print("⏳ Generating via Edge-TTS...")
    try:
        path = asyncio.run(_gen())
        print(f"✅ Saved: {path}")
        os.startfile(path)
    except Exception as e:
        print(f"❌ Edge-TTS error: {e}")

def show_voices():
    print("\n" + "=" * 50)
    print("QWEN voices (local, GPU):")
    print("-" * 50)
    for i, (vid, v) in enumerate(QWEN_VOICES.items()):
        qvp = os.path.join(VOICES_DIR, vid, "prompt.qvp")
        ready = "✅" if os.path.exists(qvp) else "❌ no .qvp"
        print(f"  q{i+1}) {v['emoji']} {v['name']} ({vid}) {ready}")
    print("\nEDGE voices (cloud, no GPU):")
    print("-" * 50)
    for i, (vid, v) in enumerate(EDGE_VOICES.items()):
        print(f"  e{i+1}) {v['emoji']} {v['name']} ({vid})")
    print("=" * 50)

def main():
    print("🎙 Voice Testing Tool")
    print("Commands: list, quit")
    print("For Qwen: choose language when prompted (default: English)\n")

    qwen_list = list(QWEN_VOICES.keys())
    edge_list = list(EDGE_VOICES.keys())

    show_voices()

    while True:
        print()
        choice = input("Voice (q1/e1/id or list/quit): ").strip().lower()
        if choice == "quit":
            unload_qwen()
            break
        if choice == "list":
            show_voices()
            continue
        if not choice:
            continue

        engine = None
        voice_id = None
        if choice.startswith("q") and choice[1:].isdigit():
            idx = int(choice[1:]) - 1
            if 0 <= idx < len(qwen_list):
                engine, voice_id = "qwen", qwen_list[idx]
        elif choice.startswith("e") and choice[1:].isdigit():
            idx = int(choice[1:]) - 1
            if 0 <= idx < len(edge_list):
                engine, voice_id = "edge", edge_list[idx]
        elif choice in QWEN_VOICES:
            engine, voice_id = "qwen", choice
        elif choice in EDGE_VOICES:
            engine, voice_id = "edge", choice

        if not engine:
            print("❌ Voice not found. Type 'list' for available voices.")
            continue

        name = (QWEN_VOICES if engine == "qwen" else EDGE_VOICES)[voice_id]["name"]
        print(f"Selected: {name} ({engine}:{voice_id})")

        text = input("Text to speak: ").strip()
        if not text:
            print("❌ Empty text.")
            continue

        try:
            if engine == "qwen":
                lang = input("Language (English/Russian/Chinese/auto, default=English): ").strip()
                if not lang or lang.lower() == "auto":
                    lang = "English"
                generate_qwen(voice_id, text, lang)
            else:
                generate_edge(voice_id, text)
        except Exception as ex:
            print(f"❌ Error: {ex}")

if __name__ == "__main__":
    main()
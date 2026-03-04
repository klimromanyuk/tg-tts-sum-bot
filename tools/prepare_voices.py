"""
Скрипт подготовки голосов для Qwen3-TTS.

Использование:
1. Создайте папку voices/<voice_id>/
2. Положите туда reference.wav (5-15 сек чистой речи)
3. Создайте meta.json: {"name": "Название", "emoji": "👩", "ref_text": "Точная расшифровка аудио"}
4. Запустите: python prepare_voices.py

Скрипт создаст prompt.qvp и preview.wav в каждой папке.
"""

import os, json, shutil, torch, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import VOICES_DIR, TTS_MODEL_ID

MODEL_ID = TTS_MODEL_ID

def main():
    from qwen_tts import Qwen3TTSModel

    dirs = [d for d in os.listdir(VOICES_DIR)
            if os.path.isdir(os.path.join(VOICES_DIR, d))]

    if not dirs:
        print(f"Нет папок в {VOICES_DIR}. Создайте папки с reference.wav и meta.json.")
        return

    to_process = []
    for d in dirs:
        path = os.path.join(VOICES_DIR, d)
        meta_path = os.path.join(path, "meta.json")
        ref_path = os.path.join(path, "reference.wav")
        qvp_path = os.path.join(path, "prompt.qvp")

        if os.path.exists(qvp_path):
            print(f"  [{d}] prompt.qvp уже существует, пропускаю")
            continue
        if not os.path.exists(meta_path):
            print(f"  [{d}] Нет meta.json, пропускаю")
            continue
        if not os.path.exists(ref_path):
            print(f"  [{d}] Нет reference.wav, пропускаю")
            continue
        to_process.append((d, path, meta_path, ref_path, qvp_path))

    if not to_process:
        print("Нечего обрабатывать.")
        return

    print(f"Загружаю модель {MODEL_ID}...")
    model = Qwen3TTSModel.from_pretrained(
        MODEL_ID, device_map="cuda:0", dtype=torch.bfloat16, attn_implementation="sdpa",
    )
    print("Модель загружена.")

    for d, path, meta_path, ref_path, qvp_path in to_process:
        print(f"\nОбрабатываю [{d}]...")
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        ref_text = meta.get("ref_text", "")
        if not ref_text:
            print(f"  ВНИМАНИЕ: ref_text пуст в meta.json! Качество будет низким.")

        prompt = model.create_voice_clone_prompt(
            ref_audio=ref_path,
            ref_text=ref_text,
        )
        torch.save(prompt, qvp_path)
        print(f"  Сохранён {qvp_path}")

        preview_path = os.path.join(path, "preview.wav")
        if not os.path.exists(preview_path):
            shutil.copy2(ref_path, preview_path)
            print(f"  Скопирован preview.wav")

    del model
    torch.cuda.empty_cache()
    import gc; gc.collect()
    print("\nГотово! Модель выгружена.")

if __name__ == "__main__":
    main()
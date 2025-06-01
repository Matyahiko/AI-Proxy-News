#!/usr/bin/env python3
import sys
import whisper

if len(sys.argv) != 3:
    print("Usage: asr.py <wav_path> <output_txt>")
    sys.exit(1)

wav_path = sys.argv[1]
output_path = sys.argv[2]

model = whisper.load_model("large-v3")
result = model.transcribe(wav_path, language="ja")

with open(output_path, "w", encoding="utf-8") as f:
    f.write(result["text"].strip() + "\n")

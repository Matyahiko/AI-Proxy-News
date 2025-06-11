#!/usr/bin/env python3
import sys
import os
import subprocess
import tempfile
from dotenv import load_dotenv
from google.cloud import speech

load_dotenv(os.path.join("secrets", ".env"))

if len(sys.argv) != 3:
    print("Usage: asr.py <audio_path> <output_txt>")
    sys.exit(1)

src_path = sys.argv[1]
output_path = sys.argv[2]
print(f"[ASR] Transcribing '{src_path}'...")

def convert_to_wav(path: str) -> str:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tmp.close()
    subprocess.run([
        "ffmpeg",
        "-y",
        "-i",
        path,
        "-ar",
        "16000",
        "-ac",
        "1",
        tmp.name,
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return tmp.name

use_path = src_path
cleanup = False
if not src_path.lower().endswith(".wav"):
    use_path = convert_to_wav(src_path)
    cleanup = True

client = speech.SpeechClient()

with open(use_path, "rb") as audio_file:
    audio_content = audio_file.read()

audio = speech.RecognitionAudio(content=audio_content)
config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    language_code="ja-JP",
)

response = client.recognize(config=config, audio=audio)
text = "".join(result.alternatives[0].transcript for result in response.results)

if cleanup:
    os.remove(use_path)

with open(output_path, "w", encoding="utf-8") as f:
    f.write(text.strip() + "\n")
print(f"[ASR] Transcript saved to '{output_path}'")

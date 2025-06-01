#!/usr/bin/env python3
import sys
from dotenv import load_dotenv
from google.cloud import speech

load_dotenv()

if len(sys.argv) != 3:
    print("Usage: asr.py <wav_path> <output_txt>")
    sys.exit(1)

wav_path = sys.argv[1]
output_path = sys.argv[2]

client = speech.SpeechClient()

with open(wav_path, "rb") as audio_file:
    audio_content = audio_file.read()

audio = speech.RecognitionAudio(content=audio_content)
config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    language_code="ja-JP",
)

response = client.recognize(config=config, audio=audio)
text = "".join(result.alternatives[0].transcript for result in response.results)

with open(output_path, "w", encoding="utf-8") as f:
    f.write(text.strip() + "\n")

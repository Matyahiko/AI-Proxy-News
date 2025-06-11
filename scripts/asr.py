#!/usr/bin/env python3
import sys
import os
import subprocess
import tempfile
import uuid
from dotenv import load_dotenv
from google.cloud import speech, storage

load_dotenv(os.path.join("secrets", ".env"))

bucket_name = os.getenv("GCS_BUCKET")
if not bucket_name:
    print("Error: GCS_BUCKET not set in environment")
    sys.exit(1)

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

speech_client = speech.SpeechClient()
storage_client = storage.Client()

bucket = storage_client.bucket(bucket_name)
blob_name = f"audio/{uuid.uuid4()}.wav"
blob = bucket.blob(blob_name)
blob.upload_from_filename(use_path)
gcs_uri = f"gs://{bucket_name}/{blob_name}"

audio = speech.RecognitionAudio(uri=gcs_uri)
config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    language_code="ja-JP",
)

# Use long-running recognition for better handling of long audio files
operation = speech_client.long_running_recognize(config=config, audio=audio)
response = operation.result(timeout=600)
text = "".join(result.alternatives[0].transcript for result in response.results)

blob.delete()  # cleanup uploaded file

if cleanup:
    os.remove(use_path)

with open(output_path, "w", encoding="utf-8") as f:
    f.write(text.strip() + "\n")
print(f"[ASR] Transcript saved to '{output_path}'")

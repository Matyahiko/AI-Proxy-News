#!/usr/bin/env python3
import sys
import os
import subprocess
import tempfile
import uuid
from contextlib import contextmanager
from typing import Optional
from google.cloud import speech, storage
from config import validate_gcs_config

bucket_name = validate_gcs_config()

if len(sys.argv) != 3:
    print("Usage: asr.py <audio_path> <output_txt>")
    sys.exit(1)

src_path = sys.argv[1]
output_path = sys.argv[2]
print(f"[ASR] Transcribing '{src_path}'...")

def convert_to_wav(path: str) -> str:
    """Convert audio file to WAV format suitable for Speech-to-Text."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tmp.close()
    
    try:
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
    except subprocess.CalledProcessError as e:
        os.remove(tmp.name)
        print(f"Error converting audio file: {e}")
        sys.exit(1)


@contextmanager
def temporary_wav_file(src_path: str):
    """Context manager for handling temporary WAV file conversion."""
    if src_path.lower().endswith(".wav"):
        yield src_path
    else:
        temp_path = convert_to_wav(src_path)
        try:
            yield temp_path
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


def upload_to_gcs(bucket_name: str, local_path: str) -> str:
    """Upload audio file to Google Cloud Storage and return GCS URI."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob_name = f"audio/{uuid.uuid4()}.wav"
    blob = bucket.blob(blob_name)
    
    try:
        blob.upload_from_filename(local_path)
        return f"gs://{bucket_name}/{blob_name}", blob
    except Exception as e:
        print(f"Error uploading to GCS: {e}")
        sys.exit(1)


def transcribe_audio(gcs_uri: str) -> str:
    """Transcribe audio from GCS URI using Speech-to-Text API."""
    speech_client = speech.SpeechClient()
    
    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="ja-JP",
    )
    
    try:
        operation = speech_client.long_running_recognize(config=config, audio=audio)
        response = operation.result(timeout=600)
        return "".join(result.alternatives[0].transcript for result in response.results)
    except Exception as e:
        print(f"Error during transcription: {e}")
        sys.exit(1)


def save_transcript(text: str, output_path: str) -> None:
    """Save transcript text to file."""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text.strip() + "\n")
    except IOError as e:
        print(f"Error saving transcript: {e}")
        sys.exit(1)

with temporary_wav_file(src_path) as wav_path:
    gcs_uri, blob = upload_to_gcs(bucket_name, wav_path)
    
    try:
        text = transcribe_audio(gcs_uri)
        save_transcript(text, output_path)
        print(f"[ASR] Transcript saved to '{output_path}'")
    finally:
        # Clean up uploaded file
        try:
            blob.delete()
        except Exception as e:
            print(f"Warning: Could not delete GCS file: {e}")

#!/usr/bin/env python3
import asyncio
import json
import os
import queue
from typing import Iterable

from dotenv import load_dotenv
from google.api_core.exceptions import GoogleAPICallError
from google.cloud import speech
import websockets

load_dotenv(os.path.join("secrets", ".env"))

PORT = int(os.environ.get("ASR_PORT", "7001"))


def make_request_stream(
    q: queue.Queue, cfg: speech.StreamingRecognitionConfig
) -> Iterable[speech.StreamingRecognizeRequest]:
    """Yield config first then queued audio chunks."""
    yield speech.StreamingRecognizeRequest(streaming_config=cfg)
    while True:
        data = q.get()
        if data is None:
            break
        yield speech.StreamingRecognizeRequest(audio_content=data)


async def handle(websocket):
    print("Client connected")
    try:
        client = speech.SpeechClient()
        client.get_project_id()
    except Exception:
        print("WARNING: credentials missing")
        await websocket.close()
        return
    await websocket.send("READY")
    # MediaRecorder in the demo captures audio as WebM/Opus.
    # The sample rate is detected automatically.
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
        language_code="ja-JP",
    )
    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True,
    )

    q: queue.Queue[bytes | None] = queue.Queue()
    loop = asyncio.get_event_loop()
    request_stream = lambda: make_request_stream(q, streaming_config)

    async def send_audio():
        try:
            async for message in websocket:
                if isinstance(message, bytes):
                    print("Received chunk", len(message))
                    q.put(message)
                else:
                    if message == "EOS":
                        break
        finally:
            q.put(None)
            print("Client disconnected")

    def forward_responses():
        try:
            responses = client.streaming_recognize(requests=request_stream())
            for response in responses:
                for result in response.results:
                    if not result.alternatives:
                        continue
                    payload = json.dumps(
                        {
                            "text": result.alternatives[0].transcript,
                            "isFinal": result.is_final,
                        },
                        ensure_ascii=False,
                    )
                    asyncio.run_coroutine_threadsafe(websocket.send(payload), loop)
        except GoogleAPICallError as exc:
            print("Speech API error:", exc)

    sender = asyncio.create_task(send_audio())
    receiver = loop.run_in_executor(None, forward_responses)
    await asyncio.gather(sender, receiver)


async def main():
    async with websockets.serve(handle, "0.0.0.0", PORT, max_size=None):
        print(f"Realtime ASR server listening on ws://0.0.0.0:{PORT}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())

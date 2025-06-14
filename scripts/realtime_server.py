#!/usr/bin/env python3
import asyncio
import os
import queue
import threading
from dotenv import load_dotenv
from google.cloud import speech
import websockets

load_dotenv(os.path.join('secrets', '.env'))

PORT = int(os.environ.get('ASR_PORT', '9000'))

async def handle(websocket):
    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code='ja-JP',
    )
    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=False,
    )

    q = queue.Queue()
    loop = asyncio.get_event_loop()

    def request_gen():
        yield speech.StreamingRecognizeRequest(streaming_config=streaming_config)
        while True:
            data = q.get()
            if data is None:
                break
            yield speech.StreamingRecognizeRequest(audio_content=data)

    async def reader():
        try:
            async for message in websocket:
                if isinstance(message, bytes):
                    q.put(message)
                else:
                    if message == 'EOS':
                        break
        finally:
            q.put(None)

    def process():
        responses = client.streaming_recognize(request_gen())
        for response in responses:
            for result in response.results:
                if not result.alternatives:
                    continue
                text = result.alternatives[0].transcript
                asyncio.run_coroutine_threadsafe(websocket.send(text), loop)

    thread = threading.Thread(target=process, daemon=True)
    thread.start()
    await reader()
    thread.join()

async def main():
    async with websockets.serve(handle, '0.0.0.0', PORT, max_size=None):
        print(f'Realtime ASR server listening on ws://0.0.0.0:{PORT}')
        await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())

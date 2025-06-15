#!/usr/bin/env python3
import asyncio
import logging
import os
import queue
import threading
from dotenv import load_dotenv
from google.cloud import speech
import websockets

load_dotenv(os.path.join('secrets', '.env'))

level_name = os.environ.get('LOG_LEVEL', 'INFO').upper()
level = getattr(logging, level_name, logging.INFO)
logging.basicConfig(level=level, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

PORT = int(os.environ.get('ASR_PORT', '9000'))

async def handle(websocket):
    logger.info('Client connected')
    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
        sample_rate_hertz=48000,
        language_code='ja-JP',
        audio_channel_count=1,
    )
    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=False,
    )

    q = queue.Queue()
    loop = asyncio.get_event_loop()

    def request_gen():
        while True:
            data = q.get()
            if data is None:
                break
            yield speech.StreamingRecognizeRequest(audio_content=data)

    async def reader():
        try:
            async for message in websocket:
                if isinstance(message, bytes):
                    logger.debug('Received %d bytes', len(message))
                    q.put(message)
                else:
                    if message == 'EOS':
                        logger.debug('Received EOS')
                        break
        finally:
            q.put(None)

    def process():
        try:
            responses = client.streaming_recognize(
                config=streaming_config,
                requests=request_gen(),
            )
            for response in responses:
                for result in response.results:
                    if not result.alternatives:
                        continue
                    text = result.alternatives[0].transcript
                    logger.info('Recognized: %s', text)
                    asyncio.run_coroutine_threadsafe(websocket.send(text), loop)
        except Exception as e:
            logger.exception('Recognition error: %s', e)
        


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

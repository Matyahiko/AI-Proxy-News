#!/usr/bin/env python3
import asyncio
import logging
import queue
import threading
from typing import AsyncGenerator
from google.cloud import speech
import websockets
from config import get_asr_port

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('realtime_asr.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

PORT = get_asr_port()

class RequestGenerator:
    """Handles audio data streaming for Speech-to-Text API."""
    
    def __init__(self):
        self.queue = queue.Queue()
        
    def add_audio_data(self, data: bytes) -> None:
        """Add audio data to the processing queue."""
        self.queue.put(data)
        
    def close(self) -> None:
        """Signal end of audio stream."""
        self.queue.put(None)
        
    def generate_requests(self) -> AsyncGenerator[speech.StreamingRecognizeRequest, None]:
        """Generate streaming recognition requests."""
        while True:
            data = self.queue.get()
            if data is None:
                break
            yield speech.StreamingRecognizeRequest(audio_content=data)


async def handle(websocket):
    """Handle WebSocket connection for realtime transcription."""
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

    request_gen = RequestGenerator()
    loop = asyncio.get_event_loop()

    async def read_websocket_messages():
        """Read messages from WebSocket and queue audio data."""
        try:
            async for message in websocket:
                if isinstance(message, bytes):
                    logger.debug(f"Received audio data: {len(message)} bytes")
                    request_gen.add_audio_data(message)
                elif message == 'EOS':
                    logger.info("Received EOS signal")
                    break
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            request_gen.close()

    def process_speech_recognition():
        """Process speech recognition in separate thread."""
        try:
            responses = client.streaming_recognize(
                config=streaming_config,
                requests=request_gen.generate_requests(),
            )
            for response in responses:
                for result in response.results:
                    if result.alternatives:
                        text = result.alternatives[0].transcript
                        asyncio.run_coroutine_threadsafe(
                            send_result_safely(websocket, text), loop
                        )
        except Exception as e:
            logger.error(f"Speech recognition error: {e}")

    recognition_thread = threading.Thread(target=process_speech_recognition, daemon=True)
    recognition_thread.start()
    
    await read_websocket_messages()
    recognition_thread.join(timeout=5.0)


async def send_result_safely(websocket, text: str):
    """Safely send transcription result to WebSocket."""
    try:
        await websocket.send(text)
    except websockets.exceptions.ConnectionClosed:
        pass

async def main():
    """Start the realtime ASR WebSocket server."""
    try:
        async with websockets.serve(handle, '0.0.0.0', PORT, max_size=None):
            logger.info(f'Realtime ASR server listening on ws://0.0.0.0:{PORT}')
            await asyncio.Future()
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == '__main__':
    asyncio.run(main())

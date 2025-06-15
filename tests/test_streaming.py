import queue
import sys
from pathlib import Path
import types

sys.path.append(str(Path(__file__).resolve().parent.parent))

fake_dotenv = types.ModuleType("dotenv")
fake_dotenv.load_dotenv = lambda *a, **k: None
sys.modules["dotenv"] = fake_dotenv
sys.modules.setdefault("google", types.ModuleType("google"))
cloud_mod = types.ModuleType("google.cloud")
sys.modules["google.cloud"] = cloud_mod
speech_mod = types.ModuleType("google.cloud.speech")
speech_mod.SpeechClient = object
speech_mod.RecognitionConfig = object
speech_mod.StreamingRecognitionConfig = object


class DummyReq:
    def __init__(self, streaming_config=None, audio_content=None):
        self.streaming_config = streaming_config
        self.audio_content = audio_content


speech_mod.StreamingRecognizeRequest = DummyReq
sys.modules["google.cloud.speech"] = speech_mod
cloud_mod.speech = speech_mod
api_core_mod = types.ModuleType("api_core.exceptions")
api_core_mod.GoogleAPICallError = Exception
sys.modules["google.api_core.exceptions"] = api_core_mod
sys.modules["websockets"] = types.ModuleType("websockets")
from scripts import realtime_server


def test_request_stream_yields_config_first():
    q = queue.Queue()
    streaming_config = object()
    gen = realtime_server.make_request_stream(q, streaming_config)
    first = next(gen)
    assert first.streaming_config is streaming_config
    q.put(b"abc")
    second = next(gen)
    assert second.audio_content == b"abc"
    q.put(None)
    try:
        next(gen)
    except StopIteration:
        pass

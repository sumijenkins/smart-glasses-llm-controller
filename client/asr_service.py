"""ASR (Speech-to-Text) service implementation using Whisper model."""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ASRService:
    """Automatic Speech Recognition service for Smart Glasses audio input."""

    def __init__(self, model_name: str = "tiny"):
        self.model_name = model_name
        self.whisper_model = None
        self._init_model()

    def _init_model(self):
        """Attempt loading whisper model or set mock mode."""
        try:
            import whisper
            logger.info(f"Loading Whisper model: '{self.model_name}'...")
            self.whisper_model = whisper.load_model(self.model_name)
            logger.info("Whisper model loaded successfully.")
        except ImportError:
            logger.warning("openai-whisper package not installed. ASR running in mock mode.")
        except Exception as e:
            logger.warning(f"Could not load Whisper model ({e}). ASR running in mock mode.")

    def transcribe_audio(self, audio_file_path: str) -> str:
        """Transcribe audio file to text."""
        if self.whisper_model:
            try:
                result = self.whisper_model.transcribe(audio_file_path, language="tr")
                text = result.get("text", "").strip()
                logger.info(f"ASR Transcribed Text: '{text}'")
                return text
            except Exception as e:
                logger.error(f"Whisper transcription failed: {e}")
                return "Kamerayı aç ve nesneyi tara"

        # Mock fallback transcription
        logger.info(f"[Mock ASR] Transcribing fake audio input from '{audio_file_path}'...")
        return "Kamerayı aç ve pil durumunu kontrol et"

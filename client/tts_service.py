"""TTS (Text-to-Speech) service implementation using pyttsx3."""
import logging

logger = logging.getLogger(__name__)


class TTSService:
    """Text to Speech engine for smart glasses audio response playback."""

    def __init__(self):
        self.engine = None
        self._init_engine()

    def _init_engine(self):
        """Initialize pyttsx3 text to speech engine."""
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            # Set speech rate and volume
            self.engine.setProperty("rate", 160)
            self.engine.setProperty("volume", 0.9)
            logger.info("pyttsx3 TTS engine initialized.")
        except Exception as e:
            logger.warning(f"pyttsx3 TTS engine initialization skipped ({e}). Console speech enabled.")

    def speak(self, text: str):
        """Speak the given text aloud or print to console."""
        logger.info(f"🔊 [TTS Speaking]: {text}")
        print(f"\n[🔊 Gözlük Sesli Yanıt]: {text}\n")
        
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                logger.error(f"TTS audio output error: {e}")

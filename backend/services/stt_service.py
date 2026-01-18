import logging
import os

logger = logging.getLogger("ai_avatar_backend.stt")

# Try to import whisper
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("OPENAI WHISPER not installed. STT will return mock text.")

class STTService:
    def __init__(self, model_size="base"):
        self.model = None
        if WHISPER_AVAILABLE:
            try:
                logger.info(f"Loading Whisper model: {model_size}...")
                self.model = whisper.load_model(model_size)
                logger.info("Whisper model loaded.")
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                
    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe audio file to text.
        """
        if self.model:
            result = self.model.transcribe(audio_path)
            text = result["text"]
            return text.strip()
        else:
            # Mock behavior
            logger.info("Returning mock transaction")
            return "I want to become a data scientist"

stt_service = STTService()

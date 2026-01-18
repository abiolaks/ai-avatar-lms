import logging
import os
import uuid
from gtts import gTTS

logger = logging.getLogger("ai_avatar_backend.tts")

class TTSService:
    def __init__(self):
        self.output_dir = "static/audio"
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_audio(self, text: str) -> str:
        """
        Generate audio from text using gTTS.
        Returns the relative path to the audio file.
        """
        logger.info(f"Generating TTS for: {text}")
        try:
            filename = f"{uuid.uuid4()}.mp3"
            filepath = os.path.join(self.output_dir, filename)
            
            tts = gTTS(text=text, lang='en')
            tts.save(filepath)
            
            return f"/static/audio/{filename}"
        except Exception as e:
            logger.error(f"TTS Generation failed: {e}")
            return ""

tts_service = TTSService()

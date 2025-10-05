"""
ElevenLabs Voice Integration (Setup but dormant until backend is stable)
"""

import os
from typing import Optional
import logging
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

logger = logging.getLogger(__name__)


class VoiceService:
    """
    ElevenLabs integration for text-to-speech and speech-to-text
    Currently configured but not actively used until backend is stable
    """

    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            logger.warning("ELEVENLABS_API_KEY not set - voice features will be unavailable")
            self.client = None
            self.enabled = False
            return

        try:
            self.client = ElevenLabs(api_key=self.api_key)
            self.enabled = True

            # Default voice ID - Using "Rachel" as a professional female voice
            # You can change this to any ElevenLabs voice ID
            self.default_voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

            # Voice settings for financial advisor persona
            self.voice_settings = VoiceSettings(
                stability=0.5,  # Moderate stability for natural variation
                similarity_boost=0.75,  # High similarity to selected voice
                style=0.5,  # Moderate style exaggeration
                use_speaker_boost=True
            )

            logger.info("ElevenLabs Voice Service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize ElevenLabs: {e}")
            self.client = None
            self.enabled = False

    async def text_to_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        model_id: str = "eleven_multilingual_v2"
    ) -> Optional[bytes]:
        """
        Convert text to speech using ElevenLabs

        Args:
            text: Text to convert to speech
            voice_id: Voice ID (defaults to Rachel)
            model_id: ElevenLabs model ID

        Returns:
            Audio bytes or None if disabled/error
        """
        if not self.enabled or not self.client:
            logger.warning("Voice service not enabled - skipping TTS")
            return None

        try:
            voice_id = voice_id or self.default_voice_id

            # Generate audio
            audio_generator = self.client.generate(
                text=text,
                voice=voice_id,
                model=model_id,
                voice_settings=self.voice_settings
            )

            # Collect audio bytes
            audio_bytes = b"".join(audio_generator)

            logger.info(f"Generated TTS audio: {len(audio_bytes)} bytes")
            return audio_bytes

        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return None

    async def speech_to_text(
        self,
        audio_data: bytes,
        language: str = "en"
    ) -> Optional[str]:
        """
        Convert speech to text

        Note: ElevenLabs primarily does TTS. For STT, you might want to use:
        - OpenAI Whisper API
        - Google Speech-to-Text
        - AssemblyAI

        This is a placeholder for future implementation.

        Args:
            audio_data: Audio bytes
            language: Language code

        Returns:
            Transcribed text or None
        """
        logger.warning("Speech-to-text not yet implemented - use OpenAI Whisper instead")
        return None

    def get_available_voices(self) -> Optional[list]:
        """
        Get list of available voices from ElevenLabs

        Returns:
            List of voice objects or None if disabled
        """
        if not self.enabled or not self.client:
            logger.warning("Voice service not enabled")
            return None

        try:
            voices = self.client.voices.get_all()
            return voices.voices

        except Exception as e:
            logger.error(f"Failed to fetch voices: {e}")
            return None

    def set_voice(self, voice_id: str):
        """
        Set the default voice ID

        Args:
            voice_id: ElevenLabs voice ID
        """
        self.default_voice_id = voice_id
        logger.info(f"Default voice changed to: {voice_id}")


# Global voice service instance (dormant until explicitly called)
voice_service = VoiceService()


# ============= OpenAI Whisper Integration for STT =============
# Since ElevenLabs doesn't do STT, here's a Whisper implementation

from openai import AsyncOpenAI
import io


class WhisperSTT:
    """OpenAI Whisper for Speech-to-Text"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not set - Whisper STT unavailable")
            self.client = None
            self.enabled = False
            return

        self.client = AsyncOpenAI(api_key=self.api_key)
        self.enabled = True
        logger.info("Whisper STT initialized")

    async def transcribe(
        self,
        audio_data: bytes,
        language: str = "en",
        prompt: Optional[str] = None
    ) -> Optional[str]:
        """
        Transcribe audio using Whisper

        Args:
            audio_data: Audio file bytes (mp3, wav, m4a, etc.)
            language: Language code (e.g., 'en', 'es')
            prompt: Optional context prompt

        Returns:
            Transcribed text or None
        """
        if not self.enabled or not self.client:
            logger.warning("Whisper STT not enabled")
            return None

        try:
            # Create file-like object from bytes
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.mp3"  # Required by API

            # Transcribe
            transcript = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language,
                prompt=prompt or "Financial conversation about budgeting and expenses"
            )

            logger.info(f"Transcribed audio: {len(transcript.text)} chars")
            return transcript.text

        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            return None


# Global Whisper instance
whisper_stt = WhisperSTT()


# ============= Complete Voice Pipeline =============

async def voice_chat_pipeline(audio_data: bytes) -> Optional[dict]:
    """
    Complete voice interaction pipeline:
    1. STT: Convert speech to text (Whisper)
    2. Process with AI
    3. TTS: Convert response to speech (ElevenLabs)

    Args:
        audio_data: Input audio bytes

    Returns:
        {
            "transcribed_text": str,
            "ai_response_text": str,
            "response_audio": bytes
        }
    """
    # Step 1: Speech to Text
    transcribed_text = await whisper_stt.transcribe(audio_data)
    if not transcribed_text:
        logger.error("STT failed")
        return None

    logger.info(f"User said: {transcribed_text}")

    # Step 2: Process with AI (placeholder - will be connected to AI service)
    # TODO: Connect to AI service's chat endpoint
    ai_response_text = "This is a placeholder response. Connect to AI service."

    # Step 3: Text to Speech
    response_audio = await voice_service.text_to_speech(ai_response_text)

    return {
        "transcribed_text": transcribed_text,
        "ai_response_text": ai_response_text,
        "response_audio": response_audio
    }

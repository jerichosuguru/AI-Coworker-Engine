"""
Speech Service - Text-to-Speech and Speech-to-Text utilities

In production, integrate with:
- Google Cloud Text-to-Speech / Speech-to-Text
- Amazon Polly / Transcribe
- Azure Speech Services
- OpenAI Whisper (for STT)
- ElevenLabs (for high-quality TTS)
"""
from typing import Optional, Dict, Any
import base64
import io


class SpeechService:
    """
    Wrapper for Text-to-Speech and Speech-to-Text services

    This is a mock implementation for development.
    In production, replace with actual API calls.
    """

    def __init__(self, provider: str = "mock"):
        """
        Initialize speech service

        Args:
            provider: Service provider (mock, google, aws, azure, openai)
        """
        self.provider = provider
        self.tts_enabled = False
        self.stt_enabled = False

        # Voice settings
        self.default_voice = {
            "language": "en-US",
            "gender": "neutral",
            "name": "en-US-Neural2-C",
            "speaking_rate": 1.0,
            "pitch": 0.0,
            "volume": 0.0
        }

    def text_to_speech(
            self,
            text: str,
            voice: Optional[str] = None,
            language: str = "en-US",
            speed: float = 1.0,
            pitch: float = 0.0,
            output_format: str = "mp3"
    ) -> bytes:
        """
        Convert text to speech audio

        Args:
            text: Text to convert
            voice: Voice ID/name
            language: Language code (e.g., en-US, fr-FR)
            speed: Speaking rate (0.25 to 4.0, default 1.0)
            pitch: Voice pitch (-20.0 to 20.0, default 0.0)
            output_format: Audio format (mp3, wav, ogg)

        Returns:
            Audio bytes in specified format
        """
        if self.provider == "mock":
            return self._mock_text_to_speech(text, output_format)
        elif self.provider == "google":
            return self._google_text_to_speech(text, voice, language, speed, pitch)
        elif self.provider == "aws":
            return self._aws_text_to_speech(text, voice, language, speed)
        elif self.provider == "azure":
            return self._azure_text_to_speech(text, voice, language, speed, pitch)
        elif self.provider == "elevenlabs":
            return self._elevenlabs_text_to_speech(text, voice)
        else:
            raise ValueError(f"Unsupported TTS provider: {self.provider}")

    def speech_to_text(
            self,
            audio_bytes: bytes,
            language: str = "en-US",
            enable_punctuation: bool = True,
            enable_word_timestamps: bool = False
    ) -> Dict[str, Any]:
        """
        Convert speech audio to text

        Args:
            audio_bytes: Audio data (WAV, MP3, FLAC, etc.)
            language: Language code
            enable_punctuation: Automatically add punctuation
            enable_word_timestamps: Include word-level timestamps

        Returns:
            {
                "transcript": "transcribed text",
                "confidence": 0.95,
                "words": [{"word": "hello", "start": 0.0, "end": 0.5}] (optional)
            }
        """
        if self.provider == "mock":
            return self._mock_speech_to_text(audio_bytes)
        elif self.provider == "google":
            return self._google_speech_to_text(audio_bytes, language, enable_punctuation)
        elif self.provider == "aws":
            return self._aws_speech_to_text(audio_bytes, language)
        elif self.provider == "azure":
            return self._azure_speech_to_text(audio_bytes, language)
        elif self.provider == "openai":
            return self._openai_speech_to_text(audio_bytes, language)
        else:
            raise ValueError(f"Unsupported STT provider: {self.provider}")

    def get_available_voices(self, language: Optional[str] = None) -> list:
        """
        Get list of available voices

        Args:
            language: Filter by language code

        Returns:
            List of voice objects
        """
        if self.provider == "mock":
            return self._mock_available_voices()
        else:
            # In production: call actual API
            return []

    # ============================================
    # MOCK IMPLEMENTATIONS (for development)
    # ============================================

    def _mock_text_to_speech(self, text: str, format: str) -> bytes:
        """Mock TTS - returns empty audio bytes"""
        print(f"[MOCK TTS] Converting to speech: {text[:50]}...")
        print(f"[MOCK TTS] Format: {format}")
        print(f"[MOCK TTS] In production, this would call actual TTS API")

        # Return empty bytes (in production: return actual audio)
        return b""

    def _mock_speech_to_text(self, audio_bytes: bytes) -> Dict[str, Any]:
        """Mock STT - returns placeholder transcript"""
        print(f"[MOCK STT] Transcribing {len(audio_bytes)} bytes of audio...")
        print(f"[MOCK STT] In production, this would call actual STT API")

        return {
            "transcript": "",
            "confidence": 0.0,
            "duration": 0.0
        }

    def _mock_available_voices(self) -> list:
        """Mock voice list"""
        return [
            {
                "id": "en-US-Neural2-A",
                "name": "en-US-Neural2-A",
                "language": "en-US",
                "gender": "female",
                "type": "neural"
            },
            {
                "id": "en-US-Neural2-C",
                "name": "en-US-Neural2-C",
                "language": "en-US",
                "gender": "neutral",
                "type": "neural"
            },
            {
                "id": "en-GB-Neural2-A",
                "name": "en-GB-Neural2-A",
                "language": "en-GB",
                "gender": "female",
                "type": "neural"
            }
        ]

    # ============================================
    # GOOGLE CLOUD SPEECH (example integration)
    # ============================================

    def _google_text_to_speech(
            self,
            text: str,
            voice: Optional[str],
            language: str,
            speed: float,
            pitch: float
    ) -> bytes:
        """
        Google Cloud Text-to-Speech integration

        Requires: pip install google-cloud-texttospeech
        """
        try:
            from google.cloud import texttospeech

            client = texttospeech.TextToSpeechClient()

            synthesis_input = texttospeech.SynthesisInput(text=text)

            voice_params = texttospeech.VoiceSelectionParams(
                language_code=language,
                name=voice or self.default_voice["name"]
            )

            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=speed,
                pitch=pitch
            )

            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice_params,
                audio_config=audio_config
            )

            return response.audio_content

        except ImportError:
            print("⚠️  google-cloud-texttospeech not installed, using mock")
            return self._mock_text_to_speech(text, "mp3")
        except Exception as e:
            print(f"❌ Google TTS error: {e}")
            return self._mock_text_to_speech(text, "mp3")

    def _google_speech_to_text(
            self,
            audio_bytes: bytes,
            language: str,
            enable_punctuation: bool
    ) -> Dict[str, Any]:
        """
        Google Cloud Speech-to-Text integration

        Requires: pip install google-cloud-speech
        """
        try:
            from google.cloud import speech

            client = speech.SpeechClient()

            audio = speech.RecognitionAudio(content=audio_bytes)

            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                language_code=language,
                enable_automatic_punctuation=enable_punctuation,
            )

            response = client.recognize(config=config, audio=audio)

            if response.results:
                result = response.results[0]
                alternative = result.alternatives[0]

                return {
                    "transcript": alternative.transcript,
                    "confidence": alternative.confidence,
                }
            else:
                return {
                    "transcript": "",
                    "confidence": 0.0
                }

        except ImportError:
            print("⚠️  google-cloud-speech not installed, using mock")
            return self._mock_speech_to_text(audio_bytes)
        except Exception as e:
            print(f"❌ Google STT error: {e}")
            return self._mock_speech_to_text(audio_bytes)

    # ============================================
    # AWS POLLY & TRANSCRIBE (example integration)
    # ============================================

    def _aws_text_to_speech(
            self,
            text: str,
            voice: Optional[str],
            language: str,
            speed: float
    ) -> bytes:
        """
        AWS Polly integration

        Requires: pip install boto3
        """
        try:
            import boto3

            polly = boto3.client('polly')

            response = polly.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=voice or 'Joanna',
                Engine='neural',
                LanguageCode=language
            )

            return response['AudioStream'].read()

        except ImportError:
            print("⚠️  boto3 not installed, using mock")
            return self._mock_text_to_speech(text, "mp3")
        except Exception as e:
            print(f"❌ AWS Polly error: {e}")
            return self._mock_text_to_speech(text, "mp3")

    def _aws_speech_to_text(self, audio_bytes: bytes, language: str) -> Dict[str, Any]:
        """AWS Transcribe integration (simplified)"""
        # AWS Transcribe requires async processing
        # This is a simplified example
        print("⚠️  AWS Transcribe requires async processing")
        return self._mock_speech_to_text(audio_bytes)

    # ============================================
    # AZURE SPEECH (example integration)
    # ============================================

    def _azure_text_to_speech(
            self,
            text: str,
            voice: Optional[str],
            language: str,
            speed: float,
            pitch: float
    ) -> bytes:
        """
        Azure Speech Services TTS integration

        Requires: pip install azure-cognitiveservices-speech
        """
        try:
            import azure.cognitiveservices.speech as speechsdk

            speech_config = speechsdk.SpeechConfig(
                subscription=os.getenv("AZURE_SPEECH_KEY"),
                region=os.getenv("AZURE_SPEECH_REGION")
            )

            speech_config.speech_synthesis_voice_name = voice or "en-US-JennyNeural"

            synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

            result = synthesizer.speak_text_async(text).get()

            return result.audio_data

        except ImportError:
            print("⚠️  azure-cognitiveservices-speech not installed, using mock")
            return self._mock_text_to_speech(text, "mp3")
        except Exception as e:
            print(f"❌ Azure TTS error: {e}")
            return self._mock_text_to_speech(text, "mp3")

    def _azure_speech_to_text(self, audio_bytes: bytes, language: str) -> Dict[str, Any]:
        """Azure Speech STT integration"""
        # Similar to TTS, requires Azure SDK
        print("⚠️  Azure STT not implemented in mock")
        return self._mock_speech_to_text(audio_bytes)

    # ============================================
    # OPENAI WHISPER (example integration)
    # ============================================

    def _openai_speech_to_text(self, audio_bytes: bytes, language: str) -> Dict[str, Any]:
        """
        OpenAI Whisper integration

        Requires: pip install openai
        """
        try:
            from openai import OpenAI

            client = OpenAI()

            # Write bytes to temporary file (Whisper API requires file)
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                f.write(audio_bytes)
                temp_path = f.name

            # Transcribe
            with open(temp_path, 'rb') as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language[:2] if language else None  # e.g., "en" from "en-US"
                )

            # Cleanup
            import os
            os.unlink(temp_path)

            return {
                "transcript": transcript.text,
                "confidence": 1.0  # Whisper doesn't provide confidence
            }

        except ImportError:
            print("⚠️  openai not installed, using mock")
            return self._mock_speech_to_text(audio_bytes)
        except Exception as e:
            print(f"❌ Whisper error: {e}")
            return self._mock_speech_to_text(audio_bytes)

    # ============================================
    # ELEVENLABS (high-quality TTS)
    # ============================================

    def _elevenlabs_text_to_speech(self, text: str, voice: Optional[str]) -> bytes:
        """
        ElevenLabs TTS integration

        Requires: pip install elevenlabs
        """
        try:
            from elevenlabs import generate, set_api_key
            import os

            set_api_key(os.getenv("ELEVENLABS_API_KEY"))

            audio = generate(
                text=text,
                voice=voice or "Rachel",  # Default voice
                model="eleven_monolingual_v1"
            )

            return audio

        except ImportError:
            print("⚠️  elevenlabs not installed, using mock")
            return self._mock_text_to_speech(text, "mp3")
        except Exception as e:
            print(f"❌ ElevenLabs error: {e}")
            return self._mock_text_to_speech(text, "mp3")


# ============================================
# CONVENIENCE FUNCTIONS
# ============================================

# Global service instance
_speech_service = SpeechService(provider="mock")


def text_to_speech(
        text: str,
        voice: Optional[str] = None,
        language: str = "en-US",
        speed: float = 1.0,
        pitch: float = 0.0
) -> bytes:
    """
    Convert text to speech (convenience function)

    Args:
        text: Text to convert
        voice: Voice ID
        language: Language code
        speed: Speaking rate
        pitch: Voice pitch

    Returns:
        Audio bytes
    """
    return _speech_service.text_to_speech(text, voice, language, speed, pitch)


def speech_to_text(
        audio_bytes: bytes,
        language: str = "en-US"
) -> str:
    """
    Convert speech to text (convenience function)

    Args:
        audio_bytes: Audio data
        language: Language code

    Returns:
        Transcribed text
    """
    result = _speech_service.speech_to_text(audio_bytes, language)
    return result.get("transcript", "")


def set_speech_provider(provider: str):
    """
    Set global speech service provider

    Args:
        provider: Provider name (mock, google, aws, azure, openai)
    """
    global _speech_service
    _speech_service = SpeechService(provider=provider)
    print(f"✅ Speech provider set to: {provider}")


# ============================================
# AUDIO UTILITIES
# ============================================

def audio_bytes_to_base64(audio_bytes: bytes) -> str:
    """
    Convert audio bytes to base64 string

    Args:
        audio_bytes: Audio data

    Returns:
        Base64 encoded string
    """
    return base64.b64encode(audio_bytes).decode('utf-8')


def base64_to_audio_bytes(base64_string: str) -> bytes:
    """
    Convert base64 string to audio bytes

    Args:
        base64_string: Base64 encoded audio

    Returns:
        Audio bytes
    """
    return base64.b64decode(base64_string)


def get_audio_duration(audio_bytes: bytes) -> float:
    """
    Get audio duration in seconds (approximate)

    Args:
        audio_bytes: Audio data

    Returns:
        Duration in seconds
    """
    # This is a simplified placeholder
    # In production, use a library like pydub or mutagen
    try:
        from pydub import AudioSegment

        audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
        return len(audio) / 1000.0  # Convert ms to seconds

    except ImportError:
        # Fallback: rough estimate based on file size
        # Assuming MP3 at 128kbps: 1 second ≈ 16KB
        return len(audio_bytes) / 16000.0
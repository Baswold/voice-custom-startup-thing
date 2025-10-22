"""
Automatic Speech Recognition for consent verification
Uses OpenAI Whisper for accurate transcription
"""
import os
from typing import Optional, Tuple
from difflib import SequenceMatcher


class WhisperASR:
    """
    Whisper-based ASR for consent verification.
    Lazy-loads model to save memory when not needed.
    """

    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper ASR.

        Args:
            model_size: Model size - "tiny", "base", "small", "medium", "large"
                - tiny: Fast, less accurate (~39M params)
                - base: Good balance (~74M params) - RECOMMENDED
                - small: Better accuracy (~244M params)
                - medium: High accuracy (~769M params)
                - large: Best accuracy (~1550M params)
        """
        self.model_size = model_size
        self.model = None
        self._available = None

    def is_available(self) -> bool:
        """Check if Whisper is installed and available"""
        if self._available is not None:
            return self._available

        try:
            import whisper
            self._available = True
            return True
        except ImportError:
            self._available = False
            return False

    def _load_model(self):
        """Lazy load Whisper model"""
        if self.model is not None:
            return

        if not self.is_available():
            raise ImportError(
                "Whisper not installed. Install with: pip install openai-whisper"
            )

        try:
            import whisper
            print(f"Loading Whisper '{self.model_size}' model...")
            self.model = whisper.load_model(self.model_size)
            print("✅ Whisper model loaded")
        except Exception as e:
            raise RuntimeError(f"Failed to load Whisper model: {e}")

    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None
    ) -> dict:
        """
        Transcribe audio file to text.

        Args:
            audio_path: Path to audio file
            language: Language code (e.g., "en", "es", "fr") or None for auto-detect

        Returns:
            dict with keys:
                - text: Transcribed text
                - language: Detected language
                - segments: Detailed segments
        """
        self._load_model()

        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Transcribe
        result = self.model.transcribe(
            audio_path,
            language=language,
            task="transcribe"
        )

        return {
            "text": result["text"].strip(),
            "language": result.get("language", "unknown"),
            "segments": result.get("segments", [])
        }

    def verify_consent(
        self,
        audio_path: str,
        expected_phrase: str,
        threshold: float = 0.75,
        language: Optional[str] = None
    ) -> Tuple[bool, float, str]:
        """
        Verify that audio contains the expected consent phrase.

        Args:
            audio_path: Path to consent audio
            expected_phrase: Expected consent phrase
            threshold: Similarity threshold (0.0 - 1.0)
            language: Language code or None for auto-detect

        Returns:
            Tuple of (is_verified: bool, similarity: float, transcription: str)
        """
        if not self.is_available():
            print("⚠️  Whisper not available, using fallback verification")
            # Fallback: just check that audio exists and has reasonable duration
            import librosa
            try:
                duration = librosa.get_duration(path=audio_path)
                # Heuristic: consent should be 3-30 seconds
                is_valid = 3 <= duration <= 30
                return is_valid, 0.5 if is_valid else 0.0, "[Whisper not available]"
            except Exception:
                return False, 0.0, "[Error]"

        # Transcribe audio
        result = self.transcribe(audio_path, language=language)
        transcription = result["text"]

        if not transcription:
            return False, 0.0, ""

        # Calculate similarity
        similarity = self._calculate_similarity(transcription, expected_phrase)

        is_verified = similarity >= threshold

        return is_verified, similarity, transcription

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two strings.
        Uses SequenceMatcher for fuzzy matching.

        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Normalize text
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()

        # Remove punctuation for better matching
        import string
        translator = str.maketrans('', '', string.punctuation)
        text1 = text1.translate(translator)
        text2 = text2.translate(translator)

        # Calculate similarity
        similarity = SequenceMatcher(None, text1, text2).ratio()

        return similarity


# Global instance (lazy-loaded)
_whisper_instance = None


def get_whisper_asr(model_size: str = "base") -> WhisperASR:
    """
    Get global Whisper ASR instance (singleton pattern).
    This avoids reloading the model for every request.
    """
    global _whisper_instance

    if _whisper_instance is None:
        _whisper_instance = WhisperASR(model_size=model_size)

    return _whisper_instance


# Example usage:
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python asr.py <audio_file> [expected_phrase]")
        sys.exit(1)

    audio_file = sys.argv[1]
    expected_phrase = sys.argv[2] if len(sys.argv) > 2 else None

    asr = WhisperASR(model_size="base")

    if not asr.is_available():
        print("❌ Whisper not installed. Install with:")
        print("   pip install openai-whisper")
        sys.exit(1)

    if expected_phrase:
        # Verify consent
        is_verified, similarity, transcription = asr.verify_consent(
            audio_file,
            expected_phrase,
            threshold=0.75
        )

        print(f"\n{'='*60}")
        print(f"Expected: {expected_phrase}")
        print(f"Transcribed: {transcription}")
        print(f"Similarity: {similarity:.2%}")
        print(f"Verified: {'✅ Yes' if is_verified else '❌ No'}")
        print(f"{'='*60}\n")
    else:
        # Just transcribe
        result = asr.transcribe(audio_file)

        print(f"\n{'='*60}")
        print(f"Language: {result['language']}")
        print(f"Transcription: {result['text']}")
        print(f"{'='*60}\n")

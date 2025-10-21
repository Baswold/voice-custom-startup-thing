"""
Test cases for utility functions
"""
import pytest
import numpy as np
import tempfile
import os
from app.api.utils import (
    get_audio_duration,
    load_audio,
    save_audio,
    normalize_audio,
    trim_silence,
    compute_audio_hash,
    validate_audio_quality
)


@pytest.fixture
def sample_audio():
    """Generate a sample audio signal for testing"""
    # Generate 2 seconds of 440Hz sine wave (A4 note)
    sample_rate = 22050
    duration = 2.0
    frequency = 440.0

    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = 0.5 * np.sin(2 * np.pi * frequency * t)

    return audio.astype(np.float32), sample_rate


@pytest.fixture
def audio_file(sample_audio):
    """Create a temporary audio file for testing"""
    audio, sr = sample_audio

    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        temp_path = f.name

    save_audio(temp_path, audio, sr)

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)


class TestAudioUtils:
    """Test audio utility functions"""

    def test_save_and_load_audio(self, sample_audio):
        """Test saving and loading audio"""
        audio, sr = sample_audio

        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            temp_path = f.name

        try:
            # Save audio
            save_audio(temp_path, audio, sr)
            assert os.path.exists(temp_path)

            # Load audio
            loaded_audio, loaded_sr = load_audio(temp_path, target_sr=sr)

            # Check that loaded audio matches original
            assert loaded_sr == sr
            assert len(loaded_audio) > 0
            assert loaded_audio.dtype == np.float32

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_get_audio_duration(self, audio_file):
        """Test getting audio duration"""
        duration = get_audio_duration(audio_file)

        # Should be approximately 2 seconds
        assert 1.9 < duration < 2.1

    def test_normalize_audio(self, sample_audio):
        """Test audio normalization"""
        audio, _ = sample_audio

        # Normalize to -20 dB
        normalized = normalize_audio(audio, target_level=-20.0)

        # Check that audio was normalized
        assert len(normalized) == len(audio)
        assert np.max(np.abs(normalized)) <= 1.0  # No clipping

        # Check RMS level is close to target
        rms = np.sqrt(np.mean(normalized ** 2))
        target_rms = 10 ** (-20.0 / 20.0)
        assert abs(rms - target_rms) < 0.01

    def test_trim_silence(self, sample_audio):
        """Test silence trimming"""
        audio, sr = sample_audio

        # Add silence to beginning and end
        silence = np.zeros(sr // 2)  # 0.5 seconds of silence
        audio_with_silence = np.concatenate([silence, audio, silence])

        # Trim silence
        trimmed = trim_silence(audio_with_silence, sr, top_db=30)

        # Trimmed audio should be shorter than original
        assert len(trimmed) < len(audio_with_silence)
        assert len(trimmed) > 0

    def test_compute_audio_hash(self, audio_file):
        """Test audio file hashing"""
        hash1 = compute_audio_hash(audio_file)

        # Hash should be consistent
        hash2 = compute_audio_hash(audio_file)
        assert hash1 == hash2

        # Hash should be SHA-256 (64 hex characters)
        assert len(hash1) == 64
        assert all(c in '0123456789abcdef' for c in hash1)

    def test_validate_audio_quality(self, audio_file):
        """Test audio quality validation"""
        validation = validate_audio_quality(audio_file, min_duration=1.0)

        assert isinstance(validation, dict)
        assert "valid" in validation
        assert "duration" in validation
        assert "sample_rate" in validation
        assert "rms_level" in validation
        assert "peak_level" in validation
        assert "issues" in validation

        # Should be valid since it's a clean 2-second audio
        assert validation["valid"] is True
        assert validation["duration"] > 1.0

    def test_validate_audio_too_short(self):
        """Test validation fails for too short audio"""
        # Create very short audio
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, 0.5, 11025))  # 0.5 seconds

        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            temp_path = f.name

        try:
            save_audio(temp_path, audio, 22050)

            validation = validate_audio_quality(temp_path, min_duration=6.0)

            assert validation["valid"] is False
            assert len(validation["issues"]) > 0
            assert any("too short" in issue.lower() for issue in validation["issues"])

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_validate_audio_too_quiet(self):
        """Test validation fails for too quiet audio"""
        # Create very quiet audio
        audio = 0.001 * np.sin(2 * np.pi * 440 * np.linspace(0, 2, 44100))

        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            temp_path = f.name

        try:
            save_audio(temp_path, audio, 22050)

            validation = validate_audio_quality(temp_path, min_duration=1.0)

            assert validation["valid"] is False
            assert any("too low" in issue.lower() for issue in validation["issues"])

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

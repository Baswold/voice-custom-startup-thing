"""
Utility functions for audio processing and file handling
"""
import os
import wave
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
import librosa
import soundfile as sf
import numpy as np


def get_audio_duration(file_path: str) -> float:
    """
    Get duration of audio file in seconds.
    Supports WAV, MP3, FLAC, OGG, etc.
    """
    try:
        # Use librosa for broad format support
        duration = librosa.get_duration(path=file_path)
        return duration
    except Exception as e:
        # Fallback to wave module for WAV files
        try:
            with wave.open(file_path, 'rb') as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                duration = frames / float(rate)
                return duration
        except Exception:
            raise ValueError(f"Unable to determine audio duration: {e}")


def load_audio(file_path: str, target_sr: int = 22050) -> tuple:
    """
    Load audio file and return waveform and sample rate.
    Automatically resamples to target_sr.
    """
    audio, sr = librosa.load(file_path, sr=target_sr)
    return audio, sr


def save_audio(file_path: str, audio: np.ndarray, sample_rate: int = 22050):
    """Save audio waveform to file"""
    sf.write(file_path, audio, sample_rate)


def normalize_audio(audio: np.ndarray, target_level: float = -20.0) -> np.ndarray:
    """
    Normalize audio to target RMS level in dB.
    Prevents clipping and ensures consistent volume.
    """
    # Calculate current RMS
    rms = np.sqrt(np.mean(audio ** 2))

    if rms == 0:
        return audio

    # Convert target level from dB to linear
    target_rms = 10 ** (target_level / 20.0)

    # Scale audio
    normalized = audio * (target_rms / rms)

    # Prevent clipping
    max_val = np.max(np.abs(normalized))
    if max_val > 1.0:
        normalized = normalized / max_val * 0.99

    return normalized


def trim_silence(
    audio: np.ndarray,
    sample_rate: int,
    top_db: int = 30,
    frame_length: int = 2048,
    hop_length: int = 512
) -> np.ndarray:
    """
    Trim leading and trailing silence from audio.
    """
    trimmed, _ = librosa.effects.trim(
        audio,
        top_db=top_db,
        frame_length=frame_length,
        hop_length=hop_length
    )
    return trimmed


def convert_to_wav(input_path: str, output_path: str, sample_rate: int = 22050) -> str:
    """
    Convert any audio format to WAV.
    Returns output path.
    """
    audio, sr = load_audio(input_path, target_sr=sample_rate)
    save_audio(output_path, audio, sample_rate)
    return output_path


def compute_audio_hash(file_path: str) -> str:
    """
    Compute SHA-256 hash of audio file for integrity verification.
    """
    sha256_hash = hashlib.sha256()

    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    return sha256_hash.hexdigest()


def embed_watermark_metadata(audio_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Embed watermark metadata into audio file.
    For WAV files, this writes to a sidecar JSON file.
    For production, implement actual audio watermarking (e.g., LSB or spectral).
    """
    # Create watermark metadata
    watermark = {
        "creator": metadata.get("creator", "unknown"),
        "created_at": metadata.get("created_at", datetime.utcnow().isoformat()),
        "voice_profile_id": metadata.get("voice_profile_id"),
        "license": metadata.get("license", "private"),
        "platform": "EchoForge",
        "version": "0.1.0",
        "checksum": compute_audio_hash(audio_path)
    }

    # Save watermark to sidecar file
    watermark_path = audio_path.replace(".wav", "_watermark.json")
    with open(watermark_path, "w") as f:
        json.dump(watermark, f, indent=2)

    return watermark


def verify_watermark(audio_path: str) -> Optional[Dict[str, Any]]:
    """
    Verify and read watermark metadata from audio file.
    """
    watermark_path = audio_path.replace(".wav", "_watermark.json")

    if not os.path.exists(watermark_path):
        return None

    with open(watermark_path, "r") as f:
        watermark = json.load(f)

    # Verify checksum
    current_hash = compute_audio_hash(audio_path)
    if current_hash != watermark.get("checksum"):
        raise ValueError("Audio file has been modified - checksum mismatch")

    return watermark


def split_audio_chunks(
    audio: np.ndarray,
    sample_rate: int,
    chunk_duration: float = 10.0
) -> list:
    """
    Split audio into chunks of specified duration.
    Useful for processing long recordings.
    """
    chunk_samples = int(chunk_duration * sample_rate)
    chunks = []

    for i in range(0, len(audio), chunk_samples):
        chunk = audio[i:i + chunk_samples]
        if len(chunk) > sample_rate:  # Skip chunks shorter than 1 second
            chunks.append(chunk)

    return chunks


def validate_audio_quality(audio_path: str, min_duration: float = 6.0) -> Dict[str, Any]:
    """
    Validate audio quality and return metrics.
    """
    audio, sr = load_audio(audio_path)
    duration = len(audio) / sr

    # Calculate signal metrics
    rms = np.sqrt(np.mean(audio ** 2))
    peak = np.max(np.abs(audio))
    snr_estimate = 20 * np.log10(rms / (peak - rms + 1e-10)) if rms > 0 else -np.inf

    validation = {
        "valid": True,
        "duration": duration,
        "sample_rate": sr,
        "rms_level": float(rms),
        "peak_level": float(peak),
        "snr_estimate_db": float(snr_estimate),
        "issues": []
    }

    # Check duration
    if duration < min_duration:
        validation["valid"] = False
        validation["issues"].append(f"Audio too short: {duration:.1f}s (minimum: {min_duration}s)")

    # Check if audio is too quiet
    if rms < 0.01:
        validation["valid"] = False
        validation["issues"].append("Audio level too low - please record louder")

    # Check for clipping
    if peak > 0.99:
        validation["issues"].append("Audio may be clipping - reduce input volume")

    # Check for silence
    non_silent = np.sum(np.abs(audio) > 0.01)
    silence_ratio = 1.0 - (non_silent / len(audio))
    if silence_ratio > 0.5:
        validation["issues"].append(f"Audio contains {silence_ratio*100:.0f}% silence")

    return validation

#!/usr/bin/env python3
"""
EchoForge Local CLI Synthesizer
Your voice, your device - completely offline.

Usage:
    python synthesize.py "Hello world" --voice my_voice --output speech.wav
    python synthesize.py "Hello world" -v my_voice -o speech.wav -s 1.2
"""

import argparse
import os
import sys
import json
from pathlib import Path
from typing import Optional
import torch
import torchaudio
import numpy as np


class LocalSynthesizer:
    """
    Local voice synthesis engine using pre-cloned voice models.
    Runs completely offline with no internet connection required.
    """

    def __init__(self, voices_dir: str = "./voices"):
        self.voices_dir = Path(voices_dir)
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"

        print(f"🎤 EchoForge Local Synthesizer")
        print(f"📍 Device: {self.device}")
        print(f"📁 Voices directory: {self.voices_dir}")

    def _load_model(self):
        """Lazy load TTS model"""
        if self.model is not None:
            return

        print("⏳ Loading TTS model...")
        try:
            from TTS.api import TTS
            self.model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)
            print("✅ Model loaded")
        except ImportError:
            print("❌ TTS library not installed. Install with: pip install TTS")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            sys.exit(1)

    def list_voices(self):
        """List all available voice profiles"""
        if not self.voices_dir.exists():
            print(f"❌ Voices directory not found: {self.voices_dir}")
            return []

        voices = []
        for voice_dir in self.voices_dir.iterdir():
            if voice_dir.is_dir():
                manifest_path = voice_dir / "manifest.json"
                if manifest_path.exists():
                    with open(manifest_path, 'r') as f:
                        manifest = json.load(f)
                        voices.append({
                            'name': voice_dir.name,
                            'manifest': manifest
                        })

        return voices

    def get_voice_path(self, voice_name: str) -> Optional[Path]:
        """Get the reference audio path for a voice"""
        voice_dir = self.voices_dir / voice_name
        if not voice_dir.exists():
            return None

        manifest_path = voice_dir / "manifest.json"
        if not manifest_path.exists():
            return None

        with open(manifest_path, 'r') as f:
            manifest = json.load(f)

        reference_audio = voice_dir / manifest.get('reference_audio', 'reference.wav')
        if not reference_audio.exists():
            return None

        return reference_audio

    def synthesize(
        self,
        text: str,
        voice_name: str,
        output_path: str,
        language: str = "en",
        speed: float = 1.0
    ):
        """
        Synthesize speech from text using a voice profile.

        Args:
            text: Text to synthesize
            voice_name: Name of the voice profile
            output_path: Path to save the output audio
            language: Language code (en, es, fr, etc.)
            speed: Speech speed multiplier (0.5 - 2.0)
        """
        print(f"\n🎵 Synthesizing: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        print(f"🎤 Voice: {voice_name}")
        print(f"🌍 Language: {language}")
        print(f"⚡ Speed: {speed}x")

        # Get voice path
        voice_path = self.get_voice_path(voice_name)
        if voice_path is None:
            print(f"❌ Voice not found: {voice_name}")
            print(f"\nAvailable voices:")
            for voice in self.list_voices():
                print(f"  - {voice['name']}")
            sys.exit(1)

        # Load model
        self._load_model()

        # Synthesize
        try:
            print("⏳ Generating speech...")

            self.model.tts_to_file(
                text=text,
                speaker_wav=str(voice_path),
                language=language,
                file_path=output_path,
                speed=speed
            )

            # Verify output
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / 1024  # KB
                print(f"✅ Success! Audio saved to: {output_path}")
                print(f"📦 File size: {file_size:.1f} KB")

                # Get duration
                audio, sr = torchaudio.load(output_path)
                duration = audio.shape[1] / sr
                print(f"⏱️  Duration: {duration:.2f}s")
            else:
                print("❌ Failed to generate audio")
                sys.exit(1)

        except Exception as e:
            print(f"❌ Synthesis failed: {e}")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="EchoForge Local Voice Synthesizer - Your voice, your device.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python synthesize.py "Hello world" --voice my_voice --output hello.wav

  # With speed control
  python synthesize.py "Fast speech" -v my_voice -o fast.wav -s 1.5

  # Different language
  python synthesize.py "Bonjour le monde" -v my_voice -o french.wav -l fr

  # List available voices
  python synthesize.py --list-voices
        """
    )

    parser.add_argument(
        'text',
        nargs='?',
        help='Text to synthesize'
    )

    parser.add_argument(
        '-v', '--voice',
        required=False,
        help='Voice profile name'
    )

    parser.add_argument(
        '-o', '--output',
        default='output.wav',
        help='Output audio file path (default: output.wav)'
    )

    parser.add_argument(
        '-l', '--language',
        default='en',
        help='Language code (default: en)'
    )

    parser.add_argument(
        '-s', '--speed',
        type=float,
        default=1.0,
        help='Speech speed multiplier (0.5 - 2.0, default: 1.0)'
    )

    parser.add_argument(
        '--voices-dir',
        default='./voices',
        help='Directory containing voice profiles (default: ./voices)'
    )

    parser.add_argument(
        '--list-voices',
        action='store_true',
        help='List all available voice profiles'
    )

    args = parser.parse_args()

    synthesizer = LocalSynthesizer(voices_dir=args.voices_dir)

    # List voices mode
    if args.list_voices:
        print("\n📋 Available Voices:\n")
        voices = synthesizer.list_voices()

        if not voices:
            print("No voices found. Add voice profiles to the voices directory.")
            print(f"Expected structure: {args.voices_dir}/voice_name/manifest.json")
            sys.exit(0)

        for voice in voices:
            manifest = voice['manifest']
            print(f"  🎤 {voice['name']}")
            print(f"     Language: {manifest.get('language', 'unknown')}")
            print(f"     Created: {manifest.get('created_at', 'unknown')}")
            if manifest.get('description'):
                print(f"     Description: {manifest['description']}")
            print()

        sys.exit(0)

    # Synthesis mode
    if not args.text:
        parser.error("Text is required for synthesis. Use --list-voices to see available voices.")

    if not args.voice:
        parser.error("Voice profile is required. Use --list-voices to see available voices.")

    # Validate speed
    if args.speed < 0.5 or args.speed > 2.0:
        parser.error("Speed must be between 0.5 and 2.0")

    # Synthesize
    synthesizer.synthesize(
        text=args.text,
        voice_name=args.voice,
        output_path=args.output,
        language=args.language,
        speed=args.speed
    )


if __name__ == "__main__":
    main()

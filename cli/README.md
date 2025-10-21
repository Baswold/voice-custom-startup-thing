# EchoForge Local CLI Synthesizer

**Completely offline text-to-speech using your cloned voices.**

## Features

- 🔒 **Privacy-First**: Runs 100% offline, no internet required
- 🎤 **Your Voice**: Use voice profiles cloned from the EchoForge platform
- ⚡ **Fast**: Optimized for local inference
- 🌍 **Multilingual**: Supports 15+ languages
- 🎚️ **Customizable**: Control speech speed and language

## Installation

```bash
# Install dependencies
pip install TTS torch torchaudio numpy

# Make CLI executable
chmod +x synthesize.py
```

## Quick Start

### 1. Download Your Voice Profile

After cloning your voice on the EchoForge platform, download your voice profile package and extract it to the `voices/` directory:

```
cli/
  voices/
    my_voice/
      reference.wav
      manifest.json
```

### 2. List Available Voices

```bash
python synthesize.py --list-voices
```

### 3. Synthesize Speech

```bash
python synthesize.py "Hello, world!" --voice my_voice --output hello.wav
```

## Usage Examples

### Basic Synthesis

```bash
python synthesize.py "Welcome to EchoForge" -v my_voice -o welcome.wav
```

### Adjust Speed

```bash
# Slower (0.5x - 2.0x)
python synthesize.py "Speak slowly" -v my_voice -o slow.wav -s 0.7

# Faster
python synthesize.py "Speak quickly" -v my_voice -o fast.wav -s 1.5
```

### Different Languages

```bash
# Spanish
python synthesize.py "Hola mundo" -v my_voice -o spanish.wav -l es

# French
python synthesize.py "Bonjour le monde" -v my_voice -o french.wav -l fr

# German
python synthesize.py "Hallo Welt" -v my_voice -o german.wav -l de
```

### Long Text from File

```bash
python synthesize.py "$(cat story.txt)" -v my_voice -o audiobook.wav
```

## Voice Profile Structure

Each voice profile should have this structure:

```
voices/
  my_voice_name/
    reference.wav          # Reference audio for voice cloning
    manifest.json          # Metadata and configuration
```

### manifest.json Example

```json
{
  "name": "My Professional Voice",
  "language": "en",
  "description": "My professional narration voice",
  "created_at": "2024-01-15T10:30:00Z",
  "creator": "user_123",
  "platform": "EchoForge",
  "version": "0.1.0",
  "reference_audio": "reference.wav",
  "license": "private",
  "watermark": {
    "enabled": true,
    "creator_id": "user_123"
  }
}
```

## Supported Languages

- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Polish (pl)
- Turkish (tr)
- Russian (ru)
- Dutch (nl)
- Czech (cs)
- Arabic (ar)
- Chinese (zh)
- Japanese (ja)
- Korean (ko)
- Hindi (hi)

## Command Reference

```bash
python synthesize.py [text] [options]

Required:
  text                   Text to synthesize

Options:
  -v, --voice NAME       Voice profile name (required)
  -o, --output FILE      Output file path (default: output.wav)
  -l, --language CODE    Language code (default: en)
  -s, --speed FLOAT      Speech speed (0.5 - 2.0, default: 1.0)
  --voices-dir DIR       Voices directory (default: ./voices)
  --list-voices          List all available voices
  -h, --help             Show help message
```

## Performance Tips

### For Faster Synthesis

1. **Use GPU**: If you have an NVIDIA GPU, the tool will automatically use CUDA
2. **Shorter text**: Break long texts into chunks
3. **Simpler models**: Consider using faster TTS models for real-time needs

### For Better Quality

1. **High-quality reference audio**: Use clean, well-recorded reference audio
2. **Appropriate speed**: Keep speed between 0.8x - 1.2x for natural results
3. **Proper language selection**: Always specify the correct language code

## Troubleshooting

### "Voice not found" error

Make sure your voice profile is in the `voices/` directory with the correct structure.

```bash
python synthesize.py --list-voices
```

### "Model failed to load" error

Install required dependencies:

```bash
pip install --upgrade TTS torch torchaudio
```

### Poor audio quality

1. Check that your reference audio is high quality (no background noise)
2. Use the original language of the reference audio
3. Avoid extreme speed settings

### Slow synthesis

1. Check if GPU is being used (will show in startup message)
2. For Apple Silicon: MPS acceleration should be automatic
3. For CPU-only: Consider using a lighter TTS model

## Privacy & Ethics

The CLI tool:

- ✅ Runs completely offline
- ✅ Preserves voice watermarking metadata
- ✅ Respects voice licensing terms
- ✅ Includes creator attribution

**Important**: Only use voices you have permission to use. Respect consent and licensing terms.

## License

This CLI tool is part of the EchoForge platform.
Voice profiles may have their own licenses - check `manifest.json` for details.

## Support

For issues or questions:
- Platform: https://echoforge.local
- Documentation: https://docs.echoforge.local
- Issues: https://github.com/echoforge/cli/issues

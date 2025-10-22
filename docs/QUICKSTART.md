# EchoForge Quick Start Guide

Get started with voice cloning in 5 minutes!

---

## 🚀 5-Minute Setup

### Step 1: Install (2-3 minutes)

```bash
# Clone and enter directory
git clone https://github.com/yourusername/echoforge.git
cd echoforge

# Run one-command installation
./install-mac.sh
```

Wait for installation to complete. Grab a coffee ☕

### Step 2: Start the Server (30 seconds)

```bash
./start-all.sh
```

You should see:
```
🚀 Starting EchoForge...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  EchoForge is running!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Frontend: http://localhost:3000
  Backend:  http://localhost:8000
  API Docs: http://localhost:8000/docs
```

### Step 3: Open Your Browser (5 seconds)

Open: **http://localhost:3000**

---

## 🎤 Clone Your First Voice (2-3 minutes)

### 1. Create an Account

- Click "Sign up"
- Enter email, username, and password
- Click "Create Account"

### 2. Clone Your Voice

Click "Clone Voice" and follow the wizard:

**Step 1: Voice Info**
- Name: "My Voice"
- Description: "My personal voice"
- Language: English
- Click "Continue"

**Step 2: Select Model**
- Choose "XTTS v2" (recommended)
- Click "Continue"

**Step 3: Record Your Voice**
- Click "🎤 Start Recording"
- Read naturally for 10-20 seconds
  - Example: "Hello, this is my voice. I'm creating an AI clone of my voice using EchoForge. This is exciting! I can speak in any language and say anything I want."
- Click "⏹ Stop Recording"
- Click "Continue"

**Step 4: Consent**
- Select a consent phrase
- Click "🎤 Start Recording"
- Read the consent phrase exactly
- Click "⏹ Stop Recording"
- Click "Create Voice Profile"

### 3. Wait for Processing (1-2 minutes)

The system will:
- Validate audio quality ✓
- Verify consent ✓
- Process voice embedding ✓
- Create voice profile ✓

---

## 🗣️ Generate Your First Speech (30 seconds)

### 1. Go to Synthesize Tab

- Click "Synthesize" in navigation

### 2. Select Your Voice

- Your voice should appear in the left sidebar
- Click on it

### 3. Enter Text

```
Welcome to EchoForge! This is my AI-cloned voice speaking.
```

### 4. Generate

- Click "🎵 Generate Speech"
- Wait 10-15 seconds
- Listen to the result!
- Download the audio file

---

## 🖥️ Use the CLI Tool (Offline Mode)

### First: Download Your Voice Profile

The web interface should provide a download button for your voice profile. Save it to `cli/voices/my_voice/`.

### Then: Synthesize Offline

```bash
# List available voices
./cli/synthesize.py --list-voices

# Generate speech
./cli/synthesize.py "Hello world!" --voice my_voice --output hello.wav

# Play the result (macOS)
afplay hello.wav
```

---

## 🎯 Quick Tips

### For Best Voice Quality

1. **Use a good microphone** (built-in Mac mic works too)
2. **Record in a quiet room** (no background noise)
3. **Speak naturally** (vary your intonation)
4. **Record 15-30 seconds** (more data = better quality)
5. **Use XTTS v2 model** (best quality)

### For Fastest Synthesis

1. **Use Glow-TTS or Tacotron 2** models
2. **Keep text under 100 words**
3. **Stick to one language**

### Recording Environment

✅ **Good:**
- Quiet room
- Close to mic (6-12 inches)
- Natural speech
- Varied intonation
- Good energy level

❌ **Avoid:**
- Background music
- Echo/reverb
- Monotone voice
- Whispering or shouting
- Wind noise

---

## 🔧 Common Issues

### "Port already in use"

```bash
# Kill existing processes
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9

# Restart
./start-all.sh
```

### "Dependencies not installed"

```bash
# Re-run installation
./install-mac.sh
```

### "Voice quality is poor"

- Re-record with better audio
- Use longer recording (20-30 seconds)
- Reduce background noise
- Speak more expressively

### "Synthesis is slow"

- This is normal! Quality takes time
- XTTS v2: ~15-30 seconds for 10s of audio
- Try faster models for real-time needs

---

## 📊 What's Next?

### Explore Features

- **Try different models**: Compare quality and speed
- **Multiple languages**: Clone your voice in different languages
- **Adjust speed**: Experiment with speech rate (0.5x - 2.0x)
- **Create multiple voices**: Clone different characters or styles

### Advanced Usage

- **CLI automation**: Batch process text files
- **API integration**: Build apps using the REST API
- **Voice library**: Share your voices (coming soon)
- **Fine-tuning**: Enhanced quality for specific use cases (coming soon)

### Read the Docs

- **Full README**: `/README.md`
- **Deployment Guide**: `/docs/DEPLOYMENT.md`
- **API Documentation**: http://localhost:8000/docs
- **CLI Guide**: `/cli/README.md`

---

## 🎬 Example Workflow

Here's a complete workflow from zero to deployed voice:

```bash
# 1. Install
./install-mac.sh

# 2. Start server
./start-all.sh

# 3. Open browser
open http://localhost:3000

# 4. Create account + clone voice (via web UI)
# ... use web interface ...

# 5. Test synthesis (CLI)
./cli/synthesize.py "Testing my voice!" -v my_voice -o test.wav

# 6. Play result
afplay test.wav

# Done! 🎉
```

---

## ⚡ Quick Commands Reference

```bash
# Installation and setup
./install-mac.sh           # Install everything
./verify-setup.sh          # Verify installation

# Running the platform
./start-all.sh             # Start all services
./start-backend.sh         # Start backend only
./start-frontend.sh        # Start frontend only

# CLI synthesis
./cli/synthesize.py --list-voices                    # List voices
./cli/synthesize.py "Text" -v my_voice -o out.wav   # Synthesize
./cli/synthesize.py "Text" -v my_voice -s 1.5       # 1.5x speed
./cli/synthesize.py "Hola" -v my_voice -l es        # Spanish

# Troubleshooting
lsof -ti:8000 | xargs kill -9                       # Kill backend
lsof -ti:3000 | xargs kill -9                       # Kill frontend
```

---

## 💡 Pro Tips

1. **Save your recordings**: Keep originals in case you want to re-process
2. **Test different models**: Each has different strengths
3. **Use keyboard shortcuts**: Browser shortcuts work in the UI
4. **Monitor progress**: Watch the terminal output for detailed logs
5. **Backup your voices**: Copy `data/` directory regularly

---

## 🆘 Need Help?

- **Check logs**: Look at terminal output
- **Visit API docs**: http://localhost:8000/docs
- **Read FAQ**: See main README.md
- **File an issue**: GitHub Issues
- **Check discussions**: GitHub Discussions

---

## 🎉 You're Ready!

You now know how to:
- ✅ Install EchoForge
- ✅ Clone your voice
- ✅ Generate speech via web UI
- ✅ Use the CLI tool
- ✅ Troubleshoot common issues

**Go create something amazing!** 🎤

---

**Your voice, your device.** 🚀

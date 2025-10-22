# EchoForge Deployment Guide

Complete guide for deploying EchoForge on your Mac mini as a local server.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Server](#running-the-server)
- [Production Setup](#production-setup)
- [Maintenance](#maintenance)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Hardware Requirements

**Minimum:**
- Mac mini (2018 or later)
- 8GB RAM
- 20GB free disk space
- macOS 11.0 (Big Sur) or later

**Recommended:**
- Mac mini (M1/M2/M3)
- 16GB+ RAM
- 50GB+ free disk space
- macOS 13.0 (Ventura) or later

### Software Requirements

- macOS 11.0+
- Python 3.9+
- Node.js 18+
- Homebrew (package manager)
- Git

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/echoforge.git
cd echoforge
```

### 2. Run Installation Script

```bash
# This installs all dependencies automatically
./install-mac.sh
```

The script will:
- Install Homebrew (if needed)
- Install Python 3.11
- Install Node.js
- Install ffmpeg
- Create Python virtual environment
- Install all Python dependencies
- Install all Node.js dependencies
- Create data directories
- Generate configuration files
- Run tests

**Installation time:** 10-20 minutes (depending on internet speed)

### 3. Verify Installation

```bash
./verify-setup.sh
```

This checks that everything is properly installed.

---

## Configuration

### Backend Configuration

Edit `backend/.env`:

```bash
# Database
DATABASE_URL=sqlite:///./echoforge.db
# For PostgreSQL: postgresql://user:password@localhost/echoforge

# Server
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY=your-secret-key-change-this
# Generate a secure key: openssl rand -hex 32

# TTS Model
TTS_MODEL=xtts_v2
TTS_DEVICE=auto  # auto, mps, cuda, cpu

# Storage
DATA_DIR=./data

# Development
DEBUG=false
LOG_LEVEL=INFO
```

### Frontend Configuration

Edit `frontend/.env`:

```bash
VITE_API_URL=http://localhost:8000
```

### Optional: Whisper ASR

For accurate consent verification, install Whisper:

```bash
cd backend
source venv/bin/activate
pip install openai-whisper
```

**Note:** Whisper requires additional 1-5GB for models depending on size.

---

## Running the Server

### Development Mode

**Option 1: All services at once**

```bash
./start-all.sh
```

This starts both backend and frontend with hot-reload.

**Option 2: Services separately**

```bash
# Terminal 1: Backend
./start-backend.sh

# Terminal 2: Frontend
./start-frontend.sh
```

Access the application:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Production Mode

For running as a always-on server on your Mac mini:

#### 1. Build Frontend

```bash
cd frontend
npm run build
```

This creates optimized production build in `frontend/dist/`.

#### 2. Serve Frontend with Backend

Edit `backend/app/main.py` and add:

```python
# Mount frontend build
app.mount("/", StaticFiles(directory="../frontend/dist", html=True), name="frontend")
```

#### 3. Run Backend with Gunicorn (Optional)

For production, use Gunicorn instead of uvicorn:

```bash
cd backend
source venv/bin/activate

# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn app.main:app \
    --workers 2 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --daemon
```

---

## Production Setup

### 1. Run as Background Service (launchd)

Create `~/Library/LaunchAgents/com.echoforge.server.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.echoforge.server</string>

    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>cd /path/to/echoforge && ./start-all.sh</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>StandardOutPath</key>
    <string>/path/to/echoforge/logs/stdout.log</string>

    <key>StandardErrorPath</key>
    <string>/path/to/echoforge/logs/stderr.log</string>
</dict>
</plist>
```

Load the service:

```bash
launchctl load ~/Library/LaunchAgents/com.echoforge.server.plist
```

Start/stop service:

```bash
# Start
launchctl start com.echoforge.server

# Stop
launchctl stop com.echoforge.server

# Check status
launchctl list | grep echoforge
```

### 2. Use PostgreSQL (Recommended for Production)

Install PostgreSQL:

```bash
brew install postgresql@15
brew services start postgresql@15
```

Create database:

```bash
createdb echoforge
```

Update `backend/.env`:

```bash
DATABASE_URL=postgresql://localhost/echoforge
```

Run migrations:

```bash
cd backend
source venv/bin/activate
python -c "from app.database import init_db; init_db()"
```

### 3. Enable HTTPS (Optional)

For secure connections:

1. **Generate SSL certificate:**

```bash
openssl req -x509 -newkey rsa:4096 -nodes \
    -keyout key.pem -out cert.pem -days 365
```

2. **Update backend to use HTTPS:**

```bash
uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8443 \
    --ssl-keyfile=key.pem \
    --ssl-certfile=cert.pem
```

### 4. Set Up Reverse Proxy with Nginx (Advanced)

Install nginx:

```bash
brew install nginx
```

Configure `/usr/local/etc/nginx/nginx.conf`:

```nginx
server {
    listen 80;
    server_name localhost;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Static files
    location /outputs {
        proxy_pass http://localhost:8000/outputs;
    }
}
```

Start nginx:

```bash
brew services start nginx
```

---

## Maintenance

### Database Backups

**SQLite:**

```bash
# Backup
cp data/echoforge.db backups/echoforge_$(date +%Y%m%d).db

# Restore
cp backups/echoforge_YYYYMMDD.db data/echoforge.db
```

**PostgreSQL:**

```bash
# Backup
pg_dump echoforge > backups/echoforge_$(date +%Y%m%d).sql

# Restore
psql echoforge < backups/echoforge_YYYYMMDD.sql
```

### Log Rotation

Create log rotation config in `/etc/newsyslog.d/echoforge.conf`:

```
# logfilename                      [owner:group]  mode  count  size  when  flags
/path/to/echoforge/logs/*.log                     644   7      10240 *     GZ
```

### Updates

```bash
# Pull latest code
git pull origin main

# Update Python dependencies
cd backend
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Update Node dependencies
cd ../frontend
npm install

# Restart services
./start-all.sh
```

### Monitoring Disk Usage

```bash
# Check data directory size
du -sh data/*

# Clean old outputs (optional)
find data/outputs -name "*.wav" -mtime +30 -delete
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -ti:8000

# Kill the process
lsof -ti:8000 | xargs kill -9
```

### Database Locked (SQLite)

```bash
# Close all connections and restart
rm data/echoforge.db-shm data/echoforge.db-wal
./start-all.sh
```

### High Memory Usage

```bash
# Check memory usage
ps aux | grep -E 'python|node'

# Restart services
./start-all.sh
```

### Model Download Issues

```bash
# Clear model cache
rm -rf data/models/*

# Restart - models will re-download
./start-all.sh
```

### Permission Denied

```bash
# Fix permissions
chmod +x install-mac.sh
chmod +x start-*.sh
chmod +x cli/synthesize.py
```

---

## Performance Optimization

### For Apple Silicon

Ensure you're using native ARM64 Python:

```bash
python3 -c "import platform; print(platform.machine())"
# Should output: arm64
```

### Reduce Memory Usage

In `backend/.env`:

```bash
# Use smaller TTS model
TTS_MODEL=vits  # instead of xtts_v2

# Limit worker processes
WORKERS=1
```

### Speed Up Synthesis

1. **Use GPU acceleration** (if available)
2. **Use faster TTS models** (Glow-TTS, Tacotron 2)
3. **Reduce audio quality** for faster processing

---

## Security Best Practices

1. **Change default SECRET_KEY** in `.env`
2. **Use PostgreSQL** instead of SQLite for production
3. **Enable HTTPS** if accessing remotely
4. **Set up firewall** to restrict access
5. **Regular backups** of database and voice profiles
6. **Keep dependencies updated**
7. **Monitor logs** for suspicious activity

---

## Network Access

### Local Network Only (Default)

Access from other devices on your network:

```bash
# Find your Mac mini's local IP
ifconfig | grep "inet "

# Access from other devices
http://YOUR_MAC_IP:3000
```

### Public Internet Access (Advanced)

**Warning:** Only do this if you understand the security implications.

1. **Set up dynamic DNS** (e.g., No-IP, DynDNS)
2. **Configure port forwarding** on your router
3. **Enable HTTPS** with proper SSL certificate
4. **Set up authentication** and rate limiting
5. **Use a VPN** for secure remote access (recommended)

---

## Resource Management

### Expected Resource Usage

| Component | CPU (idle) | CPU (processing) | RAM | Disk |
|-----------|------------|------------------|-----|------|
| Backend | ~5% | 50-100% | 2-4 GB | 3 GB |
| Frontend | ~2% | ~5% | 200 MB | 500 MB |
| TTS Model | - | 60-90% | 1-2 GB | 2 GB |

### Limits and Quotas

Configure in `backend/.env`:

```bash
MAX_UPLOAD_SIZE_MB=100
MAX_TEXT_LENGTH=5000
JOB_TIMEOUT_SECONDS=600
MAX_CONCURRENT_JOBS=2
```

---

## Support

- **Documentation**: See `/docs` folder
- **Issues**: GitHub Issues
- **Logs**: Check `logs/` directory
- **System Health**: Visit http://localhost:8000/health

---

## Checklist for Production Deployment

- [ ] Run `./install-mac.sh`
- [ ] Run `./verify-setup.sh`
- [ ] Change SECRET_KEY in `.env`
- [ ] Set up PostgreSQL (optional but recommended)
- [ ] Configure backups
- [ ] Set up as background service (launchd)
- [ ] Test voice cloning end-to-end
- [ ] Test synthesis
- [ ] Monitor resource usage
- [ ] Set up log rotation
- [ ] Document your specific configuration

---

**Your voice, your device - deployed and ready!** 🚀

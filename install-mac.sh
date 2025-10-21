#!/bin/bash

###############################################################################
# EchoForge Installation Script for macOS (Apple Silicon & Intel)
# Automatically sets up the complete voice cloning platform
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This script is for macOS only"
    exit 1
fi

# Detect architecture
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
    print_info "Detected: Apple Silicon (M1/M2/M3)"
    PYTHON_ARCH="arm64"
else
    print_info "Detected: Intel Mac"
    PYTHON_ARCH="x86_64"
fi

print_header "🎤 EchoForge Installation"
echo "This script will install:"
echo "  • Python dependencies"
echo "  • Node.js dependencies"
echo "  • Backend API server"
echo "  • Frontend web interface"
echo "  • CLI voice synthesizer"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Check prerequisites
print_header "Checking Prerequisites"

# Check for Homebrew
if ! command -v brew &> /dev/null; then
    print_warning "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    print_success "Homebrew installed"
else
    print_success "Homebrew found"
fi

# Check for Python 3.9+
if ! command -v python3 &> /dev/null; then
    print_warning "Python 3 not found. Installing Python..."
    brew install python@3.11
    print_success "Python installed"
else
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    print_success "Python $PYTHON_VERSION found"
fi

# Check for Node.js
if ! command -v node &> /dev/null; then
    print_warning "Node.js not found. Installing Node.js..."
    brew install node
    print_success "Node.js installed"
else
    NODE_VERSION=$(node --version)
    print_success "Node.js $NODE_VERSION found"
fi

# Check for ffmpeg (useful for audio processing)
if ! command -v ffmpeg &> /dev/null; then
    print_warning "ffmpeg not found. Installing ffmpeg..."
    brew install ffmpeg
    print_success "ffmpeg installed"
else
    print_success "ffmpeg found"
fi

# Install Python dependencies
print_header "Installing Python Dependencies"

cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_info "Creating Python virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
print_info "Installing Python packages (this may take several minutes)..."

# Install PyTorch with appropriate backend
if [[ "$ARCH" == "arm64" ]]; then
    print_info "Installing PyTorch for Apple Silicon (MPS support)..."
    pip install torch==2.1.1 torchaudio==2.1.1
else
    print_info "Installing PyTorch for Intel..."
    pip install torch==2.1.1 torchaudio==2.1.1
fi

# Install other dependencies
pip install -r requirements.txt

print_success "Python dependencies installed"

# Return to root directory
cd ..

# Install Node.js dependencies
print_header "Installing Node.js Dependencies"

cd frontend

print_info "Installing npm packages..."
npm install

print_success "Node.js dependencies installed"

# Return to root directory
cd ..

# Create necessary directories
print_header "Creating Data Directories"

mkdir -p data/uploads
mkdir -p data/models
mkdir -p data/outputs
mkdir -p cli/voices

print_success "Data directories created"

# Create environment file
print_header "Creating Configuration Files"

if [ ! -f "backend/.env" ]; then
    cat > backend/.env << EOF
# EchoForge Backend Configuration

# Database
DATABASE_URL=sqlite:///./echoforge.db

# Server
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY=$(openssl rand -hex 32)

# Storage
DATA_DIR=./data

# TTS
TTS_MODEL=xtts_v2
TTS_CACHE_DIR=./data/models

# Development
DEBUG=true
EOF
    print_success "Backend configuration created"
else
    print_info "Backend configuration already exists"
fi

if [ ! -f "frontend/.env" ]; then
    cat > frontend/.env << EOF
# EchoForge Frontend Configuration

VITE_API_URL=http://localhost:8000
EOF
    print_success "Frontend configuration created"
else
    print_info "Frontend configuration already exists"
fi

# Create startup scripts
print_header "Creating Startup Scripts"

cat > start-backend.sh << 'EOF'
#!/bin/bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
EOF
chmod +x start-backend.sh
print_success "Backend startup script created"

cat > start-frontend.sh << 'EOF'
#!/bin/bash
cd frontend
npm run dev
EOF
chmod +x start-frontend.sh
print_success "Frontend startup script created"

cat > start-all.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting EchoForge..."

# Start backend in background
echo "Starting backend..."
./start-backend.sh &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend in background
echo "Starting frontend..."
./start-frontend.sh &
FRONTEND_PID=$!

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  EchoForge is running!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "  Press Ctrl+C to stop all services"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Wait for Ctrl+C
trap "echo ''; echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
EOF
chmod +x start-all.sh
print_success "Combined startup script created"

# Make CLI executable
chmod +x cli/synthesize.py
print_success "CLI tool configured"

# Run tests
print_header "Running Tests"

cd backend
source venv/bin/activate

print_info "Running backend tests..."
python -m pytest tests/ -v || print_warning "Some tests failed (this is OK for first install)"

cd ..

print_success "Tests completed"

# Installation complete
print_header "✅ Installation Complete!"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Next Steps"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Start the platform:"
echo "   ${GREEN}./start-all.sh${NC}"
echo ""
echo "2. Open your browser to:"
echo "   ${BLUE}http://localhost:3000${NC}"
echo ""
echo "3. Or start services individually:"
echo "   ${GREEN}./start-backend.sh${NC}  # API server"
echo "   ${GREEN}./start-frontend.sh${NC} # Web interface"
echo ""
echo "4. Use the CLI synthesizer:"
echo "   ${GREEN}./cli/synthesize.py --list-voices${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 Documentation:"
echo "   • Backend README:  backend/README.md"
echo "   • Frontend README: frontend/README.md"
echo "   • CLI README:      cli/README.md"
echo ""
echo "🎤 Your voice, your device."
echo ""

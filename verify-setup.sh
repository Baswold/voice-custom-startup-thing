#!/bin/bash

###############################################################################
# EchoForge Verification Script
# Checks that everything is properly set up before running
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Track errors
ERRORS=0
WARNINGS=0

print_header "🔍 EchoForge Setup Verification"

# Check Python
print_header "Checking Python Environment"

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
        print_success "Python $PYTHON_VERSION found (>= 3.9 required)"
    else
        print_error "Python $PYTHON_VERSION found (3.9+ required)"
        ERRORS=$((ERRORS + 1))
    fi
else
    print_error "Python 3 not found"
    ERRORS=$((ERRORS + 1))
fi

# Check virtual environment
if [ -d "backend/venv" ]; then
    print_success "Python virtual environment exists"

    # Check if packages are installed
    if [ -f "backend/venv/bin/python" ]; then
        INSTALLED_PACKAGES=$(backend/venv/bin/pip list 2>/dev/null | wc -l)
        if [ $INSTALLED_PACKAGES -gt 10 ]; then
            print_success "Dependencies installed ($INSTALLED_PACKAGES packages)"
        else
            print_warning "Few packages installed. Run: cd backend && source venv/bin/activate && pip install -r requirements.txt"
            WARNINGS=$((WARNINGS + 1))
        fi
    fi
else
    print_warning "Python virtual environment not found. Run ./install-mac.sh"
    WARNINGS=$((WARNINGS + 1))
fi

# Check Node.js
print_header "Checking Node.js Environment"

if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js $NODE_VERSION found"
else
    print_error "Node.js not found"
    ERRORS=$((ERRORS + 1))
fi

if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    print_success "npm $NPM_VERSION found"
else
    print_error "npm not found"
    ERRORS=$((ERRORS + 1))
fi

# Check Node modules
if [ -d "frontend/node_modules" ]; then
    NODE_MODULES_COUNT=$(ls frontend/node_modules | wc -l)
    print_success "Node modules installed ($NODE_MODULES_COUNT packages)"
else
    print_warning "Node modules not found. Run: cd frontend && npm install"
    WARNINGS=$((WARNINGS + 1))
fi

# Check project structure
print_header "Checking Project Structure"

REQUIRED_DIRS=(
    "backend"
    "backend/app"
    "backend/tests"
    "frontend"
    "frontend/src"
    "cli"
    "data"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        print_success "Directory exists: $dir"
    else
        print_error "Missing directory: $dir"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check key files
print_header "Checking Key Files"

REQUIRED_FILES=(
    "backend/app/main.py"
    "backend/app/models.py"
    "backend/requirements.txt"
    "frontend/package.json"
    "frontend/src/App.jsx"
    "cli/synthesize.py"
    "README.md"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "File exists: $file"
    else
        print_error "Missing file: $file"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check configuration
print_header "Checking Configuration"

if [ -f "backend/.env" ]; then
    print_success "Backend .env file exists"
else
    print_warning "Backend .env not found. Copy from .env.example"
    WARNINGS=$((WARNINGS + 1))
fi

if [ -f "frontend/.env" ]; then
    print_success "Frontend .env file exists"
else
    print_warning "Frontend .env not found. Copy from .env.example"
    WARNINGS=$((WARNINGS + 1))
fi

# Check data directories
print_header "Checking Data Directories"

DATA_DIRS=(
    "data/uploads"
    "data/models"
    "data/outputs"
    "cli/voices"
)

for dir in "${DATA_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        print_success "Data directory exists: $dir"
    else
        print_warning "Data directory missing: $dir (will be created on first run)"
        WARNINGS=$((WARNINGS + 1))
    fi
done

# Check permissions
print_header "Checking Permissions"

EXECUTABLE_FILES=(
    "install-mac.sh"
    "cli/synthesize.py"
)

for file in "${EXECUTABLE_FILES[@]}"; do
    if [ -f "$file" ]; then
        if [ -x "$file" ]; then
            print_success "Executable: $file"
        else
            print_warning "Not executable: $file (run: chmod +x $file)"
            WARNINGS=$((WARNINGS + 1))
        fi
    fi
done

# Check optional dependencies
print_header "Checking Optional Dependencies"

if command -v ffmpeg &> /dev/null; then
    FFMPEG_VERSION=$(ffmpeg -version | head -n1 | cut -d' ' -f3)
    print_success "ffmpeg $FFMPEG_VERSION found (recommended for audio processing)"
else
    print_warning "ffmpeg not found (recommended but optional)"
fi

if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version | cut -d' ' -f3)
    print_success "git $GIT_VERSION found"
else
    print_warning "git not found"
fi

# Summary
print_header "📊 Verification Summary"

echo ""
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}  ✓ All checks passed! You're ready to go!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Run: ${GREEN}./start-all.sh${NC}"
    echo "  2. Open: ${BLUE}http://localhost:3000${NC}"
    echo ""
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}  ⚠ $WARNINGS warning(s) found${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "The system should work, but you may want to:"
    echo "  1. Run: ${GREEN}./install-mac.sh${NC} to fix warnings"
    echo "  2. Or manually install missing components"
    echo ""
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}  ✗ $ERRORS error(s) and $WARNINGS warning(s) found${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Please run: ${GREEN}./install-mac.sh${NC} to complete setup"
    echo ""
    exit 1
fi

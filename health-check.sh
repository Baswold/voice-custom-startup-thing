#!/bin/bash

###############################################################################
# EchoForge Health Check
# Checks if the platform is running correctly
###############################################################################

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  🏥 EchoForge Health Check${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

CHECKS_PASSED=0
CHECKS_FAILED=0

# Check backend
print_info "Checking backend (http://localhost:8000)..."

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    RESPONSE=$(curl -s http://localhost:8000/health)
    STATUS=$(echo $RESPONSE | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

    if [ "$STATUS" = "healthy" ]; then
        VERSION=$(echo $RESPONSE | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
        print_success "Backend is healthy (version: $VERSION)"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        print_error "Backend returned unhealthy status"
        CHECKS_FAILED=$((CHECKS_FAILED + 1))
    fi
else
    print_error "Backend is not responding"
    print_info "  Start with: ./start-backend.sh"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi

# Check frontend
print_info "Checking frontend (http://localhost:3000)..."

if curl -s http://localhost:3000 > /dev/null 2>&1; then
    print_success "Frontend is running"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    print_error "Frontend is not responding"
    print_info "  Start with: ./start-frontend.sh"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi

# Check database
print_info "Checking database..."

if [ -f "backend/echoforge.db" ]; then
    SIZE=$(ls -lh backend/echoforge.db | awk '{print $5}')
    print_success "Database file exists ($SIZE)"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    print_error "Database file not found"
    print_info "  Will be created on first run"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi

# Check data directories
print_info "Checking data directories..."

if [ -d "data/uploads" ] && [ -d "data/models" ] && [ -d "data/outputs" ]; then
    print_success "Data directories exist"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))

    # Show disk usage
    UPLOADS_SIZE=$(du -sh data/uploads 2>/dev/null | cut -f1)
    MODELS_SIZE=$(du -sh data/models 2>/dev/null | cut -f1)
    OUTPUTS_SIZE=$(du -sh data/outputs 2>/dev/null | cut -f1)

    print_info "  Uploads: $UPLOADS_SIZE"
    print_info "  Models: $MODELS_SIZE"
    print_info "  Outputs: $OUTPUTS_SIZE"
else
    print_error "Data directories missing"
    print_info "  Will be created on first run"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi

# Check API endpoints
if [ $CHECKS_PASSED -ge 2 ]; then
    print_info "Testing API endpoints..."

    # Test health endpoint
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        print_success "Health endpoint working"
    else
        print_error "Health endpoint failed"
        CHECKS_FAILED=$((CHECKS_FAILED + 1))
    fi

    # Test API docs
    if curl -s http://localhost:8000/docs | grep -q "FastAPI"; then
        print_success "API documentation available"
        print_info "  Visit: http://localhost:8000/docs"
    else
        print_error "API documentation not available"
        CHECKS_FAILED=$((CHECKS_FAILED + 1))
    fi
fi

# Check processes
print_info "Checking processes..."

BACKEND_PROCS=$(pgrep -f "uvicorn.*app.main" | wc -l)
FRONTEND_PROCS=$(pgrep -f "vite.*3000" | wc -l)

if [ $BACKEND_PROCS -gt 0 ]; then
    print_success "Backend process running (PID: $(pgrep -f 'uvicorn.*app.main'))"
else
    print_info "No backend process found"
fi

if [ $FRONTEND_PROCS -gt 0 ]; then
    print_success "Frontend process running (PID: $(pgrep -f 'vite.*3000'))"
else
    print_info "No frontend process found"
fi

# Check system resources
print_info "Checking system resources..."

# Disk space
DISK_AVAIL=$(df -h . | tail -1 | awk '{print $4}')
print_info "  Available disk space: $DISK_AVAIL"

# Memory
if command -v vm_stat &> /dev/null; then
    FREE_BLOCKS=$(vm_stat | grep free | awk '{ print $3 }' | sed 's/\.//')
    FREE_MB=$((FREE_BLOCKS * 4096 / 1048576))
    print_info "  Free memory: ~${FREE_MB}MB"
fi

# CPU
if command -v sysctl &> /dev/null; then
    CPU_COUNT=$(sysctl -n hw.ncpu)
    print_info "  CPU cores: $CPU_COUNT"
fi

# Summary
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}  ✓ All checks passed! System is healthy.${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "🎉 EchoForge is running perfectly!"
    echo ""
    echo "Access points:"
    echo "  • Web UI:   http://localhost:3000"
    echo "  • API:      http://localhost:8000"
    echo "  • API Docs: http://localhost:8000/docs"
    echo ""
    exit 0
else
    echo -e "${YELLOW}  ⚠ Some checks failed ($CHECKS_FAILED issues found)${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Quick fixes:"
    echo "  • Start services: ./start-all.sh"
    echo "  • Check setup: ./verify-setup.sh"
    echo "  • View logs: Check terminal output"
    echo ""
    exit 1
fi

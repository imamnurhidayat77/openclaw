#!/usr/bin/env bash
# ============================================================
# deploy.sh - Deploy otomatis ke server
# ============================================================
# Usage: bash scripts/deploy.sh [production|staging]
# ============================================================

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
RESET='\033[0m'

ENVIRONMENT="${1:-production}"

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════╗${RESET}"
echo -e "${CYAN}║    OpenClaw AI - Deploy ($ENVIRONMENT)    ${RESET}"
echo -e "${CYAN}╚══════════════════════════════════════════╝${RESET}"
echo ""

# ── 1. Pre-deploy checks ──
echo -e "${YELLOW}[1/5] Running pre-deploy checks...${RESET}"

# Lint
echo -e "  ${YELLOW}→ Linting...${RESET}"
python3 -m ruff check app/ tests/ || {
    echo -e "${RED}  ✗ Lint failed! Fix errors before deploying.${RESET}"
    exit 1
}
echo -e "  ${GREEN}✔ Lint passed${RESET}"

# Tests
echo -e "  ${YELLOW}→ Running tests...${RESET}"
python3 -m pytest tests/ -v --tb=short -q || {
    echo -e "${RED}  ✗ Tests failed! Fix them before deploying.${RESET}"
    exit 1
}
echo -e "  ${GREEN}✔ Tests passed${RESET}"

# ── 2. Build Docker image ──
echo -e "${YELLOW}[2/5] Building Docker image...${RESET}"
docker compose build
echo -e "${GREEN}  ✔ Docker image built${RESET}"

# ── 3. Stop old containers ──
echo -e "${YELLOW}[3/5] Stopping old containers...${RESET}"
docker compose down 2>/dev/null || true
echo -e "${GREEN}  ✔ Old containers stopped${RESET}"

# ── 4. Start new containers ──
echo -e "${YELLOW}[4/5] Starting new containers...${RESET}"
docker compose up -d
echo -e "${GREEN}  ✔ Containers started${RESET}"

# ── 5. Health check ──
echo -e "${YELLOW}[5/5] Running health check...${RESET}"
sleep 3

MAX_RETRIES=10
RETRY_COUNT=0
until curl -sf http://localhost:8000/health > /dev/null 2>&1; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo -e "${RED}  ✗ Health check failed after $MAX_RETRIES attempts${RESET}"
        echo -e "${YELLOW}  Check logs: docker compose logs${RESET}"
        exit 1
    fi
    echo -e "  ${YELLOW}Waiting for app to start... (attempt $RETRY_COUNT/$MAX_RETRIES)${RESET}"
    sleep 2
done
echo -e "${GREEN}  ✔ Health check passed${RESET}"

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${RESET}"
echo -e "${GREEN}║    ✔ Deploy Complete!                    ║${RESET}"
echo -e "${GREEN}║    App: http://localhost:8000             ║${RESET}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${RESET}"

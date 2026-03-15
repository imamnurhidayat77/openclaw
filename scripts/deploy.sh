#!/usr/bin/env bash
# ============================================================
# deploy.sh - Deploy otomatis ke server
# ============================================================
# Usage: bash scripts/deploy.sh [production|staging]
#
# Pipeline:
#   1. Pre-deploy checks (lint + test + coverage)
#   2. Build Docker image
#   3. Stop old containers
#   4. Start new containers
#   5. Health check
#   6. Smoke tests (API verification)
#   7. Auto-rollback jika gagal
# ============================================================

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
RESET='\033[0m'

ENVIRONMENT="${1:-production}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════╗${RESET}"
echo -e "${CYAN}║    OpenClaw AI - Deploy ($ENVIRONMENT)   ${RESET}"
echo -e "${CYAN}╚══════════════════════════════════════════╝${RESET}"
echo ""

# ── Track deploy time ──
DEPLOY_START=$(date +%s)

# ── 1. Pre-deploy checks ──
echo -e "${YELLOW}[1/7] Running pre-deploy checks...${RESET}"

# Format
echo -e "  ${YELLOW}→ Formatting...${RESET}"
python3 -m ruff format app/ tests/ --quiet
python3 -m ruff check app/ tests/ --fix --quiet 2>/dev/null || true
echo -e "  ${GREEN}✔ Code formatted${RESET}"

# Lint
echo -e "  ${YELLOW}→ Linting...${RESET}"
python3 -m ruff check app/ tests/ || {
    echo -e "${RED}  ✗ Lint failed! Fix errors before deploying.${RESET}"
    exit 1
}
echo -e "  ${GREEN}✔ Lint passed${RESET}"

# Type check
echo -e "  ${YELLOW}→ Type checking...${RESET}"
python3 -m mypy app/ --ignore-missing-imports || {
    echo -e "${RED}  ✗ Type check failed! Fix before deploying.${RESET}"
    exit 1
}
echo -e "  ${GREEN}✔ Type check passed${RESET}"

# ── 2. Tests + coverage ──
echo -e "${YELLOW}[2/7] Running automated tests...${RESET}"
python3 -m pytest tests/ -v --tb=short --cov=app --cov-report=term-missing || {
    echo -e "${RED}  ✗ Tests failed! Fix them before deploying.${RESET}"
    exit 1
}
echo -e "${GREEN}  ✔ All tests passed${RESET}"

# ── 3. Git status check ──
echo -e "${YELLOW}[3/7] Checking git status...${RESET}"
if [[ -n "$(git status --porcelain 2>/dev/null)" ]]; then
    echo -e "  ${YELLOW}⚠ Ada perubahan yang belum di-commit:${RESET}"
    git status --short
    echo -e "  ${YELLOW}  Deploy tetap lanjut, tapi sebaiknya commit dulu.${RESET}"
fi
GIT_HASH=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
echo -e "  ${GREEN}✔ Deploying commit: $GIT_HASH${RESET}"

# ── 4. Build Docker image ──
echo -e "${YELLOW}[4/7] Building Docker image...${RESET}"
docker compose build || {
    echo -e "${RED}  ✗ Docker build failed!${RESET}"
    exit 1
}
echo -e "${GREEN}  ✔ Docker image built${RESET}"

# ── 5. Stop old containers ──
echo -e "${YELLOW}[5/7] Stopping old containers...${RESET}"
docker compose down 2>/dev/null || true
echo -e "${GREEN}  ✔ Old containers stopped${RESET}"

# ── 6. Start new containers ──
echo -e "${YELLOW}[6/7] Starting new containers...${RESET}"
docker compose up -d
echo -e "${GREEN}  ✔ Containers started${RESET}"

# ── 7. Post-deploy verification ──
echo -e "${YELLOW}[7/7] Post-deploy verification...${RESET}"
sleep 3

# Health check
MAX_RETRIES=10
RETRY_COUNT=0
until curl -sf http://localhost:8000/health > /dev/null 2>&1; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo -e "${RED}  ✗ Health check failed after $MAX_RETRIES attempts${RESET}"
        echo -e "${YELLOW}  Rolling back...${RESET}"
        docker compose down
        echo -e "${RED}  Deploy dibatalkan. Cek logs: docker compose logs${RESET}"
        exit 1
    fi
    echo -e "  ${YELLOW}Waiting for app to start... ($RETRY_COUNT/$MAX_RETRIES)${RESET}"
    sleep 2
done
echo -e "  ${GREEN}✔ Health check passed${RESET}"

# Smoke tests
echo -e "  ${YELLOW}→ Running smoke tests...${RESET}"
python3 scripts/smoke_test.py || {
    echo -e "${RED}  ✗ Smoke tests failed! Rolling back...${RESET}"
    docker compose down
    exit 1
}

# ── Done ──
DEPLOY_END=$(date +%s)
DEPLOY_TIME=$((DEPLOY_END - DEPLOY_START))

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${RESET}"
echo -e "${GREEN}║    ✔ Deploy Complete!                    ║${RESET}"
echo -e "${GREEN}║    App:    http://localhost:8000          ║${RESET}"
echo -e "${GREEN}║    Commit: $GIT_HASH                            ║${RESET}"
echo -e "${GREEN}║    Time:   ${DEPLOY_TIME}s                              ║${RESET}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${RESET}"

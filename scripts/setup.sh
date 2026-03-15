#!/usr/bin/env bash
# ============================================================
# setup.sh - Setup otomatis project OpenClaw AI
# ============================================================
# Usage: bash scripts/setup.sh
# ============================================================

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
RESET='\033[0m'

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════╗${RESET}"
echo -e "${CYAN}║    OpenClaw AI - Automated Setup         ║${RESET}"
echo -e "${CYAN}╚══════════════════════════════════════════╝${RESET}"
echo ""

# ── 1. Check Python ──
echo -e "${YELLOW}[1/6] Checking Python...${RESET}"
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}✗ Python3 not found. Install Python 3.10+ first.${RESET}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1)
echo -e "${GREEN}  ✔ $PYTHON_VERSION${RESET}"

# ── 2. Create venv ──
echo -e "${YELLOW}[2/6] Creating virtual environment...${RESET}"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo -e "${GREEN}  ✔ Virtual environment created${RESET}"
else
    echo -e "${GREEN}  ✔ Virtual environment already exists${RESET}"
fi

# Activate venv
source .venv/bin/activate

# ── 3. Install dependencies ──
echo -e "${YELLOW}[3/6] Installing dependencies...${RESET}"
pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install -r requirements-dev.txt -q
echo -e "${GREEN}  ✔ Dependencies installed${RESET}"

# ── 4. Setup .env ──
echo -e "${YELLOW}[4/6] Setting up environment...${RESET}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}  ✔ .env created from .env.example${RESET}"
    echo -e "${YELLOW}  ⚠ Edit .env file to add your API keys!${RESET}"
else
    echo -e "${GREEN}  ✔ .env already exists${RESET}"
fi

# ── 5. Setup pre-commit hooks ──
echo -e "${YELLOW}[5/6] Setting up pre-commit hooks...${RESET}"
if command -v pre-commit &>/dev/null; then
    pre-commit install
    echo -e "${GREEN}  ✔ Pre-commit hooks installed${RESET}"
else
    echo -e "${YELLOW}  ⚠ pre-commit not found, skipping hooks${RESET}"
fi

# ── 6. Run quick check ──
echo -e "${YELLOW}[6/6] Running quick checks...${RESET}"
python3 -m pytest tests/ -v --tb=short -q 2>/dev/null && \
    echo -e "${GREEN}  ✔ All tests passed${RESET}" || \
    echo -e "${YELLOW}  ⚠ Some tests need attention${RESET}"

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${RESET}"
echo -e "${GREEN}║    ✔ Setup Complete!                     ║${RESET}"
echo -e "${GREEN}╠══════════════════════════════════════════╣${RESET}"
echo -e "${GREEN}║                                          ║${RESET}"
echo -e "${GREEN}║  Activate venv:                          ║${RESET}"
echo -e "${GREEN}║    source .venv/bin/activate              ║${RESET}"
echo -e "${GREEN}║                                          ║${RESET}"
echo -e "${GREEN}║  Start dev server:                       ║${RESET}"
echo -e "${GREEN}║    make dev                               ║${RESET}"
echo -e "${GREEN}║                                          ║${RESET}"
echo -e "${GREEN}║  Run tests:                              ║${RESET}"
echo -e "${GREEN}║    make test                              ║${RESET}"
echo -e "${GREEN}║                                          ║${RESET}"
echo -e "${GREEN}║  See all commands:                       ║${RESET}"
echo -e "${GREEN}║    make help                              ║${RESET}"
echo -e "${GREEN}║                                          ║${RESET}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${RESET}"

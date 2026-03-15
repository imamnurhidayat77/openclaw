#!/usr/bin/env bash
# ============================================================
# Install git hooks
# ============================================================
# Usage: bash scripts/install-hooks.sh
# ============================================================

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RESET='\033[0m'

HOOKS_DIR="$(git rev-parse --git-dir)/hooks"

echo -e "${YELLOW}▶ Installing git hooks...${RESET}"

# Install pre-push hook
cp scripts/pre-push "$HOOKS_DIR/pre-push"
chmod +x "$HOOKS_DIR/pre-push"
echo -e "${GREEN}  ✔ pre-push hook installed${RESET}"

# Install pre-commit (if available)
if command -v pre-commit &>/dev/null; then
    pre-commit install
    echo -e "${GREEN}  ✔ pre-commit hooks installed${RESET}"
fi

echo -e "${GREEN}✔ All hooks installed!${RESET}"
echo ""
echo "Sekarang setiap kali kamu:"
echo "  git push   → otomatis lint + test dulu"
echo "  git commit → otomatis format + check"

# ============================================================
# OpenClaw AI - Makefile Automation
# ============================================================
# Gunakan: make <target>
# Lihat semua target: make help
# ============================================================

.PHONY: help setup install run dev test lint format clean docker-build docker-up docker-down docker-logs check all

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON     := python3
PIP        := pip
VENV       := .venv
UVICORN    := uvicorn
APP_MODULE := app.main:app

# Colors for output
GREEN  := \033[0;32m
YELLOW := \033[0;33m
CYAN   := \033[0;36m
RESET  := \033[0m

# ============================================================
# 📋 HELP
# ============================================================
help: ## Tampilkan daftar semua command
	@echo ""
	@echo "$(CYAN)╔══════════════════════════════════════════╗$(RESET)"
	@echo "$(CYAN)║      OpenClaw AI - Make Commands         ║$(RESET)"
	@echo "$(CYAN)╚══════════════════════════════════════════╝$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-18s$(RESET) %s\n", $$1, $$2}'
	@echo ""

# ============================================================
# 🚀 SETUP & INSTALL
# ============================================================
setup: ## Setup lengkap: venv + install + env
	@echo "$(YELLOW)▶ Membuat virtual environment...$(RESET)"
	$(PYTHON) -m venv $(VENV)
	@echo "$(YELLOW)▶ Menginstall dependencies...$(RESET)"
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt
	$(VENV)/bin/pip install -r requirements-dev.txt
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(GREEN)✔ File .env dibuat dari .env.example$(RESET)"; \
	fi
	@echo "$(GREEN)✔ Setup selesai! Jalankan: make dev$(RESET)"

install: ## Install dependencies saja
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt

# ============================================================
# 🏃 RUN
# ============================================================
run: ## Jalankan server (production mode)
	$(UVICORN) $(APP_MODULE) --host 0.0.0.0 --port 8000

dev: ## Jalankan server (development mode + auto-reload)
	$(UVICORN) $(APP_MODULE) --reload --host 127.0.0.1 --port 8000

# ============================================================
# 🧪 TESTING
# ============================================================
test: ## Jalankan semua test
	@echo "$(YELLOW)▶ Menjalankan tests...$(RESET)"
	$(PYTHON) -m pytest tests/ -v --tb=short

test-cov: ## Jalankan test + coverage report
	@echo "$(YELLOW)▶ Menjalankan tests + coverage...$(RESET)"
	$(PYTHON) -m pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html
	@echo "$(GREEN)✔ Coverage report: htmlcov/index.html$(RESET)"

test-watch: ## Jalankan test secara otomatis saat file berubah
	$(PYTHON) -m pytest_watch -- tests/ -v --tb=short

# ============================================================
# 🔍 CODE QUALITY
# ============================================================
lint: ## Cek kualitas kode (ruff + mypy)
	@echo "$(YELLOW)▶ Running ruff linter...$(RESET)"
	$(PYTHON) -m ruff check app/ tests/
	@echo "$(YELLOW)▶ Running mypy type checker...$(RESET)"
	$(PYTHON) -m mypy app/ --ignore-missing-imports
	@echo "$(GREEN)✔ Lint passed!$(RESET)"

format: ## Format kode otomatis (ruff format)
	@echo "$(YELLOW)▶ Formatting code...$(RESET)"
	$(PYTHON) -m ruff format app/ tests/
	$(PYTHON) -m ruff check app/ tests/ --fix
	@echo "$(GREEN)✔ Code formatted!$(RESET)"

check: ## Jalankan lint + test sekaligus (pre-push check)
	@echo "$(CYAN)═══ Running full check ═══$(RESET)"
	@$(MAKE) format
	@$(MAKE) lint
	@$(MAKE) test
	@echo "$(GREEN)✔ All checks passed!$(RESET)"

# ============================================================
# 🐳 DOCKER
# ============================================================
docker-build: ## Build Docker image
	docker compose build

docker-up: ## Start semua container
	docker compose up -d
	@echo "$(GREEN)✔ App running at http://localhost:8000$(RESET)"

docker-down: ## Stop semua container
	docker compose down

docker-logs: ## Lihat logs container
	docker compose logs -f

docker-restart: ## Restart semua container
	docker compose down && docker compose up -d

# ============================================================
# 🧹 CLEAN
# ============================================================
clean: ## Bersihkan file sementara
	@echo "$(YELLOW)▶ Cleaning...$(RESET)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	@echo "$(GREEN)✔ Clean!$(RESET)"

# ============================================================
# 🎯 ALL-IN-ONE
# ============================================================
all: setup check ## Setup + jalankan semua check
	@echo "$(GREEN)🎉 Semua selesai!$(RESET)"

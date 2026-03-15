<div align="center">

# 🤖 OpenClaw AI

**AI Chatbot Platform dengan Multi-Provider LLM, Telegram Bot, dan Full CI/CD Pipeline**

[![CI/CD](https://github.com/imamnurhidayat77/openclaw/actions/workflows/ci.yml/badge.svg)](https://github.com/imamnurhidayat77/openclaw/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116-009688.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED.svg)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

</div>

---

## Highlights

- **Multi-Provider** — Pilih antara Ollama (lokal) atau OpenAI-compatible API (OpenRouter, GPT, dll)
- **Auto Fallback** — Otomatis switch dari Ollama ke OpenAI jika Ollama down
- **Telegram Bot** — Integrasi langsung ke Telegram via long polling
- **REST API** — `POST /api/chat` siap integrasi ke frontend manapun
- **Web UI** — Chat interface minimalis di browser
- **Full CI/CD** — GitHub Actions: lint → test → build → deploy
- **Dockerized** — Satu command untuk deploy ke production
- **Automated Testing** — 19 tests, 53%+ coverage
- **Code Quality** — Pre-commit hooks, Ruff linter, MyPy type checker

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI, Uvicorn |
| LLM Providers | Ollama, OpenAI API, OpenRouter |
| Bot | Telegram Bot API (long polling) |
| Testing | Pytest, pytest-cov, pytest-anyio |
| Code Quality | Ruff, MyPy, Pre-commit |
| CI/CD | GitHub Actions |
| Container | Docker, Docker Compose |
| Automation | Make, Bash scripts |

---

## Quick Start
```bash
cd openclaw-ai
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## 2) Jalankan Ollama (opsional tapi default)
Install Ollama lalu pull model:
```bash
ollama pull llama3.1:8b
```

## 3) Jalankan aplikasi
```bash
uvicorn app.main:app --reload
```

Buka:
- http://127.0.0.1:8000
- Health check: http://127.0.0.1:8000/health

## Pakai provider OpenAI-compatible
Edit `.env`:
```env
OPENCLAW_PROVIDER=openai
OPENAI_API_KEY=isi_api_key_kamu
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

Lalu restart server.

## Aktifkan fallback otomatis (opsional)
Jika ingin tetap pakai `ollama` sebagai utama, tapi otomatis pindah ke OpenAI-compatible saat Ollama down:

```env
OPENCLAW_PROVIDER=ollama
OPENAI_API_KEY=isi_api_key_kamu
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
OPENCLAW_FALLBACK_TO_OPENAI_ON_OLLAMA_ERROR=true
```

Catatan: fallback hanya aktif jika `OPENAI_API_KEY` terisi.

## Integrasi Telegram
1. Buat bot lewat `@BotFather` di Telegram lalu copy token bot.
2. Edit `.env`:

```env
TELEGRAM_BOT_ENABLED=true
TELEGRAM_BOT_TOKEN=isi_token_dari_botfather
TELEGRAM_POLL_TIMEOUT=20
```

3. Jalankan bot polling:

```bash
python -m app.telegram_bot
```

4. Buka Telegram, cari username bot kamu, lalu kirim `/start`.

Catatan:
- Jalankan backend web (`uvicorn ...`) dan Telegram bot di terminal terpisah jika kamu ingin keduanya aktif bersamaan.
- Telegram bot menggunakan provider yang sama dengan konfigurasi `.env` (`openai` atau `ollama`).

## Struktur
```
openclaw-ai/
  app/
    main.py
    providers.py
    config.py
    telegram_bot.py
  tests/
    test_api.py
    test_providers.py
    test_config.py
  scripts/
    setup.sh
    deploy.sh
  static/
    index.html
  .github/workflows/
    ci.yml
  .env.example
  .pre-commit-config.yaml
  Dockerfile
  docker-compose.yml
  Makefile
  pyproject.toml
  requirements.txt
  requirements-dev.txt
```

---

## 🤖 Automation Guide

Project ini sudah dilengkapi full automation pipeline. Berikut penjelasan setiap tahap:

### Quick Start (Setup Otomatis)
```bash
# Satu command untuk setup semuanya:
bash scripts/setup.sh

# Atau pakai Make:
make setup
```

### Development Workflow

| Command | Fungsi |
|---------|--------|
| `make dev` | Jalankan server (auto-reload) |
| `make test` | Jalankan semua test |
| `make test-cov` | Test + coverage report |
| `make lint` | Cek kualitas kode |
| `make format` | Format kode otomatis |
| `make check` | Format + lint + test (pre-push) |
| `make clean` | Bersihkan file sementara |
| `make help` | Lihat semua command |

### Automation Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEVELOPMENT WORKFLOW                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. CODE          2. PRE-COMMIT       3. PUSH                  │
│  ┌──────────┐     ┌──────────────┐    ┌──────────────┐         │
│  │ Edit     │────▶│ Auto format  │───▶│ git push     │         │
│  │ code     │     │ Auto lint    │    │              │         │
│  └──────────┘     │ Check keys   │    └──────┬───────┘         │
│                   └──────────────┘           │                  │
│                                              ▼                  │
│  4. CI/CD (GitHub Actions)                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Lint     │─▶│ Test     │─▶│ Build    │─▶│ Deploy   │       │
│  │ (ruff)   │  │ (pytest) │  │ (Docker) │  │ (server) │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Docker
```bash
make docker-build    # Build image
make docker-up       # Start containers
make docker-down     # Stop containers
make docker-logs     # Lihat logs
make docker-restart  # Restart
```

### Deploy ke Production
```bash
bash scripts/deploy.sh
```
Script ini otomatis: lint → test → build Docker → deploy → health check.

### Pre-commit Hooks
Otomatis format & lint setiap kali `git commit`:
```bash
pre-commit install          # Install hooks (satu kali)
pre-commit run --all-files  # Manual run
```

---

## API Reference

### `GET /health`
Health check endpoint.
```json
{ "status": "ok", "provider": "openai" }
```

### `POST /api/chat`
Kirim pesan ke AI.
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Halo!", "history": []}'
```
Response:
```json
{ "reply": "Halo! Ada yang bisa saya bantu?" }
```

### `GET /`
Web chat UI.

---

## Screenshots

> Tambahkan screenshot UI chat dan Telegram bot di sini untuk portofolio yang lebih menarik.
> Caranya: ambil screenshot, simpan di folder `docs/`, lalu uncomment baris di bawah:
>
> ```markdown
> ![Web Chat](docs/screenshot-web.png)
> ![Telegram Bot](docs/screenshot-telegram.png)
> ```

---

## Contributing

1. Fork repo ini
2. Buat branch: `git checkout -b feature/nama-fitur`
3. Commit: `git commit -m "feat: tambah fitur X"`
4. Push: `git push origin feature/nama-fitur`
5. Buat Pull Request

Gunakan [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` fitur baru
- `fix:` perbaikan bug
- `docs:` dokumentasi
- `test:` testing
- `ci:` CI/CD changes

---

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

---

<div align="center">
  <sub>Built with FastAPI + Python | Automation by GitHub Actions + Docker</sub>
</div>

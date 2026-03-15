from contextlib import asynccontextmanager, suppress
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .config import settings
from .providers import ProviderError, chat_with_provider


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start Telegram bot polling on startup if enabled."""
    import asyncio

    bot_task = None
    if settings.telegram_bot_enabled and settings.telegram_bot_token:
        from .telegram_bot import run_telegram_bot

        bot_task = asyncio.create_task(run_telegram_bot())
        print("[app] Telegram bot started")

    yield

    if bot_task:
        bot_task.cancel()
        with suppress(asyncio.CancelledError):
            await bot_task
        print("[app] Telegram bot stopped")


class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    history: list[Message] = []


class ChatResponse(BaseModel):
    reply: str


app = FastAPI(title=settings.app_title, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "provider": settings.provider}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    try:
        history_dict = [item.model_dump() for item in payload.history]
        reply = await chat_with_provider(payload.message, history_dict)
        return ChatResponse(reply=reply)
    except ProviderError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Internal error: {error}") from error

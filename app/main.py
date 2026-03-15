from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .config import settings
from .providers import ProviderError, chat_with_provider


class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    history: list[Message] = []


class ChatResponse(BaseModel):
    reply: str


app = FastAPI(title=settings.app_title)

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
    api_key = settings.openai_api_key
    return {
        "status": "ok",
        "provider": settings.provider,
        "api_key_set": bool(api_key),
        "api_key_preview": f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "(empty)",
        "base_url": settings.openai_base_url,
        "model": settings.openai_model,
    }


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

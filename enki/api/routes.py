"""API routes — REST endpoints + WebSocket streaming chat."""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from enki.core.assistant import Assistant
from enki.plugins import DEFAULT_PLUGINS

logger = logging.getLogger(__name__)

router = APIRouter()

# One shared assistant instance per process (stateful memory).
_assistant: Assistant | None = None


def _get_assistant() -> Assistant:
    global _assistant  # noqa: PLW0603
    if _assistant is None:
        _assistant = Assistant(plugins=DEFAULT_PLUGINS)
    return _assistant


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


class ResetResponse(BaseModel):
    status: str


class HealthResponse(BaseModel):
    status: str
    version: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get("/health", response_model=HealthResponse, tags=["meta"])
async def health() -> HealthResponse:
    """Liveness probe."""
    from enki import __version__

    return HealthResponse(status="ok", version=__version__)


@router.post("/chat", response_model=ChatResponse, tags=["chat"])
async def chat(request: ChatRequest) -> ChatResponse:
    """Send a message and receive a complete reply."""
    assistant = _get_assistant()
    try:
        reply = await assistant.chat(request.message)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Error during /chat")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return ChatResponse(reply=reply)


@router.post("/reset", response_model=ResetResponse, tags=["chat"])
async def reset() -> ResetResponse:
    """Clear conversation history."""
    _get_assistant().reset()
    return ResetResponse(status="conversation reset")


@router.get("/plugins", tags=["meta"])
async def list_plugins() -> list[dict]:
    """List registered plugins / tools."""
    return [p.schema() for p in _get_assistant().plugins]


@router.websocket("/ws/chat")
async def ws_chat(websocket: WebSocket) -> None:
    """Stream chat replies token by token over a WebSocket."""
    await websocket.accept()
    assistant = _get_assistant()
    try:
        while True:
            user_input = await websocket.receive_text()
            async for chunk in assistant.stream(user_input):
                await websocket.send_text(chunk)
            # Signal end-of-message with an empty sentinel.
            await websocket.send_text("")
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as exc:  # noqa: BLE001
        logger.exception("WebSocket error")
        await websocket.close(code=1011, reason=str(exc))

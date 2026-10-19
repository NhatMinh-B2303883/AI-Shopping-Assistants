"""Camera Relay Endpoints — Bridge between Mobile Camera and Desktop Web.

Enables cross-device mobile camera capture over LAN/Wi-Fi:
1. Desktop creates session: POST /api/v1/camera/session -> sessionId
2. Mobile uploads photo:    POST /api/v1/camera/upload/{sessionId} -> saves image in-memory
3. Desktop polls status:    GET /api/v1/camera/status/{sessionId} -> returns image when ready
"""

from __future__ import annotations

import time
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter()

# In-memory store for active camera sessions
# Structure: { session_id: { "created_at": float, "image": str | None, "category": str | None, "ready": bool } }
_camera_sessions: Dict[str, Dict[str, Any]] = {}
_SESSION_TTL_SECONDS = 900  # 15 minutes


def _cleanup_expired_sessions() -> None:
    now = time.time()
    expired = [
        sid for sid, data in _camera_sessions.items()
        if now - data.get("created_at", 0) > _SESSION_TTL_SECONDS
    ]
    for sid in expired:
        _camera_sessions.pop(sid, None)


class SessionCreateRequest(BaseModel):
    session_id: Optional[str] = None


class SessionCreateResponse(BaseModel):
    session_id: str
    created_at: float


class CameraUploadPayload(BaseModel):
    image: str = Field(description="Base64 DataURL or URL of captured photo")
    category: Optional[str] = Field(default="ao", description="Detected category e.g. ao, quan, giay")


class CameraStatusResponse(BaseModel):
    session_id: str
    status: str = Field(description="'waiting' | 'ready' | 'not_found'")
    image: Optional[str] = None
    category: Optional[str] = None


@router.post("/session", response_model=SessionCreateResponse, summary="Create or register a camera sync session")
def create_session(payload: Optional[SessionCreateRequest] = None) -> SessionCreateResponse:
    _cleanup_expired_sessions()
    now = time.time()
    import uuid
    sid = (payload.session_id.strip() if payload and payload.session_id else uuid.uuid4().hex[:8].upper())
    _camera_sessions[sid] = {
        "created_at": now,
        "image": None,
        "category": None,
        "ready": False,
    }
    return SessionCreateResponse(session_id=sid, created_at=now)


@router.post("/upload/{session_id}", summary="Mobile uploads captured photo")
def upload_photo(session_id: str, payload: CameraUploadPayload) -> dict:
    _cleanup_expired_sessions()
    sid = session_id.strip().upper()
    now = time.time()

    if sid not in _camera_sessions:
        # Tự động tạo session nếu mobile kết nối trước
        _camera_sessions[sid] = {
            "created_at": now,
            "image": None,
            "category": None,
            "ready": False,
        }

    _camera_sessions[sid]["image"] = payload.image
    _camera_sessions[sid]["category"] = payload.category or "ao"
    _camera_sessions[sid]["ready"] = True
    _camera_sessions[sid]["uploaded_at"] = now

    return {"status": "ok", "session_id": sid, "message": "Photo uploaded successfully"}


@router.get("/status/{session_id}", response_model=CameraStatusResponse, summary="Desktop polls photo upload status")
def get_status(session_id: str, consume: bool = False) -> CameraStatusResponse:
    _cleanup_expired_sessions()
    sid = session_id.strip().upper()

    if sid not in _camera_sessions:
        return CameraStatusResponse(session_id=sid, status="not_found")

    data = _camera_sessions[sid]
    if data.get("ready") and data.get("image"):
        res = CameraStatusResponse(
            session_id=sid,
            status="ready",
            image=data["image"],
            category=data.get("category"),
        )
        if consume:
            _camera_sessions.pop(sid, None)
        return res

    return CameraStatusResponse(session_id=sid, status="waiting")


@router.delete("/session/{session_id}", summary="Delete or close a camera session")
def delete_session(session_id: str) -> dict:
    sid = session_id.strip().upper()
    _camera_sessions.pop(sid, None)
    return {"status": "ok", "session_id": sid}

"""
BuildWise AI — File Upload Router
"""
import os
import uuid
import aiofiles
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form
from typing import Optional
from config import settings
from models.user import User
from services.jwt_service import get_current_user

router = APIRouter()

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_AUDIO_TYPES = {"audio/mpeg", "audio/wav", "audio/ogg", "audio/mp4"}


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    complaint_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Invalid image type. Allowed: JPEG, PNG, WebP, GIF")

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File too large. Max {settings.MAX_UPLOAD_SIZE_MB}MB")

    ext = file.filename.rsplit(".", 1)[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    save_path = os.path.join(settings.UPLOAD_DIR, "images", filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    async with aiofiles.open(save_path, "wb") as f:
        await f.write(content)

    file_url = f"/uploads/images/{filename}"
    return {"file_url": file_url, "file_name": filename, "file_type": "image", "size_bytes": len(content)}


@router.post("/audio")
async def upload_audio(
    file: UploadFile = File(...),
    complaint_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
):
    if file.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(status_code=400, detail="Invalid audio type")

    content = await file.read()
    ext = file.filename.rsplit(".", 1)[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    save_path = os.path.join(settings.UPLOAD_DIR, "audio", filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    async with aiofiles.open(save_path, "wb") as f:
        await f.write(content)

    transcription = None
    if settings.OPENAI_API_KEY:
        try:
            from openai import AsyncOpenAI
            oa_client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL,
            )
            with open(save_path, "rb") as audio_file:
                transcript = await oa_client.audio.transcriptions.create(
                    model="whisper-1", file=audio_file
                )
            transcription = transcript.text
        except Exception as e:
            import structlog
            structlog.get_logger().warning("Voice transcription failed", error=str(e))

    return {
        "file_url": f"/uploads/audio/{filename}",
        "file_name": filename,
        "file_type": "audio",
        "transcription": transcription,
        "complaint_id": complaint_id,
    }

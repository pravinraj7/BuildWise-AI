"""
BuildWise AI — Computer Vision Router (YOLOv8 Damage Detection)
"""
import os
import uuid
import aiofiles
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from config import settings
from models.user import User
from services.jwt_service import get_current_user

router = APIRouter()


@router.post("/detect")
async def detect_damage(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Upload an image and detect building damage using YOLOv8."""
    allowed = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Only JPEG/PNG/WebP images allowed")

    content = await file.read()
    ext = file.filename.rsplit(".", 1)[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    save_path = os.path.join(settings.UPLOAD_DIR, "images", filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    async with aiofiles.open(save_path, "wb") as f:
        await f.write(content)

    # Run YOLO detection
    from services.cv_service import detect_building_damage
    result = await detect_building_damage(save_path, filename)

    return {
        "original_image_url": f"/uploads/images/{filename}",
        "annotated_image_url": result.get("annotated_url"),
        "detections": result.get("detections", []),
        "summary": result.get("summary", {}),
        "confidence_threshold": 0.5,
        "model": "YOLOv8",
    }


@router.get("/classes")
async def get_detection_classes(current_user: User = Depends(get_current_user)):
    """Return list of detectable damage categories."""
    return {
        "classes": [
            {"id": 0, "name": "pipe_leakage", "label": "Pipe Leakage", "color": "#3b82f6"},
            {"id": 1, "name": "wall_crack", "label": "Wall Crack", "color": "#ef4444"},
            {"id": 2, "name": "broken_switch", "label": "Broken Switch", "color": "#f59e0b"},
            {"id": 3, "name": "broken_window", "label": "Broken Window", "color": "#8b5cf6"},
            {"id": 4, "name": "electrical_damage", "label": "Electrical Damage", "color": "#ec4899"},
            {"id": 5, "name": "ac_damage", "label": "AC Damage", "color": "#06b6d4"},
            {"id": 6, "name": "ceiling_damage", "label": "Ceiling Damage", "color": "#84cc16"},
            {"id": 7, "name": "fire_damage", "label": "Fire Damage", "color": "#f97316"},
            {"id": 8, "name": "water_damage", "label": "Water Damage", "color": "#0ea5e9"},
            {"id": 9, "name": "structural_damage", "label": "Structural Damage", "color": "#dc2626"},
        ]
    }

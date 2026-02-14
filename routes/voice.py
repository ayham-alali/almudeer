"""
Al-Mudeer - Voice Message Routes
Handles voice message upload, transcription, and retrieval
Uses S3 for production storage, local for development
"""

import os
import uuid
import tempfile
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel

from dependencies import get_license_from_header

from services.file_storage_service import get_file_storage
from services.agora_service import AGORA_APP_ID
from logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/voice", tags=["Voice Messages"])

# File storage service instance
file_storage = get_file_storage()


class VoiceUploadResponse(BaseModel):
    success: bool
    audio_url: Optional[str] = None
    duration: Optional[int] = None  # seconds
    error: Optional[str] = None


# S3 and local save functions are now handled by FileStorageService
# (Keeping internal logic if needed, but the service provides a better abstraction)


async def get_audio_duration(file_data: bytes, filename: str) -> int:
    """
    Get audio duration in seconds.
    Uses mutagen library if available, otherwise estimates.
    """
    try:
        from mutagen import File as MutagenFile
        from mutagen.ogg import OggFileType
        from mutagen.mp3 import MP3
        from mutagen.mp4 import MP4
        
        # Save to temp file for mutagen
        suffix = os.path.splitext(filename)[1] or '.ogg'
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(file_data)
            tmp_path = tmp.name
        
        try:
            audio = MutagenFile(tmp_path)
            if audio and audio.info:
                return int(audio.info.length)
        finally:
            os.unlink(tmp_path)
            
    except ImportError:
        logger.debug("mutagen not installed, estimating duration")
    except Exception as e:
        logger.debug(f"Could not get exact duration: {e}")
    
    # Estimate duration from file size (rough: ~16KB per second for OGG)
    size_kb = len(file_data) / 1024
    estimated_duration = max(1, int(size_kb / 16))
    return estimated_duration


@router.post("/upload", response_model=VoiceUploadResponse)
async def upload_voice_message(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_license_from_header)
):
    """
    Upload a voice message, transcribe it, and return the URL.
    
    - Accepts: audio/ogg, audio/webm, audio/mp3, audio/wav, audio/m4a
    - Transcribes using OpenAI Whisper
    - Stores in S3 (production) or local filesystem (development)
    
    Returns:
        - audio_url: URL to access the audio file
        - duration: Audio duration in seconds
        - transcript: Transcribed text (Arabic)
    """
    # Validate file type
    allowed_types = ['audio/ogg', 'audio/webm', 'audio/mp3', 'audio/mpeg', 'audio/wav', 'audio/x-m4a', 'audio/mp4']
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
        )
    
    try:
        # Read file data
        file_data = await file.read()
        
        if len(file_data) == 0:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Generate unique filename
        ext = os.path.splitext(file.filename)[1] or '.ogg'
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        
        # Save file using storage service
        _, audio_url = file_storage.save_file(
            content=file_data,
            filename=file.filename,
            mime_type=file.content_type,
            subfolder="voice"
        )
        
        # Get duration
        duration = await get_audio_duration(file_data, unique_filename)
        
        logger.info(f"Voice upload complete: {audio_url}, duration={duration}s")
        
        return VoiceUploadResponse(
            success=True,
            audio_url=audio_url,
            duration=duration
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice upload failed: {e}")
        return VoiceUploadResponse(
            success=False,
            error=f"Upload failed: {str(e)}"
        )




# ============ Voice Call Signaling (Agora) ============

class CallInviteRequest(BaseModel):
    recipient_username: str
    channel_name: Optional[str] = None

@router.post("/call/invite")
async def invite_to_call(
    data: CallInviteRequest,
    license: dict = Depends(get_license_from_header)
):
    """
    Send a call invitation signal to a specific user.
    """
    from services.websocket_manager import get_websocket_manager, WebSocketMessage
    from db_helper import get_db, fetch_one
    
    sender_username = license.get("username")
    if not sender_username:
        # Fallback if username not in license dict
        async with get_db() as db:
            row = await fetch_one(db, "SELECT username, company_name FROM license_keys WHERE id = ?", [license["license_id"]])
            sender_username = row["username"] if row else "mudeer_user"
            sender_company = row["company_name"] if row else "Al-Mudeer User"
    else:
        sender_company = license.get("company_name", "Al-Mudeer User")

    # 1. Find the recipient's license holder
    async with get_db() as db:
        recipient = await fetch_one(db, "SELECT id FROM license_keys WHERE username = ?", [data.recipient_username])
        if not recipient:
            raise HTTPException(status_code=404, detail="المستخدم المستهدف غير موجود")
        
    # 2. Generate or use provided channel name
    channel_name = data.channel_name or f"call_{sender_username}_{data.recipient_username}_{int(datetime.utcnow().timestamp())}"
    
    # Generate Agora Token
    from services.agora_service import AgoraService
    agora_token = AgoraService.generate_token(channel_name)
    
    # 3. Broadcast signal via WebSocket
    manager = get_websocket_manager()
    await manager.send_to_license(recipient["id"], WebSocketMessage(
        event="call_invite",
        data={
            "sender_username": sender_username,
            "sender_name": sender_company,
            "channel_name": channel_name,
            "type": "voice",
            "app_id": AGORA_APP_ID,
            "agora_token": agora_token
        }
    ))
    
    # 4. Trigger FCM push for mobile background handling
    try:
        from services.fcm_mobile_service import send_fcm_to_license
        await send_fcm_to_license(
            recipient["id"], 
            "مكالمة واردة", 
            f"مكالمة من {sender_company}", 
            data={
                "type": "voice_call",
                "channel_name": channel_name,
                "sender_username": sender_username,
                "sender_name": sender_company,
                "agora_token": agora_token,
                "app_id": AGORA_APP_ID
            },
            sound="call_ringtone.mp3"
        )
    except Exception as e:
        logger.error(f"Failed to send call push notification: {e}")

    return {
        "success": True, 
        "channel_name": channel_name, 
        "agora_token": agora_token,
        "app_id": AGORA_APP_ID
    }

@router.post("/call/cancel")
async def cancel_call(
    data: CallInviteRequest,
    license: dict = Depends(get_license_from_header)
):
    """
    Cancel an outgoing call invitation (hang up before answer).
    Signals the recipient to stop ringing.
    """
    sender_username = license.get("username") or "mudeer_user"
    sender_company = license.get("company_name", "Al-Mudeer User")
    
    async with get_db() as db:
        recipient = await fetch_one(db, "SELECT id FROM license_keys WHERE username = ?", [data.recipient_username])
        if not recipient:
            return {"success": False, "detail": "Recipient not found"}

    # Signal recipient via WebSocket
    manager = get_websocket_manager()
    await manager.send_to_license(recipient["id"], WebSocketMessage(
        event="call_cancel",
        data={
            "sender_username": sender_username,
            "channel_name": data.channel_name
        }
    ))

    # Trigger FCM to dismiss notification (optional, based on mobile implementation)
    try:
        from services.fcm_mobile_service import send_fcm_to_license
        await send_fcm_to_license(
            recipient["id"],
            "مكالمة فائتة",
            f"مكالمة فائتة من {sender_company}",
            data={
                "type": "call_cancel",
                "channel_name": data.channel_name,
                "sender_username": sender_username
            }
        )
    except Exception as e:
        logger.error(f"Failed to send call cancel notification: {e}")

    return {"success": True}


@router.get("/call/token")
async def get_call_token(
    channel_name: str,
    uid: int = 0,
    license: dict = Depends(get_license_from_header)
):
    """
    Generate an Agora RTC token for the given channel.
    """
    from services.agora_service import AgoraService
    
    token = AgoraService.generate_token(channel_name, uid=uid)
    if not token:
        raise HTTPException(status_code=500, detail="فشل في إنشاء مفتاح الوصول للمكالمة")
        
    return {
        "success": True,
        "token": token,
        "app_id": AgoraService.get_app_id(),
        "channel_name": channel_name
    }


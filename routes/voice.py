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

from dependencies import get_current_user
from services.voice_service import transcribe_voice_message
from logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/voice", tags=["Voice Messages"])

# Storage configuration
USE_S3 = os.getenv("USE_S3_STORAGE", "false").lower() == "true"
S3_BUCKET = os.getenv("S3_BUCKET", "almudeer-voice")
S3_REGION = os.getenv("AWS_REGION", "me-south-1")  # Bahrain region
LOCAL_UPLOAD_DIR = os.getenv("UPLOAD_DIR", "static/uploads/voice")

# Ensure local upload directory exists
os.makedirs(LOCAL_UPLOAD_DIR, exist_ok=True)


class VoiceUploadResponse(BaseModel):
    success: bool
    audio_url: Optional[str] = None
    duration: Optional[int] = None  # seconds
    transcript: Optional[str] = None
    error: Optional[str] = None


async def save_to_s3(file_data: bytes, filename: str, content_type: str) -> str:
    """
    Save file to S3 bucket.
    Returns the public URL of the uploaded file.
    """
    try:
        import boto3
        from botocore.exceptions import ClientError
        
        s3_client = boto3.client(
            's3',
            region_name=S3_REGION,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        
        # Upload to S3
        key = f"voice/{datetime.utcnow().strftime('%Y/%m/%d')}/{filename}"
        
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=file_data,
            ContentType=content_type,
            ACL='public-read'
        )
        
        # Return public URL
        url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{key}"
        logger.info(f"Uploaded voice to S3: {url}")
        return url
        
    except ImportError:
        logger.warning("boto3 not installed, falling back to local storage")
        raise
    except ClientError as e:
        logger.error(f"S3 upload failed: {e}")
        raise


async def save_locally(file_data: bytes, filename: str) -> str:
    """
    Save file to local filesystem.
    Returns the relative URL path.
    """
    filepath = os.path.join(LOCAL_UPLOAD_DIR, filename)
    
    with open(filepath, 'wb') as f:
        f.write(file_data)
    
    # Return URL path (assumes static files are served)
    url = f"/static/uploads/voice/{filename}"
    logger.info(f"Saved voice locally: {url}")
    return url


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
    current_user: dict = Depends(get_current_user)
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
        
        # Save file
        try:
            if USE_S3:
                audio_url = await save_to_s3(file_data, unique_filename, file.content_type)
            else:
                audio_url = await save_locally(file_data, unique_filename)
        except Exception as e:
            logger.error(f"Storage error: {e}")
            # Fallback to local if S3 fails
            audio_url = await save_locally(file_data, unique_filename)
        
        # Get duration
        duration = await get_audio_duration(file_data, unique_filename)
        
        # Transcribe
        transcript_result = await transcribe_voice_message(file_data, file.filename or "audio.ogg")
        transcript = transcript_result.get("text", "") if transcript_result.get("success") else ""
        
        logger.info(f"Voice upload complete: {audio_url}, duration={duration}s, transcript_len={len(transcript)}")
        
        return VoiceUploadResponse(
            success=True,
            audio_url=audio_url,
            duration=duration,
            transcript=transcript
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice upload failed: {e}")
        return VoiceUploadResponse(
            success=False,
            error=f"Upload failed: {str(e)}"
        )


@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Transcribe an audio file without storing it.
    Useful for previewing transcription before sending.
    """
    try:
        file_data = await file.read()
        
        if len(file_data) == 0:
            raise HTTPException(status_code=400, detail="Empty file")
        
        result = await transcribe_voice_message(file_data, file.filename or "audio.ogg")
        
        if result.get("success"):
            return {
                "success": True,
                "text": result.get("text", ""),
                "language": result.get("language", "ar"),
                "duration": result.get("duration", 0)
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Transcription failed")
            }
            
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

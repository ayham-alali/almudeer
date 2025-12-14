"""
Al-Mudeer Voice Message Transcription Service
Supports Whisper (local or API) for Arabic voice transcription
"""

import os
import tempfile
import base64
from typing import Optional
import httpx

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
USE_LOCAL_WHISPER = os.getenv("USE_LOCAL_WHISPER", "false").lower() == "true"


async def transcribe_audio_openai(audio_data: bytes, filename: str = "audio.ogg") -> dict:
    """
    Transcribe audio using OpenAI Whisper API
    Supports: mp3, mp4, mpeg, mpga, m4a, wav, webm, ogg
    """
    if not OPENAI_API_KEY:
        return {
            "success": False,
            "error": "OpenAI API key not configured. Set OPENAI_API_KEY environment variable."
        }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Prepare multipart form data
            files = {
                "file": (filename, audio_data, "audio/ogg"),
                "model": (None, "whisper-1"),
                "language": (None, "ar"),  # Arabic
                "response_format": (None, "verbose_json"),
            }
            
            response = await client.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                files=files
            )
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"API Error: {response.text}"
                }
            
            data = response.json()
            
            return {
                "success": True,
                "text": data.get("text", ""),
                "language": data.get("language", "ar"),
                "duration": data.get("duration", 0),
                "segments": data.get("segments", [])
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Transcription failed: {str(e)}"
        }


async def transcribe_audio_local(audio_data: bytes, filename: str = "audio.ogg") -> dict:
    """
    Transcribe audio using local Whisper model
    Requires: pip install openai-whisper
    """
    try:
        import whisper
        
        # Save audio to temp file
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as f:
            f.write(audio_data)
            temp_path = f.name
        
        try:
            # Load model (uses cache after first download)
            model = whisper.load_model("small")  # Options: tiny, base, small, medium, large
            
            # Transcribe
            result = model.transcribe(
                temp_path,
                language="ar",
                task="transcribe"
            )
            
            return {
                "success": True,
                "text": result.get("text", "").strip(),
                "language": result.get("language", "ar"),
                "duration": 0,  # Not available in basic transcribe
                "segments": result.get("segments", [])
            }
            
        finally:
            # Clean up temp file
            os.unlink(temp_path)
            
    except ImportError:
        return {
            "success": False,
            "error": "Local Whisper not installed. Run: pip install openai-whisper"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Local transcription failed: {str(e)}"
        }


async def transcribe_voice_message(
    audio_data: bytes,
    filename: str = "audio.ogg"
) -> dict:
    """
    Main transcription function - uses OpenAI API or local Whisper
    """
    if USE_LOCAL_WHISPER:
        return await transcribe_audio_local(audio_data, filename)
    else:
        return await transcribe_audio_openai(audio_data, filename)


async def transcribe_from_base64(base64_audio: str) -> dict:
    """
    Transcribe audio from base64 encoded string
    """
    try:
        # Remove data URL prefix if present
        if "," in base64_audio:
            base64_audio = base64_audio.split(",")[1]
        
        audio_data = base64.b64decode(base64_audio)
        return await transcribe_voice_message(audio_data)
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Invalid base64 audio: {str(e)}"
        }


async def transcribe_from_url(audio_url: str) -> dict:
    """
    Transcribe audio from URL
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(audio_url)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to download audio: {response.status_code}"
                }
            
            audio_data = response.content
            
            # Get filename from URL
            filename = audio_url.split("/")[-1].split("?")[0] or "audio.ogg"
            
            return await transcribe_voice_message(audio_data, filename)
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to fetch audio: {str(e)}"
        }


# Utility to estimate transcription time saved
def estimate_time_saved(duration_seconds: float) -> int:
    """
    Estimate how much time was saved by auto-transcription
    Assumes reading is 3x faster than listening
    Plus 30 seconds for manual transcription effort
    """
    listening_time = duration_seconds
    reading_time = duration_seconds / 3
    manual_transcription = duration_seconds * 2  # Typing takes 2x audio duration
    
    saved = listening_time + manual_transcription - reading_time
    return int(max(saved, 30))  # Minimum 30 seconds saved


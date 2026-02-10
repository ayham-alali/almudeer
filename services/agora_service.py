import os
import time
from typing import Optional
from agora_token_builder import RtcTokenBuilder
from logging_config import get_logger

logger = get_logger(__name__)

# Agora Configuration
AGORA_APP_ID = os.getenv("AGORA_APP_ID")
AGORA_APP_CERTIFICATE = os.getenv("AGORA_APP_CERTIFICATE")

class AgoraService:
    """
    Service for interacting with Agora.io.
    Mainly used for generating RTC tokens for voice calls.
    """
    
    @staticmethod
    def generate_token(channel_name: str, uid: int = 0, role: int = 1, expiration_time_in_seconds: int = 3600) -> Optional[str]:
        """
        Generate an RTC token for a specific channel.
        
        Args:
            channel_name: Unique name for the call channel.
            uid: User ID (0 means Agora will assign one or it's a generic token).
            role: Role of the user (1 for publisher/host, 2 for subscriber/audience).
            expiration_time_in_seconds: Token validity duration.
            
        Returns:
            The generated token string or None if configuration is missing.
        """
        if not AGORA_APP_ID or not AGORA_APP_CERTIFICATE:
            logger.error("AGORA_APP_ID or AGORA_APP_CERTIFICATE not configured in environment")
            return None
        
        current_time = int(time.time())
        privilege_expired_ts = current_time + expiration_time_in_seconds
        
        try:
            token = RtcTokenBuilder.buildTokenWithUid(
                AGORA_APP_ID, 
                AGORA_APP_CERTIFICATE, 
                channel_name, 
                uid, 
                role, 
                privilege_expired_ts
            )
            return token
        except Exception as e:
            logger.error(f"Failed to generate Agora token: {e}")
            return None

    @staticmethod
    def get_app_id() -> Optional[str]:
        """Return the Agora App ID for frontend use."""
        return AGORA_APP_ID

"""
Al-Mudeer - Smart Reaction Service
Determines if and when AI should react to messages like a human would.
Reactions are only added after response is sent, and only when appropriate.
"""

import random
from typing import Optional, Tuple
from logging_config import get_logger

logger = get_logger(__name__)

# Reaction mapping based on context
REACTION_RULES = {
    # Sentiment-based reactions (only positive reactions to avoid seeming passive-aggressive)
    "gratitude": ["❤️", "🙏", "😊"],  # شكراً، ممتنين، جزاك الله
    "positive": ["👍", "❤️", "😊"],   # General positive
    "humor": ["😄", "😂"],             # Jokes, funny
    "celebration": ["🎉", "🥳", "👏"],  # Good news, achievement
    "agreement": ["👍", "✅"],          # Confirming, accepting
    "appreciation": ["❤️", "🙏", "✨"], # Praising the service
    
    # Intent-based selective reactions
    "completed_request": ["✅", "👍"],  # When we fulfilled their request
    "resolved_complaint": ["🙏", "💚"], # When we resolved an issue
}

# Keywords that suggest gratitude (Arabic)
GRATITUDE_KEYWORDS = [
    "شكرا", "شكراً", "مشكور", "يعطيك العافية", "ممتنين", "جزاك الله",
    "الله يعطيك", "يسلمو", "تسلم", "الله يخليك", "ما قصرت", "ما قصرتي",
    "thank", "thanks", "thx", "appreciated"
]

# Keywords suggesting celebration/good news
CELEBRATION_KEYWORDS = [
    "مبروك", "تهانينا", "فزنا", "نجحنا", "الحمد لله", "تم",
    "ممتاز", "رائع", "عظيم", "exciting", "great news", "wonderful"
]

# Keywords suggesting humor
HUMOR_KEYWORDS = [
    "هههه", "😂", "😄", "lol", "haha", "مضحك", "نكتة"
]


def should_react_to_message(
    message_body: str,
    sentiment: Optional[str] = None,
    intent: Optional[str] = None,
    is_final_message: bool = True
) -> Tuple[bool, Optional[str]]:
    """
    Determine if AI should react to this message and with which emoji.
    
    Rules for human-like reactions:
    1. Don't react to every message (feels robotic)
    2. React to gratitude, celebration, humor (natural human response)
    3. React after completing a request (confirmation)
    4. Skip reactions on complaints, negative sentiment (avoid seeming dismissive)
    5. Random chance factor (20-40% of eligible messages get reactions)
    
    Args:
        message_body: The customer's message text
        sentiment: Detected sentiment (positive, negative, neutral)
        intent: Detected intent (inquiry, complaint, etc.)
        is_final_message: Whether this is the last customer message in the conversation
        
    Returns:
        Tuple of (should_react: bool, emoji: Optional[str])
    """
    body_lower = message_body.lower()
    
    # RULE 1: Never react to negative sentiment or complaints
    if sentiment and sentiment.lower() in ["negative", "سلبي"]:
        return False, None
    if intent and intent.lower() in ["شكوى", "complaint"]:
        return False, None
    
    # RULE 2: Check for gratitude keywords (high chance to react)
    if any(keyword in body_lower for keyword in GRATITUDE_KEYWORDS):
        if random.random() < 0.6:  # 60% chance to react to gratitude
            emoji = random.choice(REACTION_RULES["gratitude"])
            logger.info(f"Smart reaction: gratitude detected -> {emoji}")
            return True, emoji
    
    # RULE 3: Check for celebration keywords
    if any(keyword in body_lower for keyword in CELEBRATION_KEYWORDS):
        if random.random() < 0.5:  # 50% chance
            emoji = random.choice(REACTION_RULES["celebration"])
            logger.info(f"Smart reaction: celebration detected -> {emoji}")
            return True, emoji
    
    # RULE 4: Check for humor
    if any(keyword in body_lower for keyword in HUMOR_KEYWORDS):
        if random.random() < 0.4:  # 40% chance
            emoji = random.choice(REACTION_RULES["humor"])
            logger.info(f"Smart reaction: humor detected -> {emoji}")
            return True, emoji
    
    # RULE 5: Positive sentiment with service completion intent
    if sentiment and sentiment.lower() in ["positive", "إيجابي"]:
        if intent and intent.lower() in ["طلب خدمة", "متابعة", "service"]:
            if random.random() < 0.3:  # 30% chance
                emoji = random.choice(REACTION_RULES["completed_request"])
                logger.info(f"Smart reaction: positive service completion -> {emoji}")
                return True, emoji
    
    # RULE 6: General positive messages (low chance)
    if sentiment and sentiment.lower() in ["positive", "إيجابي"]:
        if random.random() < 0.15:  # 15% chance for general positive
            emoji = random.choice(REACTION_RULES["positive"])
            logger.info(f"Smart reaction: general positive -> {emoji}")
            return True, emoji
    
    # Default: No reaction
    return False, None


async def add_smart_reaction(
    message_id: int,
    license_id: int,
    message_body: str,
    sentiment: Optional[str] = None,
    intent: Optional[str] = None
) -> bool:
    """
    Add a smart reaction to a message if appropriate.
    Called after response is sent.
    
    Returns True if reaction was added, False otherwise.
    """
    from models.reactions import add_reaction
    
    should_react, emoji = should_react_to_message(
        message_body=message_body,
        sentiment=sentiment,
        intent=intent
    )
    
    if should_react and emoji:
        result = await add_reaction(
            message_id=message_id,
            license_id=license_id,
            emoji=emoji,
            user_type="agent"  # AI acts as agent
        )
        
        if result["success"]:
            logger.info(f"Added smart reaction {emoji} to message {message_id}")
            
            # Broadcast to frontend for instant UI update
            try:
                from services.websocket_manager import broadcast_reaction_added
                await broadcast_reaction_added(
                    license_id=license_id,
                    message_id=message_id,
                    emoji=emoji,
                    user_type="agent"
                )
            except Exception as e:
                logger.error(f"Failed to broadcast reaction: {e}")

            # Send Mobile Push Notification
            try:
                from services.fcm_mobile_service import send_fcm_to_license
                # Truncate message body for notification
                preview = message_body[:50] + "..." if len(message_body) > 50 else message_body
                
                await send_fcm_to_license(
                    license_id=license_id,
                    title="New Reaction",
                    body=f"AI Agent reacted {emoji} to: {preview}",
                    data={
                        "type": "reaction_added",
                        "message_id": str(message_id),
                        "emoji": emoji,
                        "click_action": "FLUTTER_NOTIFICATION_CLICK"
                    }
                )
            except Exception as e:
                logger.error(f"Failed to send FCM for smart reaction: {e}")
                
            return True
        else:
            logger.warning(f"Failed to add smart reaction: {result.get('error')}")
    
    return False

"""
Al-Mudeer - Message Filtering System
Advanced filtering rules for messages before processing
"""

from typing import Dict, List, Optional, Callable
from datetime import datetime
import re
from logging_config import get_logger

logger = get_logger(__name__)


class MessageFilter:
    """Filter messages based on configurable rules"""
    
    def __init__(self):
        self.rules: List[Callable] = []
    
    def add_rule(self, rule_func: Callable):
        """Add a filtering rule"""
        self.rules.append(rule_func)
    
    def should_process(self, message: Dict) -> tuple[bool, Optional[str]]:
        """
        Check if message should be processed.
        
        Returns:
            Tuple of (should_process, reason_if_rejected)
        """
        for rule in self.rules:
            result = rule(message)
            if isinstance(result, tuple):
                should_process, reason = result
                if not should_process:
                    return False, reason
            elif not result:
                return False, "Filtered by rule"
        
        return True, None


# ============ Built-in Filter Rules ============

def filter_spam(message: Dict) -> tuple[bool, Optional[str]]:
    """Filter spam messages"""
    original_body = message.get("body", "") or message.get("text", "")
    body = original_body.lower()
    
    # Common spam indicators
    spam_keywords = [
        "click here", "limited time", "act now", "urgent action required",
        "you have won", "congratulations", "free money", "click this link",
        "اضغط هنا", "عرض محدود", "فوز", "جائزة", "مجاني"
    ]
    
    # Check for excessive links
    link_count = len(re.findall(r'http[s]?://', body))
    
    # Check for excessive caps
    caps_ratio = sum(1 for c in original_body if c.isupper()) / max(len(original_body), 1)
    
    # Spam score
    spam_score = 0
    if any(keyword in body for keyword in spam_keywords):
        spam_score += 2
    if link_count > 3:
        spam_score += 3  # Instant fail for > 3 links
    if caps_ratio > 0.5 and len(body) > 50:
        spam_score += 1
    
    if spam_score >= 3:
        return False, "Spam detected"
    
    return True, None


def filter_empty(message: Dict) -> tuple[bool, Optional[str]]:
    """Filter empty messages"""
    body = message.get("body", "").strip()
    attachments = message.get("attachments", [])
    
    # Allow messages with attachments even if body is empty/short (e.g., image-only)
    if attachments and len(attachments) > 0:
        return True, None
    
    # Allow any non-empty message (including 1-letter messages)
    if len(body) < 1:
        return False, "Message is empty"
    
    return True, None


def filter_duplicate(message: Dict, recent_messages: List[Dict], time_window_minutes: int = 5) -> tuple[bool, Optional[str]]:
    """Filter duplicate messages from same sender"""
    sender = message.get("sender_contact") or message.get("sender_id")
    body = message.get("body", "").strip()[:100]  # First 100 chars
    
    if not sender:
        return True, None
    
    # Check recent messages
    now = datetime.now()
    for recent in recent_messages:
        if recent.get("sender_contact") == sender or recent.get("sender_id") == sender:
            recent_body = recent.get("body", "").strip()[:100]

            raw_received = recent.get("received_at")
            if isinstance(raw_received, str):
                try:
                    recent_time = datetime.fromisoformat(raw_received)
                except ValueError:
                    recent_time = now
            elif isinstance(raw_received, datetime):
                recent_time = raw_received
            else:
                recent_time = now
            
            # Check if same content and within time window
            if recent_body == body:
                time_diff = (now - recent_time).total_seconds() / 60
                if time_diff < time_window_minutes:
                    return False, "Duplicate message"
    
    return True, None


def filter_blocked_senders(message: Dict, blocked_list: List[str]) -> tuple[bool, Optional[str]]:
    """Filter messages from blocked senders"""
    sender = message.get("sender_contact") or message.get("sender_id", "")
    
    if sender in blocked_list:
        return False, "Sender is blocked"
    
    return True, None

def filter_automated_messages(message: Dict) -> tuple[bool, Optional[str]]:
    """
    Filter automated messages (OTP, Marketing, System Info, Ads, Special Offers, 
    Account Info, Warnings, Newsletters, Transactional).
    
    Returns (True, None) if message is CLEAN (from a real customer).
    Returns (False, Reason) if message should be BLOCKED (automated/marketing).
    """
    body = message.get("body", "").lower()
    sender_contact = (message.get("sender_contact") or "").lower()
    sender_name = (message.get("sender_name") or "").lower()
    # Support tests that use different keys
    if not body: body = (message.get("text") or message.get("body") or "").lower()
    if not sender_contact: sender_contact = (message.get("sender_id") or message.get("from") or message.get("sender_contact") or "").lower()
    
    # Combined text for keyword matching
    subject = message.get("subject", "").lower()
    full_text = f"{body} {subject} {sender_name} {sender_contact}"

    # 1. Check for Automated Senders (Email patterns) - PRIORITIZED
    automated_sender_patterns = [
        r"^noreply@", r"^no-reply@", r"^no\.reply@",
        r"^notifications?@", r"^newsletter@", r"^newsletters@",
        r"^marketing@", r"^promo@", r"^promotions?@",
        r"^ads?@", r"^advertising@", r"^campaign@",
        r"^info@", r"^support@.*noreply", r"^alerts?@",
        r"^security@", r"^account@", r"^billing@",
        r"^mailer-daemon@", r"^postmaster@", r"^bounce@",
        r"^updates?@", r"^news@", r"^digest@",
        r"^subscriptions?@", r"^automated@", r"^system@",
        r"^donotreply@", r"^do-not-reply@", r"^reply-.*@",
        r"^help@", r"^welcome@", r"^hello@", r"^team@",
        r"^account-security@", r"^account-security-noreply@",
        r"^elsa@", r"^support@", r"^sales@",
        r"@.*\.noreply\.", r"@bounce\.",
        r"@mailer\.", r"@notifications?\.",
        r"@campaign\.", r"@newsletter\.", r"@promo\.",
        r"@help\.",
    ]
    for pattern in automated_sender_patterns:
        if re.search(pattern, sender_contact):
            return False, "Automated: Sender pattern detected"

    # 2. Check for specific Marketing/Newsletter patterns
    marketing_patterns = [
        (r"خصم", "Marketing"), (r"عرض", "Marketing"), (r"اشتراك", "Marketing"), (r"مجانا", "Marketing"), 
        (r"توفير", "Marketing"), (r"هدية", "Marketing"), (r"كوبون", "Marketing"),
        (r"discount", "Marketing"), (r"offer", "Marketing"), (r"subscribe", "Marketing"), 
        (r"free", "Marketing"), (r"save", "Marketing"), (r"gift", "Marketing"), 
        (r"coupon", "Marketing"), (r"promo", "Marketing"), (r"marketing", "Marketing"), 
        (r"sale", "Marketing"), (r"limited time", "Marketing"), (r"buy now", "Marketing"), 
        (r"newsletter", "Newsletter"), (r"digest", "Newsletter")
    ]
    for pattern, reason_key in marketing_patterns:
        if re.search(pattern, full_text):
            return False, f"Marketing: {reason_key} found"

    # 3. Check for Transactional/OTP/Account patterns
    transactional_patterns = [
        (r"رمز التحقق", "OTP"), (r"رمز التفعيل", "OTP"), (r"كلمة المرور المؤقتة", "OTP"),
        (r"تم استلام طلبك", "Order"), (r"تم الشحن", "Shipping"), (r"فاتورة رقم", "Invoice"),
        (r"verification code", "OTP"), (r"one-time password", "OTP"), (r"security code", "OTP"),
        (r"reset your password", "Account"), (r"verify your account", "Account"),
        (r"order confirmation", "Order"), (r"order #", "Order"), (r"shipping update", "Shipping"),
        (r"payment received", "Payment"), (r"payment confirmation", "Payment"),
        (r"receipt for your", "Invoice"), (r"invoice #", "Invoice"),
        (r"security alert", "Security"), (r"do not reply", "Transactional"), (r"fraud alert", "Security"),
        (r"new login detected", "Account"), (r"device verification", "Security"),
        (r"your otp", "OTP"), (r"your code", "OTP"), 
        # Specific strict patterns
        (r"^otp$", "OTP"), (r"^code:", "OTP"),
    ]
    for pattern, reason_key in transactional_patterns:
        if re.search(pattern, full_text):
            return False, f"Transactional: {reason_key} found"

    # 4. Generic Sender ID pattern (Least specific)
    if sender_contact and re.search(r"^[a-zA-Z]{4,15}$", sender_contact) and not sender_contact.isdigit():
        # But wait, if it's a known support sender name, allowed
        if "support" in sender_name.lower() or "help" in sender_name.lower():
             pass
        else:
            return False, "Automated: Corporate sender ID detected"

    # ============ Spam Filtering logic starts here ============
    # Check if this is a private chat (based on metadata)
    is_group = message.get("is_group", False)
    is_channel_src = message.get("is_channel", False)
    is_private = not (is_group or is_channel_src)

    # Keywords that are common in REAL chats but also ads (False Positive risks)
    # We only block these in [NON-PRIVATE] chats
    marketing_risk_keywords = [
        "discount", "click here", "click below", "act now", "ad:", "save now",
        "best price", "clearance", "buy now", "shop now", "order now",
        "free shipping", "free trial", "free gift", "bonus",
        "you've been selected", "congratulations", "winner",
        "claim your", "redeem", "expires soon", "last chance",
        "خصم", "مجاني", "هدية", "جائزة", "فائز", "فوز", "احصل على"
    ]
        
    # Block risk keywords only in Groups/Channels
    if not is_private:
        if any(k in full_text for k in marketing_risk_keywords):
            return False, "Automated: Marketing/Ad (Group/Channel Content)"

    # Check for excessive links (Spam indicator)
    link_count = len(re.findall(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", body))
    if link_count >= 3:
        return False, "Spam: Excessive links detected"
    
    return True, None


def filter_keywords(message: Dict, keywords: List[str], mode: str = "block") -> tuple[bool, Optional[str]]:
    """
    Filter messages based on keywords.
    
    Args:
        message: Message dict
        keywords: List of keywords to check
        mode: "block" to block messages with keywords, "allow" to only allow messages with keywords
    """
    body = message.get("body", "").lower()
    
    has_keyword = any(keyword.lower() in body for keyword in keywords)
    
    if mode == "block" and has_keyword:
        return False, "Contains blocked keyword"
    
    if mode == "allow" and not has_keyword:
        return False, "Does not contain required keyword"
    
    return True, None


def filter_urgency(message: Dict, min_urgency: str = "normal") -> tuple[bool, Optional[str]]:
    """Filter messages based on urgency level"""
    urgency_levels = {"low": 0, "normal": 1, "high": 2, "urgent": 3}
    
    message_urgency = message.get("urgency", "normal").lower()
    min_level = urgency_levels.get(min_urgency.lower(), 1)
    msg_level = urgency_levels.get(message_urgency, 1)
    
    if msg_level < min_level:
        return False, f"Urgency too low (required: {min_urgency})"
    
    return True, None


def filter_chat_types(message: Dict) -> tuple[bool, Optional[str]]:
    """Filter messages from non-private chats (groups, channels)"""
    
    # 1. Check explicit flags (Passed from listeners)
    is_group = message.get("is_group", False)
    is_channel_src = message.get("is_channel", False)
    
    if is_group:
        return False, "Message blocked: Source is a Group"
        
    if is_channel_src:
        return False, "Message blocked: Source is a Channel"
        
    chat_type = message.get("chat_type")
    if chat_type and chat_type not in ["private", "sender"]: # sender is used by some internal logic
        return False, f"Message blocked: Chat type '{chat_type}' is not private"
    
    # 2. Check Telegram specific metadata blocks
    # Telegram channels sometimes come as messages from a user with ID equal to the linked chat ID
    # or negative IDs often indicate groups/channels in Telegram/MTProto
    sender_id = str(message.get("sender_id", ""))
    if sender_id.startswith("-100") or (sender_id.startswith("-") and len(sender_id) > 5):
        return False, "Message blocked: Sender ID indicates non-private entity"

    # 3. WhatsApp Checks
    channel = message.get("channel")
    if channel == "whatsapp":
        # If the sender phone ends in @g.us (rarely passed here but possible)
        sender_contact = message.get("sender_contact", "")
        if "g.us" in sender_contact:
             return False, "Message blocked: WhatsApp Group ID detected"

    return True, None


def filter_telegram_bots(message: Dict) -> tuple[bool, Optional[str]]:
    """
    Filter messages from Telegram Bots.
    Blocks promotional bots, gaming bots, and other automated accounts.
    """
    channel = message.get("channel", "")
    
    # Only apply to Telegram messages
    if channel not in ["telegram", "telegram_bot"]:
        return True, None
    
    # Check explicit is_bot flag (if passed from listener)
    if message.get("is_bot", False):
        return False, "Message blocked: Sender is a Telegram Bot"
    
    # Check sender_contact/sender_name patterns
    sender_contact = (message.get("sender_contact") or "").lower()
    sender_name = (message.get("sender_name") or "").lower()
    
    # Usernames ending with 'bot' are bots (Telegram convention)
    if sender_contact.endswith('bot') or sender_contact.startswith('@') and sender_contact[1:].endswith('bot'):
        return False, "Message blocked: Sender username indicates a Bot"
    
    # Names that are clearly bots
    bot_name_indicators = [
        "bot", "api", "notification", "alert", "update", "news",
        "game", "play-to", "crypto", "nft", "token", "airdrop"
    ]
    
    # Only block if name ENDS with bot or contains suspicious patterns
    if sender_name.endswith('bot') or sender_name.endswith(' bot'):
        return False, "Message blocked: Sender name indicates a Bot"
    
    # Check for gaming/crypto bot patterns in name
    for indicator in ['play-to', 'airdrop', 'crypto game', 'nft game']:
        if indicator in sender_name:
            return False, f"Message blocked: Sender name contains bot indicator '{indicator}'"
    
    return True, None



# ============ Filter Manager ============

class FilterManager:
    """Manage message filters for a license"""
    
    def __init__(self, license_id: int):
        self.license_id = license_id
        self.filter = MessageFilter()
        self._setup_default_filters()
    
    def _setup_default_filters(self):
        """Setup default filter rules"""
        self.filter.add_rule(filter_spam)
        self.filter.add_rule(filter_empty)
        # Add the new automated message filter by default
        self.filter.add_rule(filter_automated_messages)
        # Add group/channel filter
        self.filter.add_rule(filter_chat_types)
        # Add Telegram bot filter
        self.filter.add_rule(filter_telegram_bots)
    
    def add_custom_rule(self, rule_func: Callable):
        """Add a custom filter rule"""
        self.filter.add_rule(rule_func)
    
    def should_process(self, message: Dict, recent_messages: List[Dict] = None) -> tuple[bool, Optional[str]]:
        """Check if message should be processed"""
        # Add duplicate check if recent messages provided
        if recent_messages:
            duplicate_check = lambda msg: filter_duplicate(msg, recent_messages)
            self.filter.add_rule(duplicate_check)
        
        return self.filter.should_process(message)
    
    def get_blocked_senders(self) -> List[str]:
        """Get list of blocked senders for this license"""
        # This would typically come from database
        # For now, return empty list
        return []
    
    def get_keyword_filters(self) -> Dict:
        """Get keyword filter configuration"""
        # This would typically come from database
        return {
            "blocked_keywords": [],
            "required_keywords": [],
            "mode": "block"
        }


# ============ Integration with Agent ============

async def apply_filters(message: Dict, license_id: int, recent_messages: List[Dict] = None) -> tuple[bool, Optional[str]]:
    """
    Apply all filters to a message.
    
    Args:
        message: Message dictionary
        license_id: License ID for custom filter rules
        recent_messages: List of recent messages for duplicate detection
        
    Returns:
        Tuple of (should_process, reason_if_rejected)
    """
    filter_manager = FilterManager(license_id)
    
    # Load custom filters from database if needed
    # blocked_senders = filter_manager.get_blocked_senders()
    # if blocked_senders:
    #     filter_manager.add_custom_rule(
    #         lambda msg: filter_blocked_senders(msg, blocked_senders)
    #     )
    
    return filter_manager.should_process(message, recent_messages)


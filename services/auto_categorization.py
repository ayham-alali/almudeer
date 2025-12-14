"""
Al-Mudeer Auto-Categorization Service
Automatically tags messages by topic, product, and priority
Uses rule-based classification with Arabic NLP patterns
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class Priority(Enum):
    URGENT = "عاجل"
    HIGH = "عالي"
    NORMAL = "عادي"
    LOW = "منخفض"

class MessageCategory(Enum):
    INQUIRY = "استفسار"
    SERVICE_REQUEST = "طلب خدمة"
    COMPLAINT = "شكوى"
    FOLLOWUP = "متابعة"
    OFFER = "عرض"
    FEEDBACK = "تقييم"
    SUPPORT = "دعم فني"
    BILLING = "مالي"
    OTHER = "أخرى"

@dataclass
class CategoryResult:
    category: MessageCategory
    confidence: float
    tags: List[str]
    priority: Priority
    priority_score: int  # 1-100
    sentiment_score: float  # -1 to 1
    detected_products: List[str]
    detected_topics: List[str]
    suggested_folder: str
    auto_actions: List[str]

# Topic patterns for Arabic business messages
TOPIC_PATTERNS = {
    "pricing": {
        "keywords": ["سعر", "أسعار", "تكلفة", "ثمن", "كم سعر", "كم تكلفة", "عرض سعر"],
        "weight": 0.8
    },
    "delivery": {
        "keywords": ["توصيل", "شحن", "وصول", "تسليم", "موعد الوصول", "تتبع"],
        "weight": 0.7
    },
    "payment": {
        "keywords": ["دفع", "فاتورة", "حوالة", "تحويل", "قسط", "سداد", "ل.س", "دولار"],
        "weight": 0.8
    },
    "quality": {
        "keywords": ["جودة", "نوعية", "مواصفات", "ضمان", "صلاحية"],
        "weight": 0.6
    },
    "availability": {
        "keywords": ["متوفر", "توفر", "مخزون", "متاح", "هل يوجد"],
        "weight": 0.5
    },
    "technical": {
        "keywords": ["مشكلة", "خلل", "لا يعمل", "عطل", "صيانة", "تصليح", "تقني"],
        "weight": 0.9
    },
    "booking": {
        "keywords": ["حجز", "موعد", "ميعاد", "تحديد موعد", "جدول"],
        "weight": 0.7
    },
    "cancellation": {
        "keywords": ["إلغاء", "رجوع", "استرجاع", "استرداد", "إعادة"],
        "weight": 0.8
    }
}

# Priority indicators
URGENT_INDICATORS = [
    "عاجل", "فوري", "فوراً", "الآن", "بأسرع", "ضروري", "طارئ",
    "سريع", "بسرعة", "مستعجل", "اليوم"
]

LOW_PRIORITY_INDICATORS = [
    "لاحقاً", "عندما يتسنى", "متى ما أمكن", "لا استعجال",
    "بالوقت المناسب", "دون استعجال"
]

# Sentiment indicators
POSITIVE_INDICATORS = [
    "شكراً", "شكرا", "ممتاز", "رائع", "جميل", "مسرور", "سعيد",
    "أحسنتم", "بارك الله", "جزاكم الله", "مبدعين", "احترافي"
]

NEGATIVE_INDICATORS = [
    "غاضب", "مستاء", "محبط", "للأسف", "سيء", "سيئ", "مخيب",
    "خيبة", "لم أتوقع", "محزن", "مزعج", "فاشل", "ضعيف"
]


def extract_tags(message: str) -> List[str]:
    """Extract relevant tags from message"""
    tags = []
    message_lower = message.lower()
    
    for topic, config in TOPIC_PATTERNS.items():
        for keyword in config["keywords"]:
            if keyword in message_lower or keyword in message:
                tags.append(topic)
                break
    
    return list(set(tags))


def calculate_priority_score(message: str) -> Tuple[Priority, int]:
    """Calculate message priority and score"""
    score = 50  # Base score
    
    # Check for urgent indicators
    for indicator in URGENT_INDICATORS:
        if indicator in message:
            score += 20
            break
    
    # Check for low priority indicators
    for indicator in LOW_PRIORITY_INDICATORS:
        if indicator in message:
            score -= 20
            break
    
    # Check for complaint indicators
    complaint_words = ["شكوى", "مشكلة", "خلل", "عطل", "لم يعمل"]
    for word in complaint_words:
        if word in message:
            score += 15
            break
    
    # Check for VIP indicators (repeat customer, big order)
    vip_indicators = ["عميل دائم", "طلبية كبيرة", "شركة", "مؤسسة"]
    for indicator in vip_indicators:
        if indicator in message:
            score += 10
            break
    
    # Clamp score
    score = max(10, min(100, score))
    
    # Determine priority level
    if score >= 80:
        priority = Priority.URGENT
    elif score >= 60:
        priority = Priority.HIGH
    elif score >= 40:
        priority = Priority.NORMAL
    else:
        priority = Priority.LOW
    
    return priority, score


def calculate_sentiment(message: str) -> float:
    """Calculate sentiment score from -1 (negative) to 1 (positive)"""
    positive_count = sum(1 for word in POSITIVE_INDICATORS if word in message)
    negative_count = sum(1 for word in NEGATIVE_INDICATORS if word in message)
    
    total = positive_count + negative_count
    if total == 0:
        return 0.0
    
    return (positive_count - negative_count) / max(total, 1)


def detect_category(message: str) -> Tuple[MessageCategory, float]:
    """Detect message category with confidence score"""
    scores = {cat: 0.0 for cat in MessageCategory}
    
    # Rule-based classification
    message_lower = message.lower()
    
    # Inquiry detection
    inquiry_patterns = ["هل", "كيف", "متى", "أين", "ما هو", "ما هي", "كم", "استفسار"]
    for pattern in inquiry_patterns:
        if pattern in message_lower or pattern in message:
            scores[MessageCategory.INQUIRY] += 0.3
    
    # Service request detection
    request_patterns = ["أريد", "أرغب", "أحتاج", "طلب", "نريد", "اطلب"]
    for pattern in request_patterns:
        if pattern in message_lower or pattern in message:
            scores[MessageCategory.SERVICE_REQUEST] += 0.35
    
    # Complaint detection
    complaint_patterns = ["شكوى", "مشكلة", "خلل", "لم يعمل", "تأخر", "لم يصل", "سيء"]
    for pattern in complaint_patterns:
        if pattern in message_lower or pattern in message:
            scores[MessageCategory.COMPLAINT] += 0.4
    
    # Follow-up detection
    followup_patterns = ["متابعة", "بخصوص", "استكمال", "تذكير", "ما الجديد", "تحديث"]
    for pattern in followup_patterns:
        if pattern in message_lower or pattern in message:
            scores[MessageCategory.FOLLOWUP] += 0.3
    
    # Offer detection
    offer_patterns = ["عرض", "خصم", "تخفيض", "فرصة", "عرض خاص"]
    for pattern in offer_patterns:
        if pattern in message_lower or pattern in message:
            scores[MessageCategory.OFFER] += 0.3
    
    # Feedback detection
    feedback_patterns = ["تقييم", "رأي", "ملاحظة", "اقتراح", "تعليق"]
    for pattern in feedback_patterns:
        if pattern in message_lower or pattern in message:
            scores[MessageCategory.FEEDBACK] += 0.3
    
    # Technical support detection
    support_patterns = ["دعم", "مساعدة", "تقني", "فني", "كيفية", "شرح"]
    for pattern in support_patterns:
        if pattern in message_lower or pattern in message:
            scores[MessageCategory.SUPPORT] += 0.3
    
    # Billing detection
    billing_patterns = ["فاتورة", "دفع", "مالي", "حساب", "رصيد", "قسط"]
    for pattern in billing_patterns:
        if pattern in message_lower or pattern in message:
            scores[MessageCategory.BILLING] += 0.35
    
    # Get highest scoring category
    best_category = max(scores, key=scores.get)
    confidence = scores[best_category]
    
    # Default to OTHER if confidence is too low
    if confidence < 0.2:
        return MessageCategory.OTHER, 0.1
    
    return best_category, min(confidence, 1.0)


def suggest_folder(category: MessageCategory, priority: Priority) -> str:
    """Suggest folder based on category and priority"""
    folder_map = {
        MessageCategory.INQUIRY: "استفسارات",
        MessageCategory.SERVICE_REQUEST: "طلبات",
        MessageCategory.COMPLAINT: "شكاوى",
        MessageCategory.FOLLOWUP: "متابعات",
        MessageCategory.OFFER: "عروض",
        MessageCategory.FEEDBACK: "تقييمات",
        MessageCategory.SUPPORT: "دعم فني",
        MessageCategory.BILLING: "مالية",
        MessageCategory.OTHER: "أخرى"
    }
    
    folder = folder_map.get(category, "أخرى")
    
    # Add priority prefix for urgent items
    if priority == Priority.URGENT:
        folder = f"⚠️ عاجل - {folder}"
    
    return folder


def suggest_auto_actions(
    category: MessageCategory,
    priority: Priority,
    sentiment_score: float
) -> List[str]:
    """Suggest automatic actions based on analysis"""
    actions = []
    
    # Priority-based actions
    if priority == Priority.URGENT:
        actions.append("إرسال إشعار للمدير")
        actions.append("إضافة للقائمة العاجلة")
    
    # Category-based actions
    if category == MessageCategory.COMPLAINT:
        actions.append("فتح تذكرة دعم")
        if sentiment_score < -0.3:
            actions.append("تصعيد للإدارة")
    
    if category == MessageCategory.SERVICE_REQUEST:
        actions.append("إنشاء طلب جديد")
        actions.append("إرسال تأكيد استلام")
    
    if category == MessageCategory.BILLING:
        actions.append("تحويل للقسم المالي")
    
    if category == MessageCategory.SUPPORT:
        actions.append("البحث في قاعدة المعرفة")
        actions.append("إنشاء تذكرة دعم فني")
    
    # Sentiment-based actions
    if sentiment_score > 0.5:
        actions.append("إضافة للعملاء المميزين")
    elif sentiment_score < -0.5:
        actions.append("مراجعة يدوية مطلوبة")
    
    return actions


def categorize_message(message: str) -> CategoryResult:
    """
    Main function to categorize a message
    Returns comprehensive categorization result
    """
    # Extract tags
    tags = extract_tags(message)
    
    # Calculate priority
    priority, priority_score = calculate_priority_score(message)
    
    # Calculate sentiment
    sentiment_score = calculate_sentiment(message)
    
    # Detect category
    category, confidence = detect_category(message)
    
    # Suggest folder
    folder = suggest_folder(category, priority)
    
    # Suggest actions
    actions = suggest_auto_actions(category, priority, sentiment_score)
    
    # Detect products (placeholder - would need product catalog)
    detected_products = []
    
    # Detected topics from tags
    detected_topics = tags
    
    return CategoryResult(
        category=category,
        confidence=confidence,
        tags=tags,
        priority=priority,
        priority_score=priority_score,
        sentiment_score=sentiment_score,
        detected_products=detected_products,
        detected_topics=detected_topics,
        suggested_folder=folder,
        auto_actions=actions
    )


def categorize_message_dict(message: str) -> dict:
    """Return categorization as dictionary for API response"""
    result = categorize_message(message)
    return {
        "category": result.category.value,
        "confidence": round(result.confidence, 2),
        "tags": result.tags,
        "priority": result.priority.value,
        "priority_score": result.priority_score,
        "sentiment_score": round(result.sentiment_score, 2),
        "detected_products": result.detected_products,
        "detected_topics": result.detected_topics,
        "suggested_folder": result.suggested_folder,
        "auto_actions": result.auto_actions
    }


# Batch processing
def categorize_messages_batch(messages: List[str]) -> List[dict]:
    """Categorize multiple messages at once"""
    return [categorize_message_dict(msg) for msg in messages]


# Test function
if __name__ == "__main__":
    test_messages = [
        "السلام عليكم، أريد الاستفسار عن أسعار خدماتكم",
        "مشكلة عاجلة! الطلب لم يصل رغم مرور أسبوع وأنا غاضب جداً",
        "شكراً جزيلاً على الخدمة الممتازة، أنتم رائعون!",
        "متابعة بخصوص طلب رقم 12345، ما الجديد؟",
        "أحتاج دعم فني لحل مشكلة في التطبيق",
    ]
    
    for msg in test_messages:
        print(f"\nMessage: {msg[:50]}...")
        result = categorize_message_dict(msg)
        print(f"Category: {result['category']} (confidence: {result['confidence']})")
        print(f"Priority: {result['priority']} (score: {result['priority_score']})")
        print(f"Sentiment: {result['sentiment_score']}")
        print(f"Tags: {result['tags']}")
        print(f"Folder: {result['suggested_folder']}")
        print(f"Actions: {result['auto_actions']}")


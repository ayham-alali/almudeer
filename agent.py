"""
Al-Mudeer - LangGraph InboxCRM Agent
Implements: Ingest -> Classify -> Extract -> Draft pipeline
Optimized for low bandwidth with text-only responses
"""

import json
import re
from typing import TypedDict, Literal, Optional
from dataclasses import dataclass
import httpx
import os

# LangGraph imports
from langgraph.graph import StateGraph, END

# Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")  # or any Arabic-capable model

# System prompt for Arabic business context
SYSTEM_PROMPT = """أنت مساعد مكتبي ذكي لشركة سورية. تتحدث العربية الفصحى بأسلوب مهني ومهذب.
تفهم السياق المحلي السوري والعربي جيداً.
مهمتك هي تحليل الرسائل الواردة واستخراج المعلومات المهمة وصياغة ردود مناسبة.
كن موجزاً ومباشراً في ردودك لتوفير استهلاك البيانات."""


class AgentState(TypedDict):
    """State for the InboxCRM agent"""
    # Input
    raw_message: str
    message_type: str  # email, whatsapp, general
    
    # Classification
    intent: str  # استفسار, طلب خدمة, شكوى, متابعة, عرض, أخرى
    urgency: str  # عاجل, عادي, منخفض
    sentiment: str  # إيجابي, محايد, سلبي
    
    # Extraction
    sender_name: Optional[str]
    sender_contact: Optional[str]
    key_points: list[str]
    action_items: list[str]
    extracted_entities: dict  # dates, amounts, product names, etc.
    
    # Output
    summary: str
    draft_response: str
    suggested_actions: list[str]
    
    # Metadata
    error: Optional[str]
    processing_step: str


async def call_llm(prompt: str, system: str = SYSTEM_PROMPT) -> str:
    """Call Ollama or fallback to rule-based processing"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "system": system,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 500  # Limit response length for bandwidth
                    }
                }
            )
            if response.status_code == 200:
                return response.json().get("response", "")
    except Exception as e:
        print(f"LLM call failed: {e}")
    
    # Fallback to rule-based if Ollama is not available
    return None


def rule_based_classify(message: str) -> dict:
    """Rule-based classification fallback (works offline)"""
    message_lower = message.lower()
    
    # Intent detection
    intent = "أخرى"
    if any(word in message for word in ["سعر", "كم", "تكلفة", "أسعار"]):
        intent = "استفسار"
    elif any(word in message for word in ["أريد", "أرغب", "طلب", "احتاج", "نريد"]):
        intent = "طلب خدمة"
    elif any(word in message for word in ["شكوى", "مشكلة", "لم يعمل", "تأخر", "سيء"]):
        intent = "شكوى"
    elif any(word in message for word in ["متابعة", "بخصوص", "استكمال", "تذكير"]):
        intent = "متابعة"
    elif any(word in message for word in ["عرض", "خصم", "تخفيض", "فرصة"]):
        intent = "عرض"
    
    # Urgency detection
    urgency = "عادي"
    if any(word in message for word in ["عاجل", "فوري", "اليوم", "الآن", "ضروري"]):
        urgency = "عاجل"
    elif any(word in message for word in ["لاحقاً", "عندما", "متى ما"]):
        urgency = "منخفض"
    
    # Sentiment detection
    sentiment = "محايد"
    if any(word in message for word in ["شكراً", "ممتاز", "رائع", "سعيد", "مسرور"]):
        sentiment = "إيجابي"
    elif any(word in message for word in ["غاضب", "محبط", "سيء", "مستاء", "للأسف"]):
        sentiment = "سلبي"
    
    return {"intent": intent, "urgency": urgency, "sentiment": sentiment}


def extract_entities(message: str) -> dict:
    """Extract entities using regex patterns"""
    entities = {}
    
    # Phone numbers (Syrian/Arabic format)
    phone_patterns = [
        r'(?:00963|\+963|0)?9\d{8}',  # Syrian mobile
        r'(?:00963|\+963|0)?11\d{7}',  # Damascus landline
        r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # General format
    ]
    phones = []
    for pattern in phone_patterns:
        phones.extend(re.findall(pattern, message))
    if phones:
        entities["phones"] = list(set(phones))
    
    # Email
    emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', message)
    if emails:
        entities["emails"] = emails
    
    # Dates (Arabic format)
    dates = re.findall(r'\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}', message)
    if dates:
        entities["dates"] = dates
    
    # Money amounts
    amounts = re.findall(r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:ل\.س|ليرة|دولار|\$|USD)', message)
    if amounts:
        entities["amounts"] = amounts
    
    # Extract possible name (after السيد/السيدة/الأستاذ)
    name_match = re.search(r'(?:السيد|السيدة|الأستاذ|الأستاذة|أخي|أختي)\s+([\u0600-\u06FF\s]+)', message)
    if name_match:
        entities["mentioned_name"] = name_match.group(1).strip()
    
    return entities


def generate_rule_based_response(state: dict) -> str:
    """Generate a draft response based on intent"""
    intent = state.get("intent", "أخرى")
    sender = state.get("sender_name", "العميل الكريم")
    
    templates = {
        "استفسار": f"""السيد/السيدة {sender} المحترم/ة،

شكراً لتواصلكم معنا.

بخصوص استفساركم، نود إفادتكم بأن [أضف التفاصيل هنا].

نرحب بأي استفسارات إضافية.

مع أطيب التحيات،
فريق خدمة العملاء""",
        
        "طلب خدمة": f"""السيد/السيدة {sender} المحترم/ة،

شكراً لثقتكم بخدماتنا.

تم استلام طلبكم بنجاح وسيتم التواصل معكم قريباً لاستكمال الإجراءات.

للمتابعة أو الاستفسار، نحن بخدمتكم.

مع أطيب التحيات،
فريق المبيعات""",
        
        "شكوى": f"""السيد/السيدة {sender} المحترم/ة،

نعتذر عن أي إزعاج سببناه لكم.

تم تسجيل ملاحظاتكم وسيتم معالجة الموضوع بأقصى سرعة.
سنتواصل معكم خلال [حدد المدة] لإطلاعكم على المستجدات.

نقدر صبركم وتفهمكم.

مع أطيب التحيات،
فريق خدمة العملاء""",
        
        "متابعة": f"""السيد/السيدة {sender} المحترم/ة،

شكراً لمتابعتكم.

بخصوص موضوعكم، نود إفادتكم بأن [أضف الحالة الحالية].

سنبقيكم على اطلاع بأي تحديثات.

مع أطيب التحيات،
فريق المتابعة""",
        
        "عرض": f"""السيد/السيدة {sender} المحترم/ة،

شكراً لتواصلكم وعرضكم الكريم.

سنقوم بدراسة العرض المقدم والرد عليكم في أقرب وقت.

مع أطيب التحيات،
فريق المشتريات""",
        
        "أخرى": f"""السيد/السيدة {sender} المحترم/ة،

شكراً لتواصلكم معنا.

تم استلام رسالتكم وسنقوم بالرد عليكم قريباً.

مع أطيب التحيات،
فريق خدمة العملاء"""
    }
    
    return templates.get(intent, templates["أخرى"])


# ============ LangGraph Nodes ============

async def ingest_node(state: AgentState) -> AgentState:
    """Step 1: Ingest and clean the message"""
    state["processing_step"] = "استلام"
    
    # Clean the message
    raw = state["raw_message"].strip()
    
    # Detect message type if not specified
    if not state.get("message_type"):
        if "@" in raw and "subject" in raw.lower():
            state["message_type"] = "email"
        elif any(x in raw for x in ["واتساب", "whatsapp", "📱"]):
            state["message_type"] = "whatsapp"
        else:
            state["message_type"] = "general"
    
    return state


async def classify_node(state: AgentState) -> AgentState:
    """Step 2: Classify intent, urgency, and sentiment"""
    state["processing_step"] = "تصنيف"
    
    # Try LLM first
    prompt = f"""حلل الرسالة التالية وأعطني:
1. النية (intent): استفسار، طلب خدمة، شكوى، متابعة، عرض، أخرى
2. الأهمية (urgency): عاجل، عادي، منخفض
3. المشاعر (sentiment): إيجابي، محايد، سلبي

الرسالة:
{state['raw_message']}

الرد بصيغة JSON فقط:
{{"intent": "", "urgency": "", "sentiment": ""}}"""

    llm_response = await call_llm(prompt)
    
    if llm_response:
        try:
            # Extract JSON from response
            json_match = re.search(r'\{[^}]+\}', llm_response)
            if json_match:
                classification = json.loads(json_match.group())
                state["intent"] = classification.get("intent", "أخرى")
                state["urgency"] = classification.get("urgency", "عادي")
                state["sentiment"] = classification.get("sentiment", "محايد")
                return state
        except json.JSONDecodeError:
            pass
    
    # Fallback to rule-based
    classification = rule_based_classify(state["raw_message"])
    state["intent"] = classification["intent"]
    state["urgency"] = classification["urgency"]
    state["sentiment"] = classification["sentiment"]
    
    return state


async def extract_node(state: AgentState) -> AgentState:
    """Step 3: Extract key information"""
    state["processing_step"] = "استخراج"
    
    # Extract entities using regex (reliable, no LLM needed)
    entities = extract_entities(state["raw_message"])
    state["extracted_entities"] = entities
    
    # Set sender info from entities if found
    if entities.get("mentioned_name"):
        state["sender_name"] = entities["mentioned_name"]
    if entities.get("emails"):
        state["sender_contact"] = entities["emails"][0]
    elif entities.get("phones"):
        state["sender_contact"] = entities["phones"][0]
    
    # Try LLM for key points extraction
    prompt = f"""من الرسالة التالية، استخرج:
1. النقاط الرئيسية (3 نقاط كحد أقصى)
2. الإجراءات المطلوبة

الرسالة:
{state['raw_message']}

الرد بصيغة JSON:
{{"key_points": ["نقطة 1", "نقطة 2"], "action_items": ["إجراء 1"]}}"""

    llm_response = await call_llm(prompt)
    
    if llm_response:
        try:
            json_match = re.search(r'\{[^}]+\}', llm_response, re.DOTALL)
            if json_match:
                extracted = json.loads(json_match.group())
                state["key_points"] = extracted.get("key_points", [])
                state["action_items"] = extracted.get("action_items", [])
                return state
        except json.JSONDecodeError:
            pass
    
    # Fallback: Basic extraction
    sentences = state["raw_message"].split('.')
    state["key_points"] = [s.strip() for s in sentences[:3] if s.strip()]
    state["action_items"] = ["مراجعة الطلب", "الرد على العميل"]
    
    return state


async def draft_node(state: AgentState) -> AgentState:
    """Step 4: Draft a response"""
    state["processing_step"] = "صياغة"
    
    sender = state.get("sender_name", "العميل الكريم")
    intent = state.get("intent", "أخرى")
    key_points = state.get("key_points", [])
    
    # Try LLM for natural response
    prompt = f"""اكتب رداً مهنياً مختصراً على الرسالة التالية.
المرسل: {sender}
نوع الرسالة: {intent}
النقاط الرئيسية: {', '.join(key_points)}

الرسالة الأصلية:
{state['raw_message']}

اكتب رداً مهذباً ومختصراً (لا يتجاوز 100 كلمة):"""

    llm_response = await call_llm(prompt)
    
    if llm_response and len(llm_response) > 50:
        state["draft_response"] = llm_response.strip()
    else:
        # Use template-based response
        state["draft_response"] = generate_rule_based_response(state)
    
    # Generate summary
    state["summary"] = f"رسالة {intent} من {sender}. المشاعر: {state.get('sentiment', 'محايد')}. الأهمية: {state.get('urgency', 'عادي')}."
    
    # Suggested actions based on intent
    actions_map = {
        "استفسار": ["الرد على الاستفسار", "إضافة للأسئلة الشائعة"],
        "طلب خدمة": ["إنشاء طلب جديد", "تحديد موعد", "إرسال عرض سعر"],
        "شكوى": ["تصعيد للمدير", "فتح تذكرة دعم", "الاتصال بالعميل"],
        "متابعة": ["تحديث حالة الطلب", "إرسال تقرير"],
        "عرض": ["دراسة العرض", "تحويل للمشتريات"],
        "أخرى": ["مراجعة يدوية", "تصنيف الرسالة"]
    }
    state["suggested_actions"] = actions_map.get(intent, actions_map["أخرى"])
    
    return state


# ============ Build the Graph ============

def create_inbox_agent():
    """Create the InboxCRM LangGraph agent"""
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("ingest", ingest_node)
    workflow.add_node("classify", classify_node)
    workflow.add_node("extract", extract_node)
    workflow.add_node("draft", draft_node)
    
    # Define edges (linear pipeline)
    workflow.set_entry_point("ingest")
    workflow.add_edge("ingest", "classify")
    workflow.add_edge("classify", "extract")
    workflow.add_edge("extract", "draft")
    workflow.add_edge("draft", END)
    
    # Compile
    return workflow.compile()


# Singleton agent instance
_agent = None

def get_agent():
    """Get or create the agent instance"""
    global _agent
    if _agent is None:
        _agent = create_inbox_agent()
    return _agent


async def process_message(
    message: str,
    message_type: str = None,
    sender_name: str = None,
    sender_contact: str = None
) -> dict:
    """Process a message through the InboxCRM pipeline"""
    
    agent = get_agent()
    
    # Initial state
    initial_state: AgentState = {
        "raw_message": message,
        "message_type": message_type or "general",
        "intent": "",
        "urgency": "",
        "sentiment": "",
        "sender_name": sender_name,
        "sender_contact": sender_contact,
        "key_points": [],
        "action_items": [],
        "extracted_entities": {},
        "summary": "",
        "draft_response": "",
        "suggested_actions": [],
        "error": None,
        "processing_step": ""
    }
    
    try:
        # Run the agent
        final_state = await agent.ainvoke(initial_state)
        return {
            "success": True,
            "data": {
                "intent": final_state["intent"],
                "urgency": final_state["urgency"],
                "sentiment": final_state["sentiment"],
                "sender_name": final_state["sender_name"],
                "sender_contact": final_state["sender_contact"],
                "key_points": final_state["key_points"],
                "action_items": final_state["action_items"],
                "extracted_entities": final_state["extracted_entities"],
                "summary": final_state["summary"],
                "draft_response": final_state["draft_response"],
                "suggested_actions": final_state["suggested_actions"],
                "message_type": final_state["message_type"]
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"حدث خطأ في المعالجة: {str(e)}"
        }


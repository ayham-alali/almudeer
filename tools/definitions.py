"""
Al-Mudeer - Agent Tools
Defines the executable tools and their schemas for the LLM.
"""

from typing import Dict, Any, List
import json
import logging

logger = logging.getLogger(__name__)

# ============ Tool Implementations ============

from database import get_customer, get_order_by_ref, upsert_customer_lead

async def lookup_customer(contact: str) -> Dict[str, Any]:
    """
    Look up a customer by phone number or email from the Real DB.
    """
    print(f"[Tool] Looking up customer in DB: {contact}")
    
    customer = await get_customer(contact)
    if not customer:
        return {"status": "not_found", "message": "No customer found with this contact in our records."}
        
    return {
        "status": "found",
        "name": customer["name"],
        "type": customer["type"],
        "total_spend": customer["total_spend"],
        "notes": customer["notes"]
    }

async def check_order_status(order_id: str) -> Dict[str, Any]:
    """
    Check the status of a specific order from the Real DB.
    """
    print(f"[Tool] Checking order status in DB: {order_id}")
    
    order = await get_order_by_ref(order_id)
    if not order:
        return {"status": "not_found", "message": f"Order {order_id} does not exist."}
    
    return {
        "order_id": order["order_ref"],
        "status": order["status"],
        "total_amount": order["total_amount"],
        "items": order["items"], # Stored as text/JSON
        "created_at": order["created_at"]
    }

async def create_lead(name: str, contact: str, interest: str, license_key_id: int = 0) -> Dict[str, Any]:
    """
    Create a new sales lead in the Real DB.
    """
    print(f"[Tool] Creating lead in DB: {name}, {contact}")
    
    lead_id = await upsert_customer_lead(name, contact, f"Interested in: {interest}")
    
    # Trigger Safety Notification
    if license_key_id > 0:
        try:
            from services.notification_service import send_tool_action_alert
            import asyncio
            # Fire and forget
            asyncio.create_task(send_tool_action_alert(
                license_id=license_key_id,
                action_name="Create Lead",
                details=f"Name: {name}, Contact: {contact}, Interest: {interest}"
            ))
        except Exception as e:
            print(f"Failed to send alert: {e}")

    return {
        "status": "success",
        "lead_id": lead_id,
        "message": f"Lead {name} saved successfully."
    }

async def search_web(query: str) -> Dict[str, Any]:
    """
    Search the web for information using DuckDuckGo.
    """
    print(f"[Tool] Searching web for: {query}")
    try:
        from duckduckgo_search import DDGS
        
        # Use sync wrapper in executor or use async directly if available?
        # DDGS has no async support in standard 4.x, need to check version.
        # It's safer to run in executor to avoid blocking loop.
        import asyncio
        
        loop = asyncio.get_event_loop()
        
        def run_search():
            with DDGS() as ddgs:
                # Get top 3 results
                results = list(ddgs.text(query, max_results=3))
            return results

        results = await loop.run_in_executor(None, run_search)
        
        if not results:
            return {"status": "no_results", "message": "No information found."}
            
        # Format results
        formatted = []
        for r in results:
            formatted.append(f"Title: {r.get('title')}\nLink: {r.get('href')}\nSnippet: {r.get('body')}")
            
        return {
            "status": "success",
            "results": "\n---\n".join(formatted)
        }
    except ImportError:
        return {"status": "error", "message": "Search module not installed (duckduckgo-search)."}
    except Exception as e:
        return {"status": "error", "message": f"Search failed: {str(e)}"}

# ============ Tool Definitions (Schema) ============

TOOLS_SCHEMA = [
    {
        "function_declarations": [
            {
                "name": "lookup_customer",
                "description": "Get customer details (name, past orders, type) by their contact info (phone/email). Use this when you need ID or history.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "contact": {
                            "type": "STRING",
                            "description": "Customer phone number or email address"
                        }
                    },
                    "required": ["contact"]
                }
            },
            {
                "name": "check_order_status",
                "description": "Get the current status and location of a specific order ID.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "order_id": {
                            "type": "STRING",
                            "description": "The unique order reference number (e.g. 123)"
                        }
                    },
                    "required": ["order_id"]
                }
            },
            {
                "name": "create_lead",
                "description": "Register a new potential customer (lead) in the system who is interested in a product/service.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "name": {
                            "type": "STRING",
                            "description": "Name of the customer"
                        },
                        "contact": {
                            "type": "STRING",
                            "description": "Phone number or email"
                        },
                        "interest": {
                            "type": "STRING",
                            "description": "What product/service they are interested in"
                        }
                    },
                    "required": ["name", "contact", "interest"]
                }
            },
            {
                "name": "search_web",
                "description": "Search the internet for real-time information, news, or facts not in the database.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "query": {
                            "type": "STRING",
                            "description": "The search query (e.g. 'latest release date of iPhone 16')"
                        }
                    },
                    "required": ["query"]
                }
            }
        ]
    }
]

# Map names to functions for execution
TOOL_FUNCTIONS = {
    "lookup_customer": lookup_customer,
    "check_order_status": check_order_status,
    "create_lead": create_lead,
    "search_web": search_web
}

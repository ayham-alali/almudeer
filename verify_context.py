
import asyncio
import sys
import os
from unittest.mock import patch, MagicMock

# Add the backend to path
sys.path.append(r"c:\roya\products\almudeer\backend")

# Mock modules before importing them if necessary, but here we can patch after import
import agent
import agent_enhanced

async def test_context_prompt_injection():
    history = """
User: كم سعر iPhone 15 Pro؟
Agent: سعر iPhone 15 Pro هو 4500 ريال سعودي.
User: هل يتوفر باللون الأزرق؟
Agent: نعم، اللون الأزرق متوفر حالياً.
"""
    current_message = "طيب وكيف أقدر أطلبه؟"
    
    print("Testing Standard Agent Context Injection...")
    print("-" * 50)
    
    # Patch call_llm in agent.py
    with patch('agent.call_llm') as mock_llm:
        # Mock return value to be valid JSON so process_message completes
        mock_llm.return_value = '{"draft_response": "Mock Response", "intent": "inquiry"}'
        
        await agent.process_message(
            message=current_message,
            history=history
        )
        
        # Verify the call arguments
        args, kwargs = mock_llm.call_args
        prompt_sent = args[0]
        
        if history in prompt_sent:
            print("✅ SUCCESS: History found in Standard Agent prompt!")
            # print(f"Snippet of prompt:\n{prompt_sent[:500]}...")
        else:
            print("❌ FAILURE: History NOT found in Standard Agent prompt!")
            print(f"Prompt content:\n{prompt_sent}")

    print("\n" + "=" * 50 + "\n")
    
    print("Testing Enhanced Agent Context Injection...")
    
    # Patch call_llm_enhanced in agent_enhanced.py
    with patch('agent_enhanced.call_llm_enhanced') as mock_llm_enhanced:
        mock_llm_enhanced.return_value = '{"draft_response": "Mock Response Enhanced"}'
        
        await agent_enhanced.process_message_enhanced(
            message=current_message,
            conversation_history=history,
            sender_name="Test User"
        )
        
        # Verify call arguments
        # agent_enhanced might make multiple calls (classify, extract, draft).
        # We want to check the 'draft_node' call mostly, or any call.
        # Let's inspect all calls
        found = False
        for call in mock_llm_enhanced.call_args_list:
            args, kwargs = call
            prompt_sent = args[0]
            if history in prompt_sent:
                found = True
                print("✅ SUCCESS: History found in Enhanced Agent prompt!")
                break
        
        if not found:
            print("❌ FAILURE: History NOT found in Enhanced Agent prompt!")
            # Print the calls to help debug
            print(f"Total calls: {len(mock_llm_enhanced.call_args_list)}")
            for i, call in enumerate(mock_llm_enhanced.call_args_list):
                 print(f"Call {i} prompt snippet: {call[0][0][:100]}...")

if __name__ == "__main__":
    asyncio.run(test_context_prompt_injection())

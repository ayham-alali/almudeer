
import asyncio
import sys
import os
import shutil
from unittest.mock import patch, MagicMock

# Add the backend to path
sys.path.append(r"c:\roya\products\almudeer\backend")

# Ensure clean state for test
if os.path.exists("./data/test_chroma_db"):
    shutil.rmtree("./data/test_chroma_db")

# Mock valid LLMProvider for embedding
async def mock_embed_text(text):
    # Determine deterministically based on text
    if "2.0" in text:
        val = 0.9
    elif "release" in text:
        val = 0.8
    else:
        val = 0.1
    # Return fake 768-dim vector (shortened for test)
    return [val] * 768

class MockLLMProvider:
    async def embed_text(self, text):
        return await mock_embed_text(text)

class MockInstance:
    def __init__(self):
        self.llm_provider = MockLLMProvider()

async def test_rag_flow():
    print("\n--- Testing RAG Flow ---")
    
    # Patch GeminiProvider to avoid real API calls
    with patch("services.knowledge_base.GeminiProvider", return_value=MockLLMProvider()):
        from services.knowledge_base import KnowledgeBase
        
        # Initialize KB with test path
        kb = KnowledgeBase(persist_path="./data/test_chroma_db")
        
        # 1. Add Document
        fact = "Al-Mudeer 2.0 will be released on January 1st, 2026."
        print(f"Adding fact: {fact}")
        success = await kb.add_document(fact, metadata={"source": "roadmap"})
        
        if success:
            print("✅ Document added successfully.")
        else:
            print("❌ Failed to add document.")
            return

        # 2. Search
        query = "When is version 2.0 coming?"
        print(f"Searching for: {query}")
        results = await kb.search(query, k=1)
        
        if results and "January 1st" in results[0]['text']:
            print(f"✅ Search successful! Found: {results[0]['text']}")
            print(f"   Score: {results[0]['score']}")
        else:
            print("❌ Search failed or returned irrelevant results.")
            if results:
                print(f"   Got: {results[0]['text']}")

    # 3. Agent Integration Test
    print("\n--- Testing RAG Agent Integration ---")
    with patch("services.knowledge_base.get_knowledge_base") as mock_get_kb:
        mock_kb = MagicMock()
        mock_kb.search = MagicMock(return_value=asyncio.Future())
        mock_kb.search.return_value.set_result([
            {"text": "Simulated KB Fact: Product X costs $50.", "score": 0.1}
        ])
        mock_get_kb.return_value = mock_kb
        
        # Mock other dependencies
        with patch("agent.call_llm", return_value='{"intent": "info"}'):
            import agent
            
            # Process message
            msg = "How much is Product X?"
            await agent.process_message(msg)
            
            # Verify search was called
            mock_kb.search.assert_called_with(msg.strip(), k=2)
            print("✅ Agent called KB search.")
            
            # We can't easily check the prompt passed to call_llm without mocking it deeper,
            # but we verified the logic injection in previous steps.

if __name__ == "__main__":
    try:
        asyncio.run(test_rag_flow())
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

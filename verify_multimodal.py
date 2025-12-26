
import asyncio
import sys
import unittest
from unittest.mock import patch, MagicMock
import base64

# Add the backend to path
sys.path.append(r"c:\roya\products\almudeer\backend")

# Import services
from services.link_reader import extract_and_scrape_links
from services.llm_provider import GeminiProvider, LLMConfig
import agent

class TestMultimodal(unittest.IsolatedAsyncioTestCase):
    
    async def test_link_reader(self):
        print("\n--- Testing Link Reader ---")
        text_with_link = "Check this out: https://example.com"
        
        # Mock httpx.AsyncClient to avoid real network calls during test (optional, but good for speed)
        # However, for verification we might want a real call to a safe URL
        # Let's try a real call to a stable URL
        
        print(f"Scraping: {text_with_link}")
        result = await extract_and_scrape_links(text_with_link)
        
        if "Example Domain" in result:
            print("✅ Link Scraping Success: Found 'Example Domain' in content.")
        else:
            print(f"❌ Link Scraping Error/Empty: {result[:100]}...")

    async def test_pdf_mime_passing(self):
        print("\n--- Testing PDF Hand-off to Gemini ---")
        
        provider = GeminiProvider(LLMConfig())
        
        # Mock the underlying google.genai.types.Part
        with patch("google.genai.types.Part") as mock_part:
            mock_part.from_bytes.return_value = "MockPart"
            
            # Mock client to prevent actual API call
            with patch.object(GeminiProvider, "_client"):
                # But we need to bypass _client check or mock it properly
                # Actually, simpler is to check if 'application/pdf' triggers from_bytes
                
                attachments = [{
                    "type": "application/pdf",
                    "base64": "JVBERi0xLjQKJcOkw7zDtsOfCjIgMCBvYmoKPDwvTGVuZ3RoIDMgMCBSL0ZpbHRlci9GbGF0ZURlY29kZT4+CnN0cmVhbQpHbobbCmVuZHN0cmVhbQplbmRvYmoKCg=="
                }]
                
                # We can't easily run generate without a client, so let's inspect the code logic
                # via a small unit test of internal logic if possible, OR
                # Check LLMProvider code directly by invoking generate and mocking the client call
                
                # Let's mock the entire client logic and just see if it processes the attachment
                provider._client = MagicMock()
                
                # Mock get_rate_limiter
                with patch("services.llm_provider.get_rate_limiter") as mock_limiter:
                    mock_limiter.return_value.wait_for_capacity = MagicMock()
                    mock_limiter.return_value.wait_for_capacity.return_value = asyncio.Future()
                    mock_limiter.return_value.wait_for_capacity.return_value.set_result(None)

                    # Mock run_in_executor
                    with patch("asyncio.get_event_loop") as mock_loop:
                        mock_loop.return_value.run_in_executor.return_value = asyncio.Future()
                        mock_loop.return_value.run_in_executor.return_value.set_result(MagicMock(text="Response"))

                        # Run generate
                        await provider.generate("test", attachments=attachments)
                        
                        # Verify from_bytes called with pdf mime type
                        mock_part.from_bytes.assert_called()
                        call_args = mock_part.from_bytes.call_args
                        print(f"Called with mime_type: {call_args.kwargs.get('mime_type')}")
                        
                        if call_args.kwargs.get('mime_type') == "application/pdf":
                             print("✅ PDF Mime Type passed correctly!")
                        else:
                             print("❌ PDF Mime Type NOT passed!")

    async def test_agent_integration(self):
        print("\n--- Testing Agent Integration (Mocked) ---")
        message = "Analyze this PDF and this link https://example.com"
        attachments = [{"type": "application/pdf", "base64": "..."}]
        
        # Patch extract_urls to return fake content
        with patch("services.link_reader.extract_and_scrape_links") as mock_scrape:
            mock_scrape.return_value = "--- Scraped Content ---"
            
            # Patch call_llm to check prompt
            with patch("agent.call_llm") as mock_llm:
                mock_llm.return_value = {"success": True, "data": {}}
                
                await agent.process_message(message, attachments=attachments)
                
                # Check prompt for scraped content
                args, kw = mock_llm.call_args
                prompt = args[0]
                
                if "--- Scraped Content ---" in prompt:
                    print("✅ Agent injected scraped content into prompt!")
                else:
                    print("❌ Agent failed to inject scraped content.")
                
                # Check attachments passed
                passed_atts = kw.get('attachments')
                if passed_atts == attachments:
                     print("✅ Agent passed attachments correctly!")

if __name__ == "__main__":
    asyncio.run(TestMultimodal().test_link_reader())
    asyncio.run(TestMultimodal().test_pdf_mime_passing())
    asyncio.run(TestMultimodal().test_agent_integration())

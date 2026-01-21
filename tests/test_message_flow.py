import pytest
import base64
from unittest.mock import AsyncMock, patch, MagicMock
from services.analysis_service import process_inbox_message_logic

@pytest.mark.asyncio
async def test_text_in_text_out():
    """
    Scenario 1: Text In -> Text Out
    """
    # Messaging Data
    inbox_msg = {
        "id": 123,
        "sender_contact": "+123456789", 
        "sender_name": "Test User",
        "sender_id": None,
        "channel": "generic",
        "body": "Hello",
        "subject": None
    }
    
    # DB Mocks
    # db_helper.fetch_one returns inbox message, then customer info
    # We'll use side_effect or just return lenient values
    
    mock_fetch_one = AsyncMock(side_effect=[
        inbox_msg, # get_inbox_message_by_id
        {"bot_token": "abc"}, # if needed by some other check
        {"id": 99}, # get_or_create_customer check (find existing)
        None
    ])
    mock_fetch_all = AsyncMock(return_value=[]) # Chat history empty
    
    mock_db = MagicMock()
    mock_db.__aenter__ = AsyncMock(return_value=mock_db)
    mock_db.__aexit__ = AsyncMock(return_value=None)
    
    mock_update_inbox = AsyncMock()
    
    mock_update_inbox = AsyncMock()
    
    with patch("models.inbox.get_db", return_value=mock_db), \
         patch("models.inbox.fetch_one", mock_fetch_one), \
         patch("models.inbox.fetch_all", mock_fetch_all), \
         patch("models.inbox.execute_sql", AsyncMock()), \
         patch("services.analysis_service.update_inbox_analysis", mock_update_inbox), \
         patch("services.analysis_service.create_outbox_message", AsyncMock(return_value=1)), \
         patch("services.analysis_service.approve_outbox_message", AsyncMock()), \
         patch("services.analysis_service.update_inbox_status", AsyncMock()), \
         patch("services.notification_service.process_message_notifications", AsyncMock()), \
         patch("models.customers.get_or_create_customer", AsyncMock(return_value={"id": 99})), \
         patch("models.customers.increment_customer_messages", AsyncMock()), \
         patch("models.customers.update_customer_lead_score", AsyncMock()), \
         patch("models.purchases.create_purchase", AsyncMock()), \
         patch("services.analysis_service.process_message", new_callable=AsyncMock) as mock_agent:

        # Agent returns a text response
        mock_agent.return_value = {
            "success": True,
            "data": {
                "intent": "inquiry",
                "urgency": "low",
                "sentiment": "neutral",
                "summary": "User hello",
                "draft_response": "Hello, how can I help you?",
                "language": "en"
            }
        }

        await process_inbox_message_logic(
            message_id=123,
            body="Hello",
            license_id=1,
            auto_reply=True
        )

        # Verification
        mock_agent.assert_called_once()
        assert "Hello" in mock_agent.call_args.kwargs["message"]
        
        mock_update_inbox.assert_called_once()
        args = mock_update_inbox.call_args.kwargs
        assert args["draft_response"] == "Hello, how can I help you?"
        assert "[AUDIO:" not in args["draft_response"]


@pytest.mark.asyncio
async def test_voice_in_voice_out():
    """
    Scenario 2: Voice In -> Voice Out
    """
    inbox_msg = {
        "id": 456,
        "sender_contact": "+123456789", 
        "sender_name": "Test User",
        "sender_id": None,
        "channel": "generic",
        "body": "", # Empty initially
        "subject": None
    }
    
    mock_fetch_one = AsyncMock(side_effect=[
        inbox_msg, 
        {"id": 99}, # customer
        None
    ])
    
    mock_update_inbox = AsyncMock()
    
    # Mock STT/TTS
    mock_transcribe = AsyncMock(return_value={
        "success": True, 
        "text": "I need help with my order."
    })
    mock_tts = AsyncMock(return_value="/static/audio/reply_123.mp3")

    # Audio data
    dummy_audio_b64 = base64.b64encode(b"fake_audio_content").decode("utf-8")
    attachments = [{
        "type": "audio/ogg",
        "base64": dummy_audio_b64,
        "filename": "voice.ogg"
    }]
    
    mock_db = MagicMock()
    mock_db.__aenter__ = AsyncMock(return_value=mock_db)
    mock_db.__aexit__ = AsyncMock(return_value=None)

    with patch("models.inbox.get_db", return_value=mock_db), \
         patch("models.inbox.fetch_one", mock_fetch_one), \
         patch("models.inbox.fetch_all", AsyncMock(return_value=[])), \
         patch("models.inbox.execute_sql", AsyncMock()), \
         patch("services.analysis_service.update_inbox_analysis", mock_update_inbox), \
         patch("services.analysis_service.create_outbox_message", AsyncMock(return_value=1)), \
         patch("services.analysis_service.approve_outbox_message", AsyncMock()), \
         patch("services.analysis_service.update_inbox_status", AsyncMock()), \
         patch("services.notification_service.process_message_notifications", AsyncMock()), \
         patch("models.customers.get_or_create_customer", AsyncMock(return_value={"id": 99})), \
         patch("models.customers.increment_customer_messages", AsyncMock()), \
         patch("models.customers.update_customer_lead_score", AsyncMock()), \
         patch("models.purchases.create_purchase", AsyncMock()), \
         patch("services.voice_service.transcribe_voice_message", mock_transcribe), \
         patch("services.tts_service.generate_speech_to_file", mock_tts), \
         patch("services.analysis_service.process_message", new_callable=AsyncMock) as mock_agent:

        mock_agent.return_value = {
            "success": True,
            "data": {
                "intent": "support",
                "urgency": "medium",
                "sentiment": "neutral",
                "summary": "Order help",
                "draft_response": "Sure, I can check your order.",
                "language": "en"
            }
        }

        await process_inbox_message_logic(
            message_id=456,
            body="", 
            license_id=1,
            auto_reply=True,
            attachments=attachments
        )

        mock_transcribe.assert_called_once()
        mock_agent.assert_called_once()
        assert "[Voice Message Transcription]: I need help with my order." in mock_agent.call_args.kwargs["message"]
        
        mock_tts.assert_called_once_with("Sure, I can check your order.")
        
        mock_update_inbox.assert_called_once()
        final_draft = mock_update_inbox.call_args.kwargs["draft_response"]
        assert "[AUDIO: /static/audio/reply_123.mp3]" in final_draft
        assert "Sure, I can check your order." in final_draft

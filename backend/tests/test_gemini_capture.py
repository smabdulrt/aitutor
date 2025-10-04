"""
Test suite for Gemini Stream Capture

CRITICAL: Tests ONLY import from codebase and verify behavior.
NO logic hardcoded - we test the actual implementation.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from backend.stream_capture.gemini_capture import (
    GeminiStreamCapture,
    StreamMessage,
    MessageType
)


class TestGeminiStreamCapture:
    """Test GeminiStreamCapture - imports from backend, no hardcoding"""

    @pytest.fixture
    def capture(self):
        """Create GeminiStreamCapture instance for testing"""
        return GeminiStreamCapture(port=8765)

    @pytest.mark.asyncio
    async def test_initialization(self, capture):
        """Test capture initializes correctly"""
        assert capture.port == 8765
        assert capture.is_running == False
        assert capture.messages == []

    @pytest.mark.asyncio
    async def test_message_capture(self, capture):
        """Test capturing streaming messages"""
        # Import from codebase and test
        test_message = {
            "type": "content",
            "text": "Let's solve this problem step by step",
            "timestamp": 1234567890
        }

        captured = await capture.capture_message(test_message)

        assert captured.message_type == MessageType.CONTENT
        assert captured.text == "Let's solve this problem step by step"
        assert captured.timestamp == 1234567890

    @pytest.mark.asyncio
    async def test_store_message(self, capture):
        """Test message storage"""
        message = StreamMessage(
            message_type=MessageType.CONTENT,
            text="Test message",
            timestamp=1234567890
        )

        capture.store_message(message)

        assert len(capture.messages) == 1
        assert capture.messages[0].text == "Test message"

    @pytest.mark.asyncio
    async def test_get_recent_messages(self, capture):
        """Test retrieving recent messages"""
        # Add multiple messages
        for i in range(5):
            msg = StreamMessage(
                message_type=MessageType.CONTENT,
                text=f"Message {i}",
                timestamp=1234567890 + i
            )
            capture.store_message(msg)

        # Get recent 3
        recent = capture.get_recent_messages(limit=3)

        assert len(recent) == 3
        assert recent[0].text == "Message 4"  # Most recent first

    @pytest.mark.asyncio
    async def test_filter_by_type(self, capture):
        """Test filtering messages by type"""
        capture.store_message(StreamMessage(
            message_type=MessageType.CONTENT,
            text="Content message",
            timestamp=1
        ))
        capture.store_message(StreamMessage(
            message_type=MessageType.AUDIO,
            text="Audio data",
            timestamp=2
        ))
        capture.store_message(StreamMessage(
            message_type=MessageType.TOOL_CALL,
            text="Tool call",
            timestamp=3
        ))

        content_only = capture.filter_by_type(MessageType.CONTENT)

        assert len(content_only) == 1
        assert content_only[0].text == "Content message"

    @pytest.mark.asyncio
    async def test_websocket_handler(self, capture):
        """Test WebSocket message handling"""
        mock_websocket = AsyncMock()

        # Mock async iteration
        async def mock_recv():
            for msg in [
                json.dumps({"type": "content", "text": "Hello", "timestamp": 1}),
                json.dumps({"type": "content", "text": "World", "timestamp": 2})
            ]:
                yield msg

        mock_websocket.__aiter__ = lambda self: mock_recv()

        try:
            task = asyncio.create_task(capture.handle_websocket(mock_websocket, "/"))
            await asyncio.sleep(0.1)  # Let messages process
            task.cancel()
            await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            pass

        assert len(capture.messages) >= 1  # At least one message processed

    @pytest.mark.asyncio
    async def test_start_stop_server(self, capture):
        """Test server start/stop"""
        # Start server in background
        server_task = asyncio.create_task(capture.start())
        await asyncio.sleep(0.2)  # Let server start

        assert capture.is_running == True

        # Stop server
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass
        await capture.stop()

        assert capture.is_running == False

    @pytest.mark.asyncio
    async def test_message_callback(self, capture):
        """Test message callback invocation"""
        callback_received = []

        def on_message(msg):
            callback_received.append(msg)

        capture.on_message_callback = on_message

        message = StreamMessage(
            message_type=MessageType.CONTENT,
            text="Callback test",
            timestamp=1
        )

        capture.store_message(message)

        assert len(callback_received) == 1
        assert callback_received[0].text == "Callback test"


class TestStreamMessage:
    """Test StreamMessage data class"""

    def test_message_creation(self):
        """Test creating StreamMessage"""
        from backend.stream_capture.gemini_capture import StreamMessage, MessageType

        msg = StreamMessage(
            message_type=MessageType.CONTENT,
            text="Test",
            timestamp=12345,
            metadata={"source": "gemini"}
        )

        assert msg.message_type == MessageType.CONTENT
        assert msg.text == "Test"
        assert msg.timestamp == 12345
        assert msg.metadata["source"] == "gemini"

    def test_message_to_dict(self):
        """Test converting message to dict"""
        from backend.stream_capture.gemini_capture import StreamMessage, MessageType

        msg = StreamMessage(
            message_type=MessageType.AUDIO,
            text="Audio data",
            timestamp=99999
        )

        msg_dict = msg.to_dict()

        assert msg_dict["type"] == "audio"
        assert msg_dict["text"] == "Audio data"
        assert msg_dict["timestamp"] == 99999


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.mark.asyncio
    async def test_empty_message(self):
        """Test handling empty messages"""
        from backend.stream_capture.gemini_capture import GeminiStreamCapture

        capture = GeminiStreamCapture()

        result = await capture.capture_message({})

        # Should handle gracefully, not crash
        assert result is not None

    @pytest.mark.asyncio
    async def test_invalid_json(self):
        """Test handling invalid JSON"""
        from backend.stream_capture.gemini_capture import GeminiStreamCapture

        capture = GeminiStreamCapture()
        mock_websocket = AsyncMock()

        # Mock async iteration with invalid JSON
        async def mock_invalid_json():
            yield "invalid json{"

        mock_websocket.__aiter__ = lambda self: mock_invalid_json()

        task = asyncio.create_task(capture.handle_websocket(mock_websocket, "/"))
        await asyncio.sleep(0.1)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        # Should not crash, message count stays 0
        assert len(capture.messages) == 0

    @pytest.mark.asyncio
    async def test_large_message_volume(self):
        """Test handling large volume of messages"""
        from backend.stream_capture.gemini_capture import GeminiStreamCapture, StreamMessage, MessageType

        capture = GeminiStreamCapture()

        # Add 1000 messages
        for i in range(1000):
            msg = StreamMessage(
                message_type=MessageType.CONTENT,
                text=f"Message {i}",
                timestamp=i
            )
            capture.store_message(msg)

        assert len(capture.messages) == 1000
        recent_10 = capture.get_recent_messages(limit=10)
        assert len(recent_10) == 10
        assert recent_10[0].text == "Message 999"

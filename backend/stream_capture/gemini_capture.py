"""
Gemini Stream Capture

Captures streaming text from Gemini's WebSocket responses and bridges to Python backend.
"""

import asyncio
import websockets
import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Optional, Callable
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages from Gemini"""
    CONTENT = "content"
    AUDIO = "audio"
    TOOL_CALL = "tool_call"
    TOOL_CALL_CANCELLATION = "tool_call_cancellation"
    SETUP_COMPLETE = "setup_complete"
    TURN_COMPLETE = "turn_complete"
    INTERRUPTED = "interrupted"


@dataclass
class StreamMessage:
    """Represents a captured message from Gemini stream"""
    message_type: MessageType
    text: str
    timestamp: float
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert message to dictionary"""
        return {
            "type": self.message_type.value,
            "text": self.text,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }


class GeminiStreamCapture:
    """Captures and stores streaming messages from Gemini"""

    def __init__(self, port: int = 8765, host: str = "localhost"):
        self.port = port
        self.host = host
        self.is_running = False
        self.messages: List[StreamMessage] = []
        self.server = None
        self.on_message_callback: Optional[Callable] = None

    async def capture_message(self, message_data: Dict) -> Optional[StreamMessage]:
        """
        Capture a message from Gemini stream

        Args:
            message_data: Raw message dict from Gemini

        Returns:
            StreamMessage object
        """
        try:
            msg_type_str = message_data.get("type", "content")
            msg_type = MessageType(msg_type_str)

            message = StreamMessage(
                message_type=msg_type,
                text=message_data.get("text", ""),
                timestamp=message_data.get("timestamp", datetime.now().timestamp()),
                metadata=message_data.get("metadata", {})
            )

            return message

        except (ValueError, KeyError) as e:
            logger.error(f"Error capturing message: {e}")
            # Return empty message instead of None for graceful handling
            return StreamMessage(
                message_type=MessageType.CONTENT,
                text="",
                timestamp=datetime.now().timestamp()
            )

    def store_message(self, message: StreamMessage) -> None:
        """
        Store captured message

        Args:
            message: StreamMessage to store
        """
        self.messages.append(message)

        # Invoke callback if registered
        if self.on_message_callback:
            self.on_message_callback(message)

        logger.info(f"Stored message: {message.message_type.value} - {message.text[:50]}...")

    def get_recent_messages(self, limit: int = 10) -> List[StreamMessage]:
        """
        Get recent messages

        Args:
            limit: Number of recent messages to return

        Returns:
            List of recent StreamMessage objects (most recent first)
        """
        return list(reversed(self.messages[-limit:]))

    def filter_by_type(self, message_type: MessageType) -> List[StreamMessage]:
        """
        Filter messages by type

        Args:
            message_type: Type to filter by

        Returns:
            List of messages matching type
        """
        return [msg for msg in self.messages if msg.message_type == message_type]

    async def handle_websocket(self, websocket, path):
        """
        Handle incoming WebSocket connections from frontend

        Args:
            websocket: WebSocket connection
            path: Connection path
        """
        logger.info(f"WebSocket connection established: {path}")

        try:
            async for message in websocket:
                try:
                    # Parse JSON message from frontend
                    data = json.loads(message)

                    # Capture the message
                    captured = await self.capture_message(data)

                    if captured:
                        self.store_message(captured)

                        # Send acknowledgment back to frontend
                        await websocket.send(json.dumps({
                            "status": "captured",
                            "timestamp": captured.timestamp
                        }))

                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {e}")
                    await websocket.send(json.dumps({
                        "status": "error",
                        "message": "Invalid JSON"
                    }))

        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
        except asyncio.CancelledError:
            logger.info("WebSocket handler cancelled")
            raise

    async def start(self):
        """Start the WebSocket server"""
        logger.info(f"Starting Gemini Stream Capture on {self.host}:{self.port}")

        self.server = await websockets.serve(
            self.handle_websocket,
            self.host,
            self.port
        )

        self.is_running = True
        logger.info(f"Server running on ws://{self.host}:{self.port}")

        # Keep server running
        await asyncio.Future()  # Run forever

    async def stop(self):
        """Stop the WebSocket server"""
        logger.info("Stopping Gemini Stream Capture...")

        if self.server:
            self.server.close()
            await self.server.wait_closed()

        self.is_running = False
        logger.info("Server stopped")

    def get_stats(self) -> Dict:
        """Get statistics about captured messages"""
        return {
            "total_messages": len(self.messages),
            "by_type": {
                msg_type.value: len(self.filter_by_type(msg_type))
                for msg_type in MessageType
            },
            "is_running": self.is_running
        }


async def main():
    """Main entry point for standalone testing"""
    capture = GeminiStreamCapture(port=8765)

    # Example callback
    def on_message(msg: StreamMessage):
        print(f"📨 Received: [{msg.message_type.value}] {msg.text}")

    capture.on_message_callback = on_message

    # Start server
    try:
        await capture.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        await capture.stop()


if __name__ == "__main__":
    asyncio.run(main())

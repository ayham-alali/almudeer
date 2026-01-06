"""
Al-Mudeer - WebSocket Service
Real-time updates for inbox, notifications, and analytics
Replaces polling with efficient push notifications
"""

import asyncio
import json
from typing import Dict, Set, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict

from fastapi import WebSocket, WebSocketDisconnect
from logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class WebSocketMessage:
    """Structure for WebSocket messages"""
    event: str  # "new_message", "notification", "analytics_update", etc.
    data: Dict[str, Any]
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()
    
    def to_json(self) -> str:
        return json.dumps(asdict(self))


class ConnectionManager:
    """
    Manages WebSocket connections for real-time updates.
    Organizes connections by license_id for targeted messaging.
    """
    
    def __init__(self):
        # Active connections organized by license_id
        self._connections: Dict[int, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, license_id: int):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        async with self._lock:
            if license_id not in self._connections:
                self._connections[license_id] = set()
            self._connections[license_id].add(websocket)
        logger.info(f"WebSocket connected: license {license_id} (total: {self.connection_count})")
    
    async def disconnect(self, websocket: WebSocket, license_id: int):
        """Remove a WebSocket connection"""
        async with self._lock:
            if license_id in self._connections:
                self._connections[license_id].discard(websocket)
                if not self._connections[license_id]:
                    del self._connections[license_id]
        logger.info(f"WebSocket disconnected: license {license_id}")
    
    async def send_to_license(self, license_id: int, message: WebSocketMessage):
        """Send a message to all connections for a specific license"""
        if license_id not in self._connections:
            return
        
        dead_connections = []
        json_message = message.to_json()
        
        for connection in self._connections[license_id]:
            try:
                await connection.send_text(json_message)
            except Exception as e:
                logger.debug(f"Failed to send to WebSocket: {e}")
                dead_connections.append(connection)
        
        # Clean up dead connections
        for conn in dead_connections:
            await self.disconnect(conn, license_id)
    
    async def broadcast(self, message: WebSocketMessage):
        """Send a message to all connected clients"""
        json_message = message.to_json()
        
        for license_id in list(self._connections.keys()):
            for connection in list(self._connections.get(license_id, [])):
                try:
                    await connection.send_text(json_message)
                except Exception:
                    pass
    
    @property
    def connection_count(self) -> int:
        """Get total number of active connections"""
        return sum(len(conns) for conns in self._connections.values())
    
    def get_connected_licenses(self) -> Set[int]:
        """Get set of license IDs with active connections"""
        return set(self._connections.keys())


# Global connection manager
_manager: Optional[ConnectionManager] = None


def get_websocket_manager() -> ConnectionManager:
    """Get or create the global WebSocket manager"""
    global _manager
    if _manager is None:
        _manager = ConnectionManager()
    return _manager


# ============ Event Broadcasting Helpers ============

async def broadcast_new_message(license_id: int, message_data: Dict[str, Any]):
    """Broadcast when a new inbox message arrives"""
    manager = get_websocket_manager()
    await manager.send_to_license(license_id, WebSocketMessage(
        event="new_message",
        data=message_data
    ))


async def broadcast_notification(license_id: int, notification: Dict[str, Any]):
    """Broadcast a new notification"""
    manager = get_websocket_manager()
    await manager.send_to_license(license_id, WebSocketMessage(
        event="notification",
        data=notification
    ))


async def broadcast_analytics_update(license_id: int, analytics: Dict[str, Any]):
    """Broadcast analytics data update"""
    manager = get_websocket_manager()
    await manager.send_to_license(license_id, WebSocketMessage(
        event="analytics_update",
        data=analytics
    ))


async def broadcast_task_complete(license_id: int, task_id: str, result: Dict[str, Any]):
    """Broadcast when an async task completes"""
    manager = get_websocket_manager()
    await manager.send_to_license(license_id, WebSocketMessage(
        event="task_complete",
        data={"task_id": task_id, "result": result}
    ))


# ============ Presence Broadcasting ============

async def broadcast_presence_update(license_id: int, is_online: bool, last_seen: str = None):
    """Broadcast presence status change to connected clients"""
    manager = get_websocket_manager()
    await manager.send_to_license(license_id, WebSocketMessage(
        event="presence_update",
        data={
            "is_online": is_online,
            "last_seen": last_seen
        }
    ))


async def broadcast_typing_indicator(license_id: int, sender_contact: str, is_typing: bool):
    """Broadcast typing indicator for a conversation"""
    manager = get_websocket_manager()
    await manager.send_to_license(license_id, WebSocketMessage(
        event="typing_indicator",
        data={
            "sender_contact": sender_contact,
            "is_typing": is_typing
        }
    ))


async def broadcast_recording_indicator(license_id: int, sender_contact: str, is_recording: bool):
    """Broadcast recording indicator for a conversation"""
    manager = get_websocket_manager()
    await manager.send_to_license(license_id, WebSocketMessage(
        event="recording_indicator",
        data={
            "sender_contact": sender_contact,
            "is_recording": is_recording
        }
    ))


# ============ Reaction Broadcasting ============

async def broadcast_reaction_added(license_id: int, message_id: int, emoji: str, user_type: str):
    """Broadcast when a reaction is added to a message"""
    manager = get_websocket_manager()
    await manager.send_to_license(license_id, WebSocketMessage(
        event="reaction_added",
        data={
            "message_id": message_id,
            "emoji": emoji,
            "user_type": user_type
        }
    ))


async def broadcast_reaction_removed(license_id: int, message_id: int, emoji: str, user_type: str):
    """Broadcast when a reaction is removed from a message"""
    manager = get_websocket_manager()
    await manager.send_to_license(license_id, WebSocketMessage(
        event="reaction_removed",
        data={
            "message_id": message_id,
            "emoji": emoji,
            "user_type": user_type
        }
    ))

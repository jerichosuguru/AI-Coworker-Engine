"""
WebSocket endpoint for real-time chat
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from agents import NPCAgent, DirectorAgent
from services import session_manager, security_service


class ConnectionManager:
    """Manage WebSocket connections"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        print(f"✅ WebSocket connected: {session_id}")

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            print(f"❌ WebSocket disconnected: {session_id}")

    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)


# Global connection manager
manager = ConnectionManager()

# Global director agent
director_agent = DirectorAgent()


async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time chat

    Usage:
    ws://localhost:8000/ws/{session_id}

    Send:
    {
        "npc_id": "chro",
        "message": "What are the 4 Pillars?"
    }

    Receive:
    {
        "npc_id": "chro",
        "response": "The 4 Pillars are...",
        "safety_flags": [],
        "intervention": null,
        "timestamp": "2024-01-01T12:00:00"
    }
    """
    await manager.connect(session_id, websocket)

    try:
        while True:
            # Receive message
            data = await websocket.receive_json()

            npc_id = data.get("npc_id", "chro")
            user_message = data.get("message", "")

            # Load session
            session = session_manager.load_session(session_id)
            if not session:
                await websocket.send_json({
                    "error": "Session not found"
                })
                continue

            # Sanitize input
            user_message = security_service.sanitize_user_input(user_message)

            # Check rate limit
            if not security_service.check_rate_limit(session.user_id, "chat"):
                await websocket.send_json({
                    "error": "Rate limit exceeded"
                })
                continue

            # Process with NPC
            try:
                npc_agent = NPCAgent(persona_id=npc_id)
                response_text, updated_session, safety_flags = npc_agent.process_message(
                    user_message=user_message,
                    session_state=session
                )

                # Director monitoring
                intervention = director_agent.monitor_conversation(
                    updated_session,
                    user_message
                )

                if intervention:
                    response_text = intervention["message"]

                # Save session
                session_manager.save_session(updated_session)

                # Send response
                await manager.send_message(session_id, {
                    "npc_id": npc_id,
                    "response": response_text,
                    "safety_flags": safety_flags,
                    "intervention": intervention["type"] if intervention else None,
                    "timestamp": datetime.now().isoformat()
                })

            except Exception as e:
                await websocket.send_json({
                    "error": f"Processing error: {e}"
                })

    except WebSocketDisconnect:
        manager.disconnect(session_id)
        print(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(session_id)

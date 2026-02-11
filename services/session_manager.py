"""
Session Manager - Handle session state with Redis
"""
import json
import sys
from pathlib import Path
from typing import Optional, Dict
from datetime import timedelta

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from models.state import SessionState
from config import REDIS_HOST, REDIS_PORT, SESSION_TTL

# Try to import redis
try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️  redis package not installed. Using in-memory storage.")


class SessionManager:
    """
    Manage user sessions with Redis storage (or in-memory fallback)

    Features:
    - Store/retrieve session state
    - TTL-based auto-cleanup
    - Thread-safe operations
    """

    def __init__(self, redis_host: str = REDIS_HOST, redis_port: int = REDIS_PORT):
        """Initialize Redis connection or fallback to memory"""
        self.redis_enabled = False
        self.redis_client = None
        self.memory_store: Dict[str, str] = {}

        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    db=0,
                    decode_responses=True,
                    socket_connect_timeout=5
                )
                # Test connection
                self.redis_client.ping()
                self.redis_enabled = True
                print(f"✅ Redis connected at {redis_host}:{redis_port}")
            except (redis.ConnectionError, redis.TimeoutError, Exception) as e:
                print(f"⚠️  Redis not available: {e}")
                print("   Using in-memory storage (data will not persist)")
        else:
            print("⚠️  Redis package not installed")
            print("   Using in-memory storage (data will not persist)")

    def save_session(self, session: SessionState) -> bool:
        """
        Save session to Redis or memory

        Args:
            session: SessionState object

        Returns:
            True if successful
        """
        try:
            # Serialize session to JSON
            session_json = session.model_dump_json()

            # Generate Redis key
            key = f"session:{session.session_id}"

            if self.redis_enabled:
                # Save to Redis with TTL
                self.redis_client.setex(
                    name=key,
                    time=timedelta(seconds=SESSION_TTL),
                    value=session_json
                )
            else:
                # Save to in-memory store
                self.memory_store[key] = session_json

            return True

        except Exception as e:
            print(f"❌ Error saving session: {e}")
            return False

    def load_session(self, session_id: str) -> Optional[SessionState]:
        """
        Load session from Redis or memory

        Args:
            session_id: Session identifier

        Returns:
            SessionState object or None if not found
        """
        try:
            key = f"session:{session_id}"

            if self.redis_enabled:
                # Load from Redis
                session_json = self.redis_client.get(key)
            else:
                # Load from memory
                session_json = self.memory_store.get(key)

            if session_json:
                # Deserialize from JSON
                session_dict = json.loads(session_json) if isinstance(session_json, str) else session_json
                return SessionState(**session_dict)

            return None

        except Exception as e:
            print(f"❌ Error loading session: {e}")
            return None

    def delete_session(self, session_id: str) -> bool:
        """
        Delete session

        Args:
            session_id: Session identifier

        Returns:
            True if successful
        """
        try:
            key = f"session:{session_id}"

            if self.redis_enabled:
                self.redis_client.delete(key)
            else:
                self.memory_store.pop(key, None)

            return True

        except Exception as e:
            print(f"❌ Error deleting session: {e}")
            return False

    def session_exists(self, session_id: str) -> bool:
        """Check if session exists"""
        try:
            key = f"session:{session_id}"

            if self.redis_enabled:
                return self.redis_client.exists(key) > 0
            else:
                return key in self.memory_store

        except Exception as e:
            print(f"❌ Error checking session: {e}")
            return False

    def extend_session(self, session_id: str, ttl_seconds: int = SESSION_TTL) -> bool:
        """Extend session TTL"""
        try:
            key = f"session:{session_id}"

            if self.redis_enabled:
                self.redis_client.expire(key, ttl_seconds)
                return True
            else:
                # In-memory doesn't support TTL extension
                return True

        except Exception as e:
            print(f"❌ Error extending session: {e}")
            return False

    def get_all_sessions(self, user_id: Optional[str] = None) -> list:
        """Get all session IDs (optionally filtered by user)"""
        try:
            if self.redis_enabled:
                # Scan Redis for session keys
                session_keys = []
                for key in self.redis_client.scan_iter(match="session:*"):
                    if user_id:
                        # Load and check user_id
                        session_json = self.redis_client.get(key)
                        if session_json:
                            session = SessionState(**json.loads(session_json))
                            if session.user_id == user_id:
                                session_keys.append(key.replace("session:", ""))
                    else:
                        session_keys.append(key.replace("session:", ""))

                return session_keys
            else:
                # Return from memory store
                return [k.replace("session:", "") for k in self.memory_store.keys()]

        except Exception as e:
            print(f"❌ Error getting sessions: {e}")
            return []


# Global session manager instance
session_manager = SessionManager()
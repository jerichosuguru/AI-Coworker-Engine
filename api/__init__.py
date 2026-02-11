"""
API package initialization
"""
from .routes import router
from .websocket import websocket_endpoint
from .middleware import setup_middleware

__all__ = [
    "router",
    "websocket_endpoint",
    "setup_middleware",
]
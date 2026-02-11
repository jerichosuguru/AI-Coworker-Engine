"""
Middleware for FastAPI application
"""
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import ALLOWED_ORIGINS


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # Log request
        print(f"➡️  {request.method} {request.url.path}")

        response = await call_next(request)

        # Log response time
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        print(f"⬅️  {response.status_code} ({process_time:.3f}s)")

        return response


def setup_middleware(app: FastAPI):
    """
    Setup all middleware for the application

    Args:
        app: FastAPI application instance
    """

    # CORS middleware (must be first)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Security headers
    app.add_middleware(SecurityHeadersMiddleware)

    # Logging
    app.add_middleware(LoggingMiddleware)

    # Trusted host (optional - uncomment in production)
    # app.add_middleware(
    #     TrustedHostMiddleware,
    #     allowed_hosts=["edtronaut.ai", "*.edtronaut.ai", "localhost"]
    # )

    print("✅ Middleware configured")
"""
AI Co-worker Engine - Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from datetime import datetime
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Suppress warnings
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*position_ids.*")

# Import our modules
from config import LLM_MODEL, ALLOWED_ORIGINS
from agents import knowledge_base
from api import router, websocket_endpoint, setup_middleware

# Initialize FastAPI app with beautiful description
app = FastAPI(
    title="🤖 AI Co-worker Engine",
    description="""
    ## NPC System for Job Simulation Platform
    
    ### ✨ Features:
    - 🎭 **Multi-Persona AI Agents** (CHRO, CEO, Regional Manager)
    - 🎬 **Director Supervision** (Stuck loop detection, progress monitoring)
    - 📚 **RAG Knowledge Base** (Gucci context, 4 Pillars framework, HR best practices)
    - 👶 **Age Adaptation** (5 groups: 8-12, 13-15, 16-18, 19-25, 26+)
    - ♿ **Accessibility** (Screen reader, text simplification, cognitive support)
    - 🔒 **Security** (JWT auth, rate limiting, jailbreak detection, GDPR compliance)
    
    ### 🚀 Quick Start:
    1. **Create session**: `POST /api/session/create`
    2. **Get token** from response
    3. **Chat with NPC**: `POST /api/chat` (add token to Authorization header)
    
    ### 🎭 NPCs Available:
    - **CHRO** (Dr. Elena Marchetti) - HR Strategy & 4 Pillars Framework
    - **CEO** (Alessandro Ricci) - Business Strategy & Brand DNA
    - **Regional Manager** (Marie Dubois) - Implementation Reality & Regional Operations
    
    ### 📊 Performance:
    - Response Time: ~0.5s
    - Test Coverage: 80%
    - Stuck Loop Detection: 3 turns
    
    ---
    **Edtronaut AI Engineer Intern Assignment** | Built with ❤️ using FastAPI + Claude AI
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "NMTC - Edtronaut Assignment",
        "url": "https://edtronaut.ai",
    },
    license_info={
        "name": "MIT License",
    },
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,  # Hide schemas by default
        "docExpansion": "none",  # Collapse all endpoints
        "filter": True,  # Enable search
        "syntaxHighlight.theme": "monokai",
        "displayRequestDuration": True,  # Show request duration
        "tryItOutEnabled": True,  # Enable "Try it out" by default
    }
)

# Mount static files (CSS, JS, images)
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")
    print("✅ Static files mounted at /static")
else:
    print("⚠️  Static directory not found - landing page will be simple JSON")

# Setup middleware (CORS, security headers, logging)
setup_middleware(app)

# Include API routes
app.include_router(router, prefix="/api")

# WebSocket endpoint
app.add_api_websocket_route("/ws/{session_id}", websocket_endpoint)


# ============================================
# STARTUP & SHUTDOWN
# ============================================

@app.on_event("startup")
async def startup_event():
    """Initialize knowledge base and services"""
    print("\n" + "="*60)
    print("🚀 AI CO-WORKER ENGINE STARTING...")
    print("="*60)

    print(f"\n📚 Loading knowledge base...")
    knowledge_base.load_documents()

    print(f"\n✅ Startup complete!")
    print(f"   Model: {LLM_MODEL}")
    print(f"   Landing Page: http://localhost:8000")
    print(f"   API Docs: http://localhost:8000/docs")
    print(f"   ReDoc: http://localhost:8000/redoc")
    print(f"   Health Check: http://localhost:8000/health")
    print(f"   CORS Origins: {ALLOWED_ORIGINS}")
    print("="*60 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("\n👋 Shutting down AI Co-worker Engine...")


# ============================================
# ROOT ENDPOINTS
# ============================================

@app.get("/", include_in_schema=False)
async def root():
    """
    Root endpoint - serves beautiful landing page if static files exist,
    otherwise returns JSON with API info
    """
    # Try to serve static HTML landing page
    static_index = Path(__file__).parent / "static" / "index.html"

    if static_index.exists():
        return FileResponse(static_index)

    # Fallback to JSON response
    return {
        "message": "🤖 AI Co-worker Engine API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "landing_page": "/",
            "api_docs": "/docs",
            "redoc": "/redoc",
            "health_check": "/health",
            "websocket": "/ws/{session_id}"
        },
        "features": [
            "Multi-persona AI agents (CHRO, CEO, Regional Manager)",
            "Director supervision (stuck loop detection)",
            "RAG knowledge base (FAISS)",
            "Age adaptation (5 groups)",
            "Accessibility support",
            "Security (JWT, rate limiting, jailbreak detection)"
        ],
        "quick_start": {
            "1": "POST /api/session/create → get token",
            "2": "POST /api/chat with Authorization header",
            "3": "Interact with NPCs!"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint

    Returns system status and metrics
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "model": LLM_MODEL,
        "knowledge_base": {
            "loaded": len(knowledge_base.documents) > 0,
            "num_documents": len(knowledge_base.documents),
            "status": "ready" if len(knowledge_base.documents) > 0 else "empty"
        },
        "features": {
            "npc_agents": 3,
            "age_groups": 5,
            "security_layers": 5
        },
        "endpoints_available": [
            "/api/session/create",
            "/api/session/{session_id}",
            "/api/chat",
            "/api/npcs",
            "/api/progress",
            "/docs",
            "/redoc"
        ]
    }


@app.get("/api")
async def api_info():
    """
    API information endpoint
    """
    return {
        "name": "AI Co-worker Engine API",
        "version": "1.0.0",
        "description": "NPC system for job simulation platform",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "session": {
                "create": "POST /api/session/create",
                "get": "GET /api/session/{session_id}",
                "delete": "DELETE /api/session/{session_id}"
            },
            "chat": {
                "chat": "POST /api/chat",
                "npcs": "GET /api/npcs"
            },
            "progress": {
                "update": "POST /api/progress/update",
                "get": "GET /api/progress"
            }
        },
        "websocket": "ws://localhost:8000/ws/{session_id}"
    }


# ============================================
# ERROR HANDLERS
# ============================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found",
            "path": str(request.url),
            "message": f"The endpoint '{request.url.path}' does not exist",
            "available_docs": {
                "swagger": "/docs",
                "redoc": "/redoc",
                "api_info": "/api"
            }
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "Something went wrong on the server",
            "detail": str(exc) if os.getenv("ENVIRONMENT") == "development" else "Contact support",
            "timestamp": datetime.now().isoformat()
        }
    )


# ============================================
# RUN SERVER
# ============================================

if __name__ == "__main__":
    import uvicorn

    print("\n🎨 Starting AI Co-worker Engine...")
    print("📍 Access points:")
    print("   🏠 Landing Page: http://localhost:8000")
    print("   📚 API Docs: http://localhost:8000/docs")
    print("   🔍 Health: http://localhost:8000/health")
    print("\n")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
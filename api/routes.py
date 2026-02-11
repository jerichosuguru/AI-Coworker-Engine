"""
API Routes - REST endpoints for AI Co-worker Engine
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional, Dict
import sys
from pathlib import Path
from datetime import datetime
import uuid

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from models import SessionState, ProgressState, UserProfile
from agents import NPCAgent, DirectorAgent, knowledge_base
from services import session_manager, security_service, adaptation_service
from models.personas import PERSONA_REGISTRY

# Create router
router = APIRouter()

# Initialize director agent
director_agent = DirectorAgent()


# ============================================
# AUTHENTICATION DEPENDENCY
# ============================================

async def verify_session(authorization: Optional[str] = Header(None)) -> str:
    """
    Verify session token and return session_id
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    try:
        # Extract token (format: "Bearer <token>")
        token = authorization.replace("Bearer ", "")

        # Verify token
        token_data = security_service.verify_token(token)

        if not token_data:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        return token_data.session_id

    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {e}")


# ============================================
# SESSION MANAGEMENT ENDPOINTS
# ============================================

@router.post("/session/create")
async def create_session(user_profile: Optional[UserProfile] = None):
    """
    Create new simulation session

    Request body (optional):
    {
        "user_id": "user_123",
        "age": 16,
        "age_group": {...},
        "accessibility": {...}
    }

    Returns:
    {
        "status": "success",
        "session_id": "uuid",
        "user_id": "user_123",
        "token": "jwt_token",
        "expires_in": 3600
    }
    """
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())
        user_id = user_profile.user_id if user_profile else f"user_{uuid.uuid4().hex[:8]}"

        # Create session state
        session = SessionState(
            session_id=session_id,
            user_id=user_id,
            simulation_id="gucci_hrm_leadership",
            progress=ProgressState(current_module=1)
        )

        # Save session
        session_manager.save_session(session)

        # Create access token
        token = security_service.create_access_token(
            user_id=user_id,
            session_id=session_id
        )

        return {
            "status": "success",
            "session_id": session_id,
            "user_id": user_id,
            "token": token,
            "expires_in": 3600  # 1 hour
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {e}")


@router.get("/session/{session_id}")
async def get_session(session_id: str = Depends(verify_session)):
    """
    Get current session state

    Returns:
    {
        "status": "success",
        "session": {...}
    }
    """
    session = session_manager.load_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "status": "success",
        "session": session.model_dump()
    }


@router.delete("/session/{session_id}")
async def delete_session(session_id: str = Depends(verify_session)):
    """
    Delete session

    Returns:
    {
        "status": "success",
        "message": "Session deleted"
    }
    """
    success = session_manager.delete_session(session_id)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete session")

    return {"status": "success", "message": "Session deleted"}


# ============================================
# NPC CHAT ENDPOINTS
# ============================================

@router.post("/chat")
async def chat_with_npc(
    request: dict,
    session_id: str = Depends(verify_session)
):
    """
    Send message to NPC

    Request body:
    {
        "npc_id": "chro",
        "message": "Can you explain the 4 Pillars?",
        "user_profile": {...}  // optional
    }

    Returns:
    {
        "status": "success",
        "npc_id": "chro",
        "response": "The 4 Pillars are...",
        "safety_flags": [],
        "intervention": null,
        "relationship_score": 1
    }
    """
    try:
        # Validate request
        npc_id = request.get("npc_id")
        user_message = request.get("message")
        user_profile_data = request.get("user_profile")

        if not npc_id or not user_message:
            raise HTTPException(status_code=400, detail="Missing npc_id or message")

        # Load session
        session = session_manager.load_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Sanitize user input
        user_message = security_service.sanitize_user_input(user_message)

        # Check rate limit
        if not security_service.check_rate_limit(session.user_id, "chat"):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        # Initialize NPC agent
        npc_agent = NPCAgent(persona_id=npc_id)

        # Process message
        response_text, updated_session, safety_flags = npc_agent.process_message(
            user_message=user_message,
            session_state=session
        )

        # Director monitoring
        intervention = director_agent.monitor_conversation(
            updated_session,
            user_message
        )

        # Apply intervention if needed
        if intervention:
            response_text = intervention["message"]
            updated_session.stuck_loop_count = updated_session.stuck_loop_count or 0

        # Adapt response for user profile (if provided)
        adapted_response = response_text
        if user_profile_data:
            user_profile = UserProfile(**user_profile_data)
            adaptation_result = adaptation_service.adapt_npc_response(
                npc_id=npc_id,
                original_response=response_text,
                user_profile=user_profile
            )
            adapted_response = adaptation_result["text"]

        # Save updated session
        session_manager.save_session(updated_session)

        # Response
        return {
            "status": "success",
            "npc_id": npc_id,
            "response": adapted_response,
            "original_response": response_text if user_profile_data else None,
            "safety_flags": safety_flags,
            "intervention": intervention["type"] if intervention else None,
            "relationship_score": updated_session.relationships.get(npc_id).score if npc_id in updated_session.relationships else 0,
            "session_updated": True
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {e}")


@router.get("/npcs")
async def get_available_npcs():
    """
    Get list of available NPCs

    Returns:
    {
        "status": "success",
        "npcs": [
            {
                "npc_id": "chro",
                "name": "Dr. Elena Marchetti",
                "role": "Chief Human Resources Officer",
                "knowledge_domains": [...]
            }
        ]
    }
    """
    npcs = []
    for npc_id, persona in PERSONA_REGISTRY.items():
        npcs.append({
            "npc_id": npc_id,
            "name": persona.name,
            "role": persona.role,
            "knowledge_domains": persona.knowledge_domains
        })

    return {
        "status": "success",
        "npcs": npcs
    }


# ============================================
# PROGRESS TRACKING ENDPOINTS
# ============================================

@router.post("/progress/update")
async def update_progress(
    request: dict,
    session_id: str = Depends(verify_session)
):
    """
    Update simulation progress

    Request body:
    {
        "current_module": 2,
        "current_task": "Design 360 program",
        "completed_tasks": ["define_dna", "create_framework"]
    }

    Returns:
    {
        "status": "success",
        "progress": {...}
    }
    """
    try:
        session = session_manager.load_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Update progress
        if "current_module" in request:
            session.progress.current_module = request["current_module"]

        if "current_task" in request:
            session.progress.current_task = request["current_task"]

        if "completed_tasks" in request:
            session.progress.completed_tasks = request["completed_tasks"]

        # Save
        session_manager.save_session(session)

        return {
            "status": "success",
            "progress": session.progress.model_dump()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update progress: {e}")


@router.get("/progress")
async def get_progress(session_id: str = Depends(verify_session)):
    """
    Get current progress

    Returns:
    {
        "status": "success",
        "progress": {...},
        "relationships": {...}
    }
    """
    session = session_manager.load_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "status": "success",
        "progress": session.progress.model_dump(),
        "relationships": {
            npc_id: rel.model_dump()
            for npc_id, rel in session.relationships.items()
        }
    }
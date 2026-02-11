"""
State management schemas for conversation tracking
"""
from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class Message(BaseModel):
    """Single message in conversation"""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    npc_id: Optional[str] = None
    metadata: Dict = Field(default_factory=dict)


class RelationshipState(BaseModel):
    """Track relationship with each NPC"""
    npc_id: str
    score: int = Field(default=0, ge=-10, le=10)  # -10 (hostile) to +10 (warm)
    interaction_count: int = 0
    last_sentiment: Optional[str] = None  # "positive", "neutral", "negative"


class ProgressState(BaseModel):
    """Track simulation progress"""
    current_module: int = 1  # Module 1, 2, or 3
    completed_tasks: List[str] = Field(default_factory=list)
    current_task: Optional[str] = None
    deliverables: Dict[str, bool] = Field(default_factory=dict)


class SessionState(BaseModel):
    """Complete session state"""
    session_id: str
    user_id: str
    simulation_id: str = "gucci_hrm_leadership"
    
    # Conversation
    conversation_history: List[Message] = Field(default_factory=list)
    active_npc: Optional[str] = None
    
    # Relationships
    relationships: Dict[str, RelationshipState] = Field(default_factory=dict)
    
    # Progress
    progress: ProgressState = Field(default_factory=ProgressState)
    
    # Director monitoring
    stuck_loop_count: int = 0
    last_hint_timestamp: Optional[datetime] = None
    safety_flags: List[str] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def add_message(self, message: Message):
        """Add message and update state"""
        self.conversation_history.append(message)
        self.updated_at = datetime.now()
        
        # Update relationship if NPC message
        if message.npc_id and message.npc_id in self.relationships:
            self.relationships[message.npc_id].interaction_count += 1
    
    def get_recent_history(self, n: int = 10) -> List[Message]:
        """Get last N messages"""
        return self.conversation_history[-n:]
    
    def update_relationship_score(self, npc_id: str, delta: int):
        """Update relationship score"""
        if npc_id not in self.relationships:
            self.relationships[npc_id] = RelationshipState(npc_id=npc_id)

        current = self.relationships[npc_id].score
        new_score = max(-10, min(10, current + delta))
        self.relationships[npc_id].score = new_score
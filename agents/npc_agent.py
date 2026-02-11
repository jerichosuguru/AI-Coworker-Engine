"""
NPC Agent - The core AI co-worker engine
"""
import anthropic
from typing import Dict, Tuple, Optional, List
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from models.state import SessionState, Message, RelationshipState
from models.personas import PERSONA_REGISTRY, PersonaConfig
from config import ANTHROPIC_API_KEY, LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS


class NPCAgent:
    """
    AI Co-worker Agent that embodies a specific persona

    Handles:
    - Loading persona configuration
    - Managing conversation context
    - Generating responses via LLM
    - Tracking relationship state
    - Safety checks
    """

    def __init__(self, persona_id: str, api_key: str = ANTHROPIC_API_KEY):
        """
        Initialize NPC with a specific persona

        Args:
            persona_id: ID of persona from PERSONA_REGISTRY
            api_key: Anthropic API key
        """
        if persona_id not in PERSONA_REGISTRY:
            raise ValueError(f"Unknown persona_id: {persona_id}. Available: {list(PERSONA_REGISTRY.keys())}")

        self.persona_id = persona_id
        self.persona: PersonaConfig = PERSONA_REGISTRY[persona_id]

        # Initialize Anthropic client
        if not api_key or api_key.startswith("your_"):
            print(f"⚠️  Warning: ANTHROPIC_API_KEY not set. Using mock responses.")
            self.client = None
        else:
            self.client = anthropic.Anthropic(api_key=api_key)

    def process_message(
        self,
        user_message: str,
        session_state: SessionState
    ) -> Tuple[str, SessionState, List[str]]:
        """
        Main method: Process user message and generate NPC response

        Args:
            user_message: User's input
            session_state: Current session state

        Returns:
            Tuple of (assistant_message, updated_state, safety_flags)
        """

        # 1. Safety checks
        safety_flags = self._safety_check(user_message)
        if "jailbreak" in safety_flags or "profanity" in safety_flags:
            response = self._generate_safety_response(safety_flags)
            return response, session_state, safety_flags

        # 2. Build context for LLM
        system_prompt = self._build_system_prompt(session_state)
        messages = self._build_message_history(session_state, user_message)

        # 3. Call LLM
        response_text = self._call_llm(system_prompt, messages)

        # 4. Analyze sentiment & update relationship
        sentiment = self._analyze_sentiment(response_text)
        session_state = self._update_relationship(session_state, sentiment)

        # 5. Update session state
        user_msg = Message(
            role="user",
            content=user_message,
            npc_id=None
        )
        assistant_msg = Message(
            role="assistant",
            content=response_text,
            npc_id=self.persona_id,
            metadata={"sentiment": sentiment}
        )

        session_state.add_message(user_msg)
        session_state.add_message(assistant_msg)
        session_state.active_npc = self.persona_id

        return response_text, session_state, safety_flags

    def _build_system_prompt(self, session_state: SessionState) -> str:
        """Build dynamic system prompt with context"""
        base_prompt = self.persona.system_prompt

        # Add current module context
        module_context = f"\n\n## Current Context\nThe user is in Module {session_state.progress.current_module}."

        if session_state.progress.current_module == 1:
            module_context += "\nFocus: Defining Group DNA and Competency Framework."
        elif session_state.progress.current_module == 2:
            module_context += "\nFocus: Designing 360° feedback and coaching program."
        elif session_state.progress.current_module == 3:
            module_context += "\nFocus: Cascading and measuring adoption."

        # Add relationship context
        relationship = session_state.relationships.get(self.persona_id)
        if relationship:
            score = relationship.score
            if score > 5:
                module_context += "\n\nRelationship: Warm and collaborative. Share more stories."
            elif score < -2:
                module_context += "\n\nRelationship: Strained. Be more formal but still helpful."

        # Add task reminder
        current_task = session_state.progress.current_task
        if current_task:
            module_context += f"\n\nCurrent task user is working on: {current_task}"

        return base_prompt + module_context

    def _build_message_history(
        self,
        session_state: SessionState,
        user_message: str
    ) -> List[Dict[str, str]]:
        """Build conversation history for LLM context"""
        recent_history = session_state.get_recent_history(n=10)

        messages = []
        for msg in recent_history:
            if msg.role in ["user", "assistant"]:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })

        return messages

    def _call_llm(self, system_prompt: str, messages: List[Dict]) -> str:
        """Call Anthropic Claude API"""
        if not self.client:
            # Mock response if no API key
            return self._generate_mock_response(messages[-1]["content"])

        try:
            response = self.client.messages.create(
                model=LLM_MODEL,
                max_tokens=LLM_MAX_TOKENS,
                temperature=LLM_TEMPERATURE,
                system=system_prompt,
                messages=messages
            )

            return response.content[0].text

        except Exception as e:
            print(f"❌ LLM API Error: {e}")
            return self._generate_fallback_response()

    def _generate_mock_response(self, user_message: str) -> str:
        """Generate mock response when API key not available"""
        return f"[MOCK RESPONSE from {self.persona.name}] I understand you're asking about: '{user_message[:50]}...'. This is a mock response because ANTHROPIC_API_KEY is not configured. Please add your API key to .env file to get real AI responses."

    def _safety_check(self, user_message: str) -> List[str]:
        """Check for safety issues"""
        flags = []

        # Check message length
        if len(user_message) > 2000:
            flags.append("too_long")

        # Check for jailbreak attempts
        jailbreak_patterns = [
            "ignore previous instructions",
            "ignore all previous",
            "you are now",
            "forget your role",
            "disregard your",
            "new instructions:",
            "system:",
            "override"
        ]

        user_lower = user_message.lower()
        for pattern in jailbreak_patterns:
            if pattern in user_lower:
                flags.append("jailbreak")
                break

        return flags

    def _generate_safety_response(self, flags: List[str]) -> str:
        """Generate response for safety violations"""
        if "jailbreak" in flags:
            return (
                f"I appreciate your creativity, but I need to stay in character as "
                f"{self.persona.name}, {self.persona.role}. Let's focus on the leadership "
                f"development challenge at hand. What aspect would you like to explore?"
            )

        if "too_long" in flags:
            return (
                f"That's quite a detailed message! Could you break it down into smaller questions? "
                f"I want to make sure I address each point properly."
            )

        return "I'm here to help with the Gucci leadership development simulation. What would you like to discuss?"

    def _analyze_sentiment(self, response_text: str) -> str:
        """Simple sentiment analysis of assistant's response"""
        positive_keywords = ["excellent", "great", "exactly", "perfect", "wonderful", "yes", "good"]
        negative_keywords = ["concern", "however", "but", "careful", "issue", "problem"]

        response_lower = response_text.lower()

        pos_count = sum(1 for kw in positive_keywords if kw in response_lower)
        neg_count = sum(1 for kw in negative_keywords if kw in response_lower)

        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        else:
            return "neutral"

    def _update_relationship(
        self,
        session_state: SessionState,
        sentiment: str
    ) -> SessionState:
        """Update relationship score based on sentiment"""
        if self.persona_id not in session_state.relationships:
            session_state.relationships[self.persona_id] = RelationshipState(
                npc_id=self.persona_id
            )

        # Update based on sentiment
        delta = 0
        if sentiment == "positive":
            delta = 1
        elif sentiment == "negative":
            delta = -1

        session_state.update_relationship_score(self.persona_id, delta)
        session_state.relationships[self.persona_id].last_sentiment = sentiment

        return session_state

    def _generate_fallback_response(self) -> str:
        """Fallback response if LLM fails"""
        return (
            f"I apologize, I'm having trouble processing that right now. "
            f"Could you rephrase your question about the leadership development program?"
        )

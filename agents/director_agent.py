"""
Director Agent - Invisible supervisor that monitors and guides simulation
"""
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import sys
from pathlib import Path
import numpy as np

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from models.state import SessionState, Message
from sentence_transformers import SentenceTransformer
from config import STUCK_LOOP_THRESHOLD, SIMILARITY_THRESHOLD


class DirectorAgent:
    """
    Supervisor agent that monitors conversation and intervenes when needed

    Responsibilities:
    - Detect stuck loops (user repeating questions)
    - Detect off-topic conversations
    - Suggest next steps when user completes a task
    - Safety monitoring
    """

    def __init__(self):
        # Load embedding model for semantic similarity
        print("🔄 Loading Director Agent embedding model...")
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Director Agent ready")
        except Exception as e:
            print(f"⚠️  Could not load embedding model: {e}")
            self.embedding_model = None

    def monitor_conversation(
        self,
        session_state: SessionState,
        latest_user_message: str
    ) -> Optional[Dict]:
        """
        Main monitoring function - called after each user message

        Returns:
            Intervention dict if action needed, None otherwise
            {
                "type": "hint" | "redirect" | "progress_check",
                "message": str,
                "metadata": dict
            }
        """

        # 1. Check for stuck loop
        if self._is_stuck_loop(session_state, latest_user_message):
            return self._generate_hint(session_state)

        # 2. Check if off-topic
        if self._is_off_topic(latest_user_message, session_state):
            return self._generate_redirect(session_state)

        # 3. Check if should advance to next task
        if self._should_suggest_next_step(session_state):
            return self._generate_progress_nudge(session_state)

        return None  # No intervention needed

    def _is_stuck_loop(self, session_state: SessionState, latest_message: str) -> bool:
        """Detect if user is asking similar questions repeatedly"""
        if not self.embedding_model:
            return False  # Can't detect without embeddings

        # Get recent user messages
        history = session_state.get_recent_history(n=10)
        user_messages = [msg.content for msg in history if msg.role == "user"]

        if len(user_messages) < STUCK_LOOP_THRESHOLD:
            return False

        # Get last N user messages (including latest)
        recent_messages = user_messages[-(STUCK_LOOP_THRESHOLD-1):] + [latest_message]

        try:
            # Compute embeddings
            embeddings = self.embedding_model.encode(recent_messages)

            # Calculate pairwise similarities
            similarities = []
            for i in range(len(embeddings) - 1):
                sim = self._cosine_similarity(embeddings[i], embeddings[-1])
                similarities.append(sim)

            # If all recent messages are very similar, it's a loop
            avg_similarity = np.mean(similarities)

            return avg_similarity > SIMILARITY_THRESHOLD
        except Exception as e:
            print(f"⚠️  Error in stuck loop detection: {e}")
            return False

    def _is_off_topic(self, user_message: str, session_state: SessionState) -> bool:
        """Detect if conversation has drifted off-topic"""
        # Define on-topic keywords per module
        module_keywords = {
            1: ["competency", "framework", "vision", "entrepreneurship", "passion",
                "trust", "dna", "brand", "talent", "leadership", "pillars"],
            2: ["360", "feedback", "coaching", "assessment", "rater", "survey",
                "questionnaire", "development", "program", "degree"],
            3: ["rollout", "cascade", "training", "implementation", "regional",
                "adoption", "measurement", "kpi", "train"]
        }

        current_module = session_state.progress.current_module
        keywords = module_keywords.get(current_module, [])

        # Check if message contains any relevant keywords
        message_lower = user_message.lower()
        matches = sum(1 for kw in keywords if kw in message_lower)

        # Also check for clearly off-topic patterns
        off_topic_patterns = [
            "favorite color", "weather", "sports", "movie", "food",
            "personal life", "weekend", "vacation", "hobby", "lunch",
            "dinner", "breakfast", "pet", "family"
        ]

        for pattern in off_topic_patterns:
            if pattern in message_lower:
                return True

        # If very few keyword matches and message is long, likely off-topic
        if matches == 0 and len(user_message.split()) > 10:
            return True

        return False

    def _should_suggest_next_step(self, session_state: SessionState) -> bool:
        """Check if user has been discussing same topic for too long"""
        # If user has had 8+ messages with same NPC without progress, suggest next step
        if session_state.active_npc:
            npc_messages = [
                msg for msg in session_state.get_recent_history(15)
                if msg.npc_id == session_state.active_npc
            ]

            if len(npc_messages) >= 8:
                # In real system, track task completion events
                return True

        return False

    def _generate_hint(self, session_state: SessionState) -> Dict:
        """Generate hint to help user get unstuck"""
        current_module = session_state.progress.current_module
        active_npc = session_state.active_npc or "chro"

        # Module-specific hints
        hints = {
            ("chro", 1): (
                "I notice we've been discussing the framework theory quite a bit. "
                "Let's make this concrete. Try drafting a competency matrix - "
                "pick one pillar (Vision, Entrepreneurship, Passion, or Trust) and "
                "write 2-3 behavioral indicators for Junior, Mid, and Senior levels. "
                "That will help us move forward."
            ),
            ("chro", 2): (
                "We've covered several aspects of 360° feedback. To progress, "
                "why don't you outline the rater groups you'd include? "
                "For example: manager, peers, direct reports, self-assessment. "
                "How many of each, and why?"
            ),
            ("regional_manager", 3): (
                "I sense you're thinking through the rollout challenges. "
                "Let me ask a concrete question: If you had to train 50 local HR "
                "managers across Europe in 3 months, what would your Week 1 agenda look like? "
                "Walking through a specific example might clarify your approach."
            ),
            ("ceo", 1): (
                "We've discussed the strategic rationale. Now I need to see the business case. "
                "What's the ROI? How does this make us more competitive? "
                "Give me three metrics you'd track to prove this works."
            )
        }

        hint_message = hints.get((active_npc, current_module),
            "Let's try approaching this from a different angle. What specific "
            "deliverable are you working on right now?"
        )

        # Update state
        session_state.stuck_loop_count += 1
        session_state.last_hint_timestamp = datetime.now()

        return {
            "type": "hint",
            "message": hint_message,
            "metadata": {
                "stuck_count": session_state.stuck_loop_count,
                "npc": active_npc,
                "module": current_module
            }
        }

    def _generate_redirect(self, session_state: SessionState) -> Dict:
        """Gently redirect off-topic conversation"""
        active_npc = session_state.active_npc or "chro"

        redirect_messages = {
            "chro": (
                "I appreciate the conversation, but let's refocus on the leadership "
                "development challenge. We're designing a competency framework for "
                "Gucci Group. What aspect would you like to explore next?"
            ),
            "ceo": (
                "That's an interesting topic, but my priority is ensuring this "
                "leadership system strengthens our brands. What's your thinking "
                "on balancing Group standards with brand autonomy?"
            ),
            "regional_manager": (
                "I'd love to chat more, but I have limited time today. "
                "Let's focus on the rollout plan - what are your main concerns "
                "about cascading this across regions?"
            )
        }

        return {
            "type": "redirect",
            "message": redirect_messages.get(active_npc, redirect_messages["chro"]),
            "metadata": {"npc": active_npc}
        }

    def _generate_progress_nudge(self, session_state: SessionState) -> Dict:
        """Suggest moving to next task or module"""
        current_module = session_state.progress.current_module

        nudge_messages = {
            1: (
                "You've explored the competency framework quite thoroughly. "
                "Are you ready to move on to designing the 360° feedback program in Module 2? "
                "Or is there something else about the framework you'd like to finalize first?"
            ),
            2: (
                "The 360° program design is taking shape. Once you're satisfied, "
                "we should discuss the rollout and change management in Module 3. "
                "Would you like to continue refining this, or move forward?"
            ),
            3: (
                "We've covered the cascade and measurement plan extensively. "
                "Do you have everything you need for your deliverables, or are "
                "there specific aspects you'd like to dig deeper into?"
            )
        }

        return {
            "type": "progress_check",
            "message": nudge_messages.get(current_module, "How is your progress?"),
            "metadata": {"current_module": current_module}
        }

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm_product = np.linalg.norm(vec1) * np.linalg.norm(vec2)
        return float(dot_product / norm_product) if norm_product > 0 else 0.0
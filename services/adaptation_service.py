"""
Adaptation Service - Age-appropriate and ability-aware content
"""
from typing import Dict, Optional
import sys
from pathlib import Path
import random

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from models.user_profile import UserProfile, AgeGroup
from agents.accessibility_agent import AccessibilityAgent


class AdaptationService:
    """
    Adapts NPC interactions based on user age and abilities

    Age Groups:
    - 8-12: Children (elementary school)
    - 13-15: Teens (middle school)
    - 16-18: Young adults (high school)
    - 19-25: College students / Early career professionals
    - 26+: Experienced professionals
    """

    def __init__(self):
        self.accessibility_agent = AccessibilityAgent()
        self.age_personas = self._load_age_adapted_personas()

    def adapt_npc_response(
        self,
        npc_id: str,
        original_response: str,
        user_profile: UserProfile
    ) -> Dict:
        """
        Adapt NPC response for user's age and accessibility needs
        """
        adapted = original_response

        # 1. Age adaptation
        if user_profile.age:
            adapted = self._adapt_for_age(adapted, user_profile)

        # 2. Accessibility adaptation
        adapted_result = self.accessibility_agent.adapt_message(
            adapted,
            user_profile
        )

        # 3. Add age-appropriate encouragement
        if user_profile.age_group.encouragement_level == "high":
            adapted_result["text"] = self._add_encouragement(
                adapted_result["text"],
                user_profile.age_group.age_range
            )
        elif user_profile.age_group.encouragement_level == "moderate":
            adapted_result["text"] = self._add_encouragement(
                adapted_result["text"],
                user_profile.age_group.age_range,
                frequency=0.3  # 30% of time
            )

        return adapted_result

    def _adapt_for_age(self, text: str, user_profile: UserProfile) -> str:
        """Adapt content for specific age groups"""
        age = user_profile.age

        if age and age < 13:  # 8-12 years old
            return self._adapt_for_children(text)
        elif age and age < 16:  # 13-15 years old
            return self._adapt_for_teens(text)
        elif age and age < 19:  # 16-18 years old
            return self._adapt_for_young_adults(text)
        elif age and age < 26:  # 19-25 years old
            return self._adapt_for_college_age(text)
        else:  # 26+ years old
            return text  # Full professional content, no adaptation

    def _adapt_for_children(self, text: str) -> str:
        """Adapt for 8-12 year olds"""
        # Use simpler vocabulary
        adapted = self.accessibility_agent.simplify_text(text, level="simple")

        # Add friendly tone
        adapted = self._make_tone_friendly(adapted)

        # Remove complex business jargon
        adapted = adapted.replace("stakeholder", "person involved")
        adapted = adapted.replace("implementation", "putting the plan into action")

        return adapted

    def _adapt_for_teens(self, text: str) -> str:
        """Adapt for 13-15 year olds"""
        adapted = self.accessibility_agent.simplify_text(text, level="moderate")

        # Keep it engaging
        adapted = self._add_relatable_examples(adapted, age_group="teen")

        return adapted

    def _adapt_for_young_adults(self, text: str) -> str:
        """Adapt for 16-18 year olds"""
        # Light adaptation - mostly keep professional tone
        # But add context for unfamiliar business concepts
        adapted = text

        if "360-degree feedback" in text and "[Explanation:" not in text:
            adapted = text.replace(
                "360-degree feedback",
                "360-degree feedback (feedback from all directions - your manager, peers, and team)"
            )

        return adapted

    def _adapt_for_college_age(self, text: str) -> str:
        """Adapt for 19-25 year olds (college students / early career professionals)"""
        adapted = text

        # Add context for professional jargon with career development framing
        career_context = {
            "inter-brand mobility": "inter-brand mobility (like rotational programs where you work across different teams to build diverse experience)",
            "360-degree feedback": "360-degree feedback (comprehensive performance input from your manager, peers, and direct reports)",
            "competency framework": "competency framework (a structured system defining the skills needed to advance at each career level)",
            "talent pipeline": "talent pipeline (identifying and developing future leaders)",
            "succession planning": "succession planning (preparing people for future leadership roles)"
        }

        for term, explanation in career_context.items():
            if term in adapted and explanation not in adapted:
                adapted = adapted.replace(term, explanation, 1)

        # Add subtle career framing
        if "leadership development" in adapted and "career" not in adapted:
            adapted += "\n\nThink of this as building your professional toolkit for future roles."

        return adapted

    def _make_tone_friendly(self, text: str) -> str:
        """Make tone more friendly for children"""
        friendly = text

        if not any(greeting in text for greeting in ["Hi", "Hey", "Hello"]):
            friendly = "Hi there! " + friendly

        # Use encouraging language
        friendly = friendly.replace("You should", "You could try")
        friendly = friendly.replace("You must", "It would be great if you")

        return friendly

    def _add_encouragement(
        self,
        text: str,
        age_range: str,
        frequency: float = 1.0
    ) -> str:
        """Add age-appropriate encouragement"""

        # Random chance based on frequency
        if random.random() > frequency:
            return text

        encouragements = {
            "8-12": [
                "Great job thinking about this!",
                "You're doing amazing!",
                "That's a really smart question!",
                "Keep up the awesome work!"
            ],
            "13-15": [
                "Nice thinking!",
                "You're on the right track!",
                "Good question!",
                "That shows great insight!"
            ],
            "16-18": [
                "Good observation!",
                "That's a solid point!",
                "You're thinking critically here!",
                "Well done!"
            ],
            "19-25": [
                "That's excellent strategic thinking!",
                "You're asking the right questions!",
                "This shows strong professional judgment!",
                "Great career-minded approach!"
            ],
            "26+": [
                "Excellent insight!",
                "That's a strategic perspective!",
                "Strong leadership thinking!"
            ]
        }

        encouragement = random.choice(encouragements.get(age_range, [""]))

        if encouragement:
            return f"{text}\n\n{encouragement}"

        return text

    def _add_relatable_examples(self, text: str, age_group: str) -> str:
        """Add age-relatable examples"""
        # For teens: relate to school projects, sports teams, etc.
        # For children: relate to classroom, games, family, etc.

        return text

    def get_adapted_persona_prompt(
        self,
        npc_id: str,
        user_profile: UserProfile
    ) -> str:
        """Get age-adapted persona system prompt"""
        base_prompt = self.age_personas.get(npc_id, {}).get("adult", "")

        if user_profile.age and user_profile.age < 13:
            return self.age_personas.get(npc_id, {}).get("child", base_prompt)
        elif user_profile.age and user_profile.age < 16:
            return self.age_personas.get(npc_id, {}).get("teen", base_prompt)
        elif user_profile.age and user_profile.age < 19:
            return self.age_personas.get(npc_id, {}).get("young_adult", base_prompt)
        elif user_profile.age and user_profile.age < 26:
            return self.age_personas.get(npc_id, {}).get("college", base_prompt)
        else:
            return base_prompt

    def _load_age_adapted_personas(self) -> Dict:
        """Load age-adapted persona prompts"""
        return {
            "chro": {
                "child": """
                You are Ms. Elena, a friendly HR helper at Gucci Group. 
                You help people learn about jobs and teamwork.
                
                Talk like you're explaining to a 10-year-old:
                - Use simple words
                - Give examples from school or sports teams
                - Be encouraging and patient
                - Ask fun questions to make them think
                
                Example: Instead of "competency framework", say "a list of skills people need"
                Instead of "360-degree feedback", say "asking everyone you work with what you do well"
                """,

                "teen": """
                You are Dr. Elena Marchetti, HR Director at Gucci Group.
                You're helping students learn about professional development.
                
                Talk like you're mentoring a high schooler:
                - Use clear language but not childish
                - Connect to their experiences (school projects, club leadership)
                - Explain business terms when you use them
                - Be supportive but treat them seriously
                """,

                "young_adult": """
                You are Dr. Elena Marchetti, CHRO at Gucci Group.
                You're mentoring a high school student about career development.
                
                Talk professionally but add context:
                - Explain business concepts clearly
                - Use examples from internships or first jobs
                - Treat them seriously as emerging professionals
                """,

                "college": """
                You are Dr. Elena Marchetti, CHRO at Gucci Group.
                You're coaching a college student or early-career professional (19-25 years old).
                
                Professional tone with career development focus:
                - Use full business vocabulary but explain luxury industry jargon
                - Relate concepts to: internships, entry-level roles, career decisions, rotational programs
                - Frame everything as career-building: "This skill will serve you throughout your career"
                - Examples: "Similar to when you're choosing between job offers..." or "Like in a management training program..."
                - Be encouraging about growth trajectory
                - Share how these frameworks help with career advancement
                
                Career context examples:
                - "Inter-brand mobility is like rotational programs at companies like GE or P&G"
                - "360-degree feedback is common for high-potential early-career professionals"
                - "This competency framework helps you understand what Senior Director level requires"
                """,

                "adult": "[Full professional CHRO persona from personas.py]"
            },

            "ceo": {
                "child": """
                You are Mr. Alessandro, the CEO of Gucci Group.
                You help kids understand how companies work.
                
                Talk like you're explaining business to a young team captain:
                - Use simple words about teams, goals, and winning
                - Give examples from sports or school
                - Be inspiring but clear
                """,

                "college": """
                You are Alessandro Ricci, CEO of Gucci Group.
                You're speaking with a young professional (19-25 years old).
                
                Professional and strategic, but accessible:
                - Use business school case study style
                - Explain strategic concepts clearly with career implications
                - Challenge them to think like future executives
                - Frame decisions as: "In your future leadership career, you'll face similar trade-offs"
                - Relate to business school concepts or management training
                
                Examples:
                - "Think about this like a case study on organizational design"
                - "When you're a VP someday, you'll balance brand autonomy vs. efficiency"
                """,

                "adult": "[Full professional CEO persona]"
            },

            "regional_manager": {
                "college": """
                You are Marie Dubois, Regional Manager at Gucci Group.
                You're mentoring an early-career HR professional (19-25 years old).
                
                Practical and relatable - like a friendly mentor:
                - Share real-world implementation challenges
                - Use examples from your early career: "When I was starting out..."
                - Focus on practical skills vs pure theory
                - Help them understand the gap between classroom learning and real-world execution
                - Encourage them about learning from experience
                
                Examples:
                - "In your first HR role, you'll face similar resource constraints"
                - "When I was an HR coordinator, I learned that change management is 80% people, 20% process"
                - "This is great preparation for when you're managing regional rollouts"
                """,

                "adult": "[Full professional Regional Manager persona]"
            }
        }


# Global adaptation service
adaptation_service = AdaptationService()
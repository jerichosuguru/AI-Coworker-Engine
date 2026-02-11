"""
Accessibility Agent - Handles text-to-speech, speech-to-text, and adaptations
"""
from typing import Optional, Dict
import re
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from models.user_profile import UserProfile, AccessibilityNeeds


class AccessibilityAgent:
    """
    Handles accessibility transformations

    Features:
    - Text simplification for cognitive accessibility
    - Audio descriptions for visual impairments
    - Content adaptation for different age groups (8-12, 13-15, 16-18, 19-25, 26+)
    """

    def __init__(self):
        self.simplification_rules = self._load_simplification_rules()

    def adapt_message(
        self,
        message: str,
        user_profile: UserProfile
    ) -> Dict[str, any]:
        """
        Adapt message based on user accessibility needs

        Returns:
            {
                "text": adapted text,
                "audio_description": optional audio description,
                "simplified": whether text was simplified,
                "metadata": transformation metadata
            }
        """
        adapted_text = message
        transformations = []

        # 1. Simplify language if needed
        if user_profile.needs_simplified_language():
            adapted_text = self.simplify_text(
                adapted_text,
                level=user_profile.get_adapted_complexity()
            )
            transformations.append("simplified")

        # 2. Add audio descriptions if needed
        audio_description = None
        if user_profile.needs_audio_description():
            audio_description = self.generate_audio_description(adapted_text)
            transformations.append("audio_described")

        # 3. Format for screen readers
        if user_profile.accessibility.screen_reader_enabled:
            adapted_text = self.format_for_screen_reader(adapted_text)
            transformations.append("screen_reader_formatted")

        # 4. Add extra spacing for cognitive support
        if user_profile.accessibility.cognitive_support_needed:
            adapted_text = self.add_cognitive_support(adapted_text)
            transformations.append("cognitive_support")

        return {
            "text": adapted_text,
            "original": message,
            "audio_description": audio_description,
            "transformations": transformations,
            "metadata": {
                "complexity_level": user_profile.get_adapted_complexity(),
                "accessibility_features": transformations
            }
        }

    def simplify_text(self, text: str, level: str = "simple") -> str:
        """
        Simplify text based on complexity level

        Levels:
        - simple: 8-12 years old (elementary)
        - moderate: 13-15 years old (middle school)
        - advanced: 16+ years old (high school+)
        """
        simplified = text

        if level == "simple":
            # Replace complex words with simpler alternatives
            replacements = {
                "competency": "skill",
                "framework": "plan",
                "assessment": "test",
                "evaluate": "check",
                "implement": "start using",
                "cascade": "spread out",
                "facilitate": "help",
                "optimize": "make better",
                "collaborate": "work together",
                "strategic": "planned",
                "entrepreneurship": "starting new things",
                "behavioral indicators": "actions you can see"
            }

            for complex_word, simple_word in replacements.items():
                # Case-insensitive replacement
                pattern = re.compile(re.escape(complex_word), re.IGNORECASE)
                simplified = pattern.sub(simple_word, simplified)

            # Shorten sentences
            simplified = self._shorten_sentences(simplified)

        elif level == "moderate":
            # Less aggressive simplification
            replacements = {
                "competency framework": "skill plan",
                "behavioral indicators": "observable actions",
                "entrepreneurship": "innovation and new ideas"
            }

            for complex_phrase, simpler_phrase in replacements.items():
                pattern = re.compile(re.escape(complex_phrase), re.IGNORECASE)
                simplified = pattern.sub(simpler_phrase, simplified)

        return simplified

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
            return self._adapt_for_professionals(text)

    def _adapt_for_children(self, text: str) -> str:
        """Adapt for 8-12 year olds"""
        # Use simpler vocabulary
        adapted = self.simplify_text(text, level="simple")

        # Add friendly tone
        adapted = self._make_tone_friendly(adapted)

        # Remove complex business jargon
        adapted = adapted.replace("stakeholder", "person involved")
        adapted = adapted.replace("implementation", "putting the plan into action")

        return adapted

    def _adapt_for_teens(self, text: str) -> str:
        """Adapt for 13-15 year olds"""
        adapted = self.simplify_text(text, level="moderate")

        # Keep it engaging
        adapted = self._add_relatable_examples(adapted, age_group="teen")

        return adapted

    def _adapt_for_young_adults(self, text: str) -> str:
        """Adapt for 16-18 year olds"""
        # Light adaptation - mostly keep professional tone
        # But add context for unfamiliar business concepts
        adapted = text

        if "360-degree feedback" in adapted and "[Explanation:" not in adapted:
            adapted = adapted.replace(
                "360-degree feedback",
                "360-degree feedback (feedback from all directions - your manager, peers, and team)",
                1  # Only first occurrence
            )

        if "competency framework" in adapted and "skill" not in adapted:
            adapted = adapted.replace(
                "competency framework",
                "competency framework (a structured system for developing professional skills)",
                1
            )

        return adapted

    def _adapt_for_college_age(self, text: str) -> str:
        """Adapt for 19-25 year olds (college students / early career)"""
        adapted = text

        # Add context for industry-specific jargon
        jargon_explanations = {
            "inter-brand mobility": "inter-brand mobility (moving between different brand teams to gain diverse experience - like rotational programs)",
            "360-degree feedback": "360-degree feedback (comprehensive input from your manager, peers, and direct reports)",
            "competency framework": "competency framework (a structured system defining the skills and behaviors needed at each career level)",
            "cascade": "cascade (systematically roll out across the organization)",
            "stakeholder": "stakeholder (anyone impacted by or invested in the outcome)",
            "behavioral indicators": "behavioral indicators (specific, observable actions that demonstrate a skill)"
        }

        for term, explanation in jargon_explanations.items():
            if term in adapted and explanation not in adapted:
                # Only explain first occurrence
                adapted = adapted.replace(term, explanation, 1)

        # Add career development context
        adapted = self._add_career_context(adapted, age_group="college")

        return adapted

    def _adapt_for_professionals(self, text: str) -> str:
        """Adapt for 26+ year olds (experienced professionals)"""
        # Minimal adaptation - full professional content
        # Only add brief context for highly specialized luxury industry terms
        adapted = text

        # Add brief context only for luxury-specific jargon (if not already explained)
        luxury_terms = {
            "Maisons": "Maisons (luxury brand houses)",
            "atelier": "atelier (artisan workshop)",
            "savoir-faire": "savoir-faire (expert craftsmanship)",
            "métier": "métier (specialized craft or trade)"
        }

        for term, context in luxury_terms.items():
            if term in adapted and context not in adapted:
                # Only first occurrence
                adapted = adapted.replace(term, context, 1)

        return adapted

    def _make_tone_friendly(self, text: str) -> str:
        """Make tone more friendly for children"""
        friendly = text

        # Add friendly greetings if not present
        if not any(greeting in text for greeting in ["Hi", "Hey", "Hello"]):
            friendly = "Hi there! " + friendly

        # Use encouraging language
        friendly = friendly.replace("You should", "You could try")
        friendly = friendly.replace("You must", "It would be great if you")

        return friendly

    def _add_relatable_examples(self, text: str, age_group: str) -> str:
        """Add age-relatable examples"""
        # This would contain age-appropriate analogies
        # For teens: relate to school projects, sports teams, etc.
        # For children: relate to classroom, games, family, etc.

        return text

    def _add_career_context(self, text: str, age_group: str) -> str:
        """Add relatable career context for young professionals"""
        # Add subtle career development framing
        # For college age: relate to internships, first jobs, career decisions

        return text

    def _shorten_sentences(self, text: str) -> str:
        """Break long sentences into shorter ones"""
        sentences = text.split('. ')
        shortened = []

        for sentence in sentences:
            if len(sentence.split()) > 15:
                # Try to split on conjunctions
                parts = re.split(r',\s+(?:and|but|or|so)\s+', sentence)
                shortened.extend([p.strip() for p in parts])
            else:
                shortened.append(sentence.strip())

        return '. '.join(shortened) + ('.' if not text.endswith('.') else '')

    def generate_audio_description(self, text: str) -> str:
        """Generate audio-friendly description"""
        # Remove special formatting that doesn't read well
        audio_text = text

        # Spell out acronyms
        acronyms = {
            "HR": "H R",
            "CEO": "C E O",
            "CHRO": "C H R O",
            "360°": "360 degree",
            "OD": "O D",
            "KPI": "K P I",
            "ROI": "R O I"
        }

        for acronym, spoken in acronyms.items():
            audio_text = audio_text.replace(acronym, spoken)

        # Add pauses for better comprehension
        audio_text = audio_text.replace('. ', '... ')  # Longer pause at sentences
        audio_text = audio_text.replace(', ', ', ... ')  # Shorter pause at commas

        return audio_text

    def format_for_screen_reader(self, text: str) -> str:
        """Format text for screen reader compatibility"""
        # Add ARIA-friendly structure markers
        formatted = text

        # Mark lists (FIXED)
        has_bullet = '•' in formatted
        has_numbered_list = bool(re.search(r'\d+\.', formatted))

        if has_bullet or has_numbered_list:
            formatted = f"[List begins] {formatted} [List ends]"

        # Mark emphasis
        formatted = re.sub(r'\*\*(.*?)\*\*', r'[Important: \1]', formatted)

        # Mark questions
        formatted = re.sub(r'([^.!?]*\?)', r'[Question: \1]', formatted)

        return formatted

    def add_cognitive_support(self, text: str) -> str:
        """Add cognitive support features"""
        # Add section headers for structure
        supported = text

        # Add clear transitions
        transition_words = ['First', 'Second', 'Third', 'Next', 'Finally', 'However']
        for word in transition_words:
            pattern = f"\\b{word}\\b"
            supported = re.sub(pattern, f"\n\n**{word}:**", supported, count=1)

        # Add whitespace for breathing room
        supported = supported.replace('. ', '.\n\n')

        return supported

    def _load_simplification_rules(self) -> Dict:
        """Load language simplification rules"""
        return {
            "complex_to_simple": {
                # Business terms
                "competency": "skill",
                "framework": "plan",
                "assessment": "test",
                "implement": "start",
                "optimize": "improve",

                # HR terms
                "talent development": "helping people grow",
                "inter-brand mobility": "moving between teams",
                "stakeholder": "person involved",
                "360-degree feedback": "feedback from everyone you work with"
            }
        }


class SpeechService:
    """
    Text-to-Speech and Speech-to-Text service wrapper

    In production, integrate with:
    - Google Cloud Text-to-Speech
    - Amazon Polly
    - Azure Speech Services
    """

    def __init__(self):
        # Placeholder for actual TTS/STT service
        self.tts_enabled = False
        self.stt_enabled = False

    def text_to_speech(
        self,
        text: str,
        voice: str = "neutral",
        speed: float = 1.0
    ) -> bytes:
        """
        Convert text to speech audio

        Returns:
            Audio bytes (MP3/WAV format)
        """
        # Mock implementation
        # In production: call TTS API
        print(f"[TTS] Converting to speech: {text[:50]}...")
        return b""  # Return actual audio bytes

    def speech_to_text(self, audio_bytes: bytes) -> str:
        """
        Convert speech audio to text

        Returns:
            Transcribed text
        """
        # Mock implementation
        # In production: call STT API (Whisper, Google, etc.)
        print(f"[STT] Transcribing audio...")
        return ""  # Return transcribed text
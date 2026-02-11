"""
User Profile with Accessibility and Age Adaptation
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class AccessibilityNeeds(BaseModel):
    """User accessibility requirements"""

    # Visual
    visual_impairment: bool = False
    screen_reader_enabled: bool = False
    high_contrast_mode: bool = False
    font_size_multiplier: float = 1.0  # 1.0 = normal, 1.5 = 150%, etc.

    # Auditory
    hearing_impairment: bool = False
    captions_required: bool = False
    sign_language_preference: Optional[str] = None  # ASL, BSL, etc.

    # Motor/Physical
    motor_impairment: bool = False
    voice_input_preferred: bool = False
    keyboard_only_navigation: bool = False

    # Cognitive
    cognitive_support_needed: bool = False
    simple_language_preferred: bool = False
    extra_processing_time: bool = False

    # Speech
    text_to_speech_enabled: bool = False
    speech_to_text_enabled: bool = False
    speech_rate: float = 1.0  # 0.5 = slow, 1.0 = normal, 1.5 = fast
    voice_preference: str = "neutral"  # "male", "female", "neutral"


class AgeGroup(BaseModel):
    """Age-appropriate content adaptation"""

    age_range: Literal["8-12", "13-15", "16-18", "19-25", "26+"] = "26+"

    # Language complexity
    reading_level: Literal["elementary", "middle", "high", "college", "professional"] = "professional"
    vocabulary_complexity: Literal["simple", "moderate", "advanced"] = "advanced"

    # Content filters
    profanity_filter: bool = True
    sensitive_content_filter: bool = False

    # Interaction style
    gamification_enabled: bool = False
    encouragement_level: Literal["minimal", "moderate", "high"] = "minimal"
    explanation_depth: Literal["brief", "standard", "detailed"] = "standard"


class UserProfile(BaseModel):
    """Complete user profile for personalization"""

    user_id: str
    email: Optional[str] = None
    name: Optional[str] = None

    # Demographics (optional, for adaptation)
    age: Optional[int] = None
    age_group: AgeGroup = Field(default_factory=AgeGroup)

    # Accessibility
    accessibility: AccessibilityNeeds = Field(default_factory=AccessibilityNeeds)

    # Language & Localization
    preferred_language: str = "en"
    timezone: str = "UTC"

    # Learning preferences
    learning_style: Literal["visual", "auditory", "reading", "kinesthetic", "mixed"] = "mixed"
    pace_preference: Literal["slow", "moderate", "fast"] = "moderate"

    # Privacy settings
    data_retention_days: int = 30
    analytics_enabled: bool = True

    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    last_active: datetime = Field(default_factory=datetime.now)

    def get_adapted_complexity(self) -> str:
        """Get appropriate language complexity level"""
        if self.accessibility.simple_language_preferred:
            return "simple"

        if self.age and self.age < 13:
            return "simple"
        elif self.age and self.age < 16:
            return "moderate"
        else:
            return self.age_group.vocabulary_complexity

    def needs_audio_description(self) -> bool:
        """Check if user needs audio descriptions"""
        return (
            self.accessibility.visual_impairment or
            self.accessibility.text_to_speech_enabled or
            self.accessibility.screen_reader_enabled
        )

    def needs_simplified_language(self) -> bool:
        """Check if language simplification is needed"""
        return (
            self.accessibility.simple_language_preferred or
            self.accessibility.cognitive_support_needed or
            (self.age is not None and self.age < 16)
        )

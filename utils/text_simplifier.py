"""
Text simplification utilities for accessibility
"""
import re
from typing import Dict, List


class TextSimplifier:
    """
    Text simplification for different reading levels

    Levels:
    - simple (grade 3-5): Very basic vocabulary, short sentences
    - moderate (grade 6-8): Clear language, moderate complexity
    - advanced (grade 9+): Standard professional language
    """

    def __init__(self):
        self.simple_replacements = self._load_simple_replacements()
        self.moderate_replacements = self._load_moderate_replacements()

    def _load_simple_replacements(self) -> Dict[str, str]:
        """Load simple vocabulary replacements"""
        return {
            # Business terms
            "competency": "skill",
            "framework": "plan",
            "assessment": "test",
            "evaluate": "check",
            "implement": "start",
            "facilitate": "help",
            "optimize": "make better",
            "collaborate": "work together",
            "strategic": "planned",
            "utilize": "use",
            "leverage": "use",
            "synergy": "working well together",
            "bandwidth": "time and energy",
            "deliverable": "finished work",

            # HR terms
            "competency framework": "skill plan",
            "360-degree feedback": "asking everyone what you're good at",
            "behavioral indicators": "things you do",
            "talent development": "helping people get better",
            "stakeholder": "person involved",
            "inter-brand mobility": "moving between teams",
            "cascade": "spread out",

            # Complex verbs
            "prioritize": "decide what's most important",
            "demonstrate": "show",
            "maintain": "keep",
            "establish": "set up",
            "determine": "figure out",
            "acquire": "get",
            "comprehend": "understand",
            "commence": "start",
            "conclude": "end",
            "construct": "build",

            # Abstract nouns
            "methodology": "way of doing things",
            "paradigm": "pattern",
            "infrastructure": "basic setup",
            "criterion": "rule",
            "component": "part",
        }

    def _load_moderate_replacements(self) -> Dict[str, str]:
        """Load moderate complexity replacements"""
        return {
            "competency framework": "skill plan",
            "behavioral indicators": "observable actions",
            "360-degree feedback": "feedback from all directions",
            "inter-brand mobility": "moving between brand teams",
            "stakeholder": "people who are affected",
            "cascade": "roll out step by step",
            "entrepreneurship": "innovation and new ideas",
        }

    def simplify(self, text: str, level: str = "simple") -> str:
        """
        Simplify text based on reading level

        Args:
            text: Text to simplify
            level: Reading level (simple, moderate, advanced)

        Returns:
            Simplified text
        """
        if level == "advanced":
            return text

        simplified = text

        if level == "simple":
            # Apply simple replacements
            for complex_word, simple_word in self.simple_replacements.items():
                pattern = re.compile(re.escape(complex_word), re.IGNORECASE)
                simplified = pattern.sub(simple_word, simplified)

            # Shorten sentences
            simplified = self._shorten_sentences(simplified, max_words=12)

        elif level == "moderate":
            # Apply moderate replacements
            for complex_phrase, simpler_phrase in self.moderate_replacements.items():
                pattern = re.compile(re.escape(complex_phrase), re.IGNORECASE)
                simplified = pattern.sub(simpler_phrase, simplified)

            # Moderate sentence shortening
            simplified = self._shorten_sentences(simplified, max_words=20)

        return simplified

    def _shorten_sentences(self, text: str, max_words: int = 15) -> str:
        """
        Break long sentences into shorter ones

        Args:
            text: Text to process
            max_words: Maximum words per sentence

        Returns:
            Text with shorter sentences
        """
        sentences = text.split('. ')
        shortened = []

        for sentence in sentences:
            word_count = len(sentence.split())

            if word_count > max_words:
                # Try to split on conjunctions
                parts = re.split(r',\s+(?:and|but|or|so)\s+', sentence)
                for part in parts:
                    shortened.append(part.strip())
            else:
                shortened.append(sentence.strip())

        return '. '.join(shortened) + ('.' if not text.endswith('.') else '')

    def add_examples(self, text: str, age_group: str = "child") -> str:
        """
        Add age-appropriate examples

        Args:
            text: Original text
            age_group: child, teen, young_adult, adult

        Returns:
            Text with examples added
        """
        # This is a placeholder for more sophisticated example addition
        examples = {
            "child": {
                "competency": " (like being good at math or reading)",
                "framework": " (like a plan for your homework)",
                "leadership": " (like being a team captain)"
            },
            "teen": {
                "competency": " (like skills you need for a job)",
                "framework": " (like a study plan)",
                "leadership": " (like being student council president)"
            }
        }

        if age_group in examples:
            for term, example in examples[age_group].items():
                if term in text.lower() and example not in text:
                    text = text.replace(term, term + example, 1)

        return text


def simplify_text(text: str, level: str = "simple") -> str:
    """
    Convenience function to simplify text

    Args:
        text: Text to simplify
        level: Reading level (simple, moderate, advanced)

    Returns:
        Simplified text
    """
    simplifier = TextSimplifier()
    return simplifier.simplify(text, level)


def count_syllables(word: str) -> int:
    """
    Count syllables in a word (approximate)

    Args:
        word: Word to analyze

    Returns:
        Estimated syllable count
    """
    word = word.lower()

    # Remove trailing e
    if word.endswith('e'):
        word = word[:-1]

    # Count vowel groups
    vowels = 'aeiouy'
    syllable_count = 0
    previous_was_vowel = False

    for char in word:
        is_vowel = char in vowels
        if is_vowel and not previous_was_vowel:
            syllable_count += 1
        previous_was_vowel = is_vowel

    # Ensure at least one syllable
    return max(1, syllable_count)


def calculate_reading_level(text: str) -> str:
    """
    Calculate approximate reading level using Flesch-Kincaid

    Args:
        text: Text to analyze

    Returns:
        Reading level (elementary, middle, high, college, professional)
    """
    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return "elementary"

    # Count words and syllables
    total_words = 0
    total_syllables = 0

    for sentence in sentences:
        words = sentence.split()
        total_words += len(words)

        for word in words:
            # Clean word
            clean_word = re.sub(r'[^a-zA-Z]', '', word)
            if clean_word:
                total_syllables += count_syllables(clean_word)

    if total_words == 0:
        return "elementary"

    # Calculate averages
    avg_sentence_length = total_words / len(sentences)
    avg_syllables_per_word = total_syllables / total_words

    # Flesch-Kincaid Grade Level
    grade = 0.39 * avg_sentence_length + 11.8 * avg_syllables_per_word - 15.59

    # Map to categories
    if grade < 6:
        return "elementary"
    elif grade < 9:
        return "middle"
    elif grade < 13:
        return "high"
    elif grade < 16:
        return "college"
    else:
        return "professional"


def get_word_difficulty(word: str) -> str:
    """
    Estimate word difficulty

    Args:
        word: Word to analyze

    Returns:
        Difficulty level (easy, medium, hard)
    """
    syllables = count_syllables(word)
    length = len(word)

    if syllables <= 1 and length <= 4:
        return "easy"
    elif syllables <= 2 and length <= 8:
        return "medium"
    else:
        return "hard"


def split_into_chunks(text: str, max_chars: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into chunks for processing

    Args:
        text: Text to split
        max_chars: Maximum characters per chunk
        overlap: Number of overlapping characters between chunks

    Returns:
        List of text chunks
    """
    if len(text) <= max_chars:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + max_chars

        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence end
            next_period = text.find('. ', end - 100, end + 100)
            if next_period != -1:
                end = next_period + 2

        chunks.append(text[start:end])
        start = end - overlap

    return chunks
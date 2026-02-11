"""
Input validation utilities
"""
import re
from typing import Optional
import uuid


def validate_email(email: str) -> bool:
    """
    Validate email format

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_session_id(session_id: str) -> bool:
    """
    Validate session ID format (UUID)

    Args:
        session_id: Session ID to validate

    Returns:
        True if valid UUID format, False otherwise
    """
    try:
        uuid.UUID(session_id)
        return True
    except (ValueError, AttributeError):
        return False


def validate_user_input(text: str, max_length: int = 2000, min_length: int = 1) -> tuple[bool, Optional[str]]:
    """
    Validate user text input

    Args:
        text: User input text
        max_length: Maximum allowed length
        min_length: Minimum required length

    Returns:
        (is_valid, error_message)
    """
    if not text or not isinstance(text, str):
        return False, "Input must be a non-empty string"

    if len(text) < min_length:
        return False, f"Input must be at least {min_length} characters"

    if len(text) > max_length:
        return False, f"Input must be at most {max_length} characters"

    # Check for suspicious patterns
    suspicious_patterns = [
        r'<script',
        r'javascript:',
        r'onerror=',
        r'onclick=',
        r'<iframe',
    ]

    for pattern in suspicious_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return False, "Input contains potentially malicious content"

    return True, None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove path separators
    filename = filename.replace('/', '_').replace('\\', '_')

    # Remove any dots at the start (hidden files)
    filename = filename.lstrip('.')

    # Remove special characters except dash, underscore, and dot
    filename = re.sub(r'[^\w\-\.]', '_', filename)

    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:250] + ('.' + ext if ext else '')

    return filename or 'unnamed_file'


def validate_age(age: int) -> tuple[bool, Optional[str]]:
    """
    Validate age value

    Args:
        age: Age to validate

    Returns:
        (is_valid, error_message)
    """
    if not isinstance(age, int):
        return False, "Age must be an integer"

    if age < 8:
        return False, "Age must be at least 8"

    if age > 120:
        return False, "Age must be at most 120"

    return True, None


def validate_npc_id(npc_id: str) -> tuple[bool, Optional[str]]:
    """
    Validate NPC ID

    Args:
        npc_id: NPC identifier

    Returns:
        (is_valid, error_message)
    """
    valid_npcs = ['chro', 'ceo', 'regional_manager']

    if npc_id not in valid_npcs:
        return False, f"Invalid NPC ID. Must be one of: {', '.join(valid_npcs)}"

    return True, None


def validate_relationship_score(score: int) -> tuple[bool, Optional[str]]:
    """
    Validate relationship score range

    Args:
        score: Relationship score

    Returns:
        (is_valid, error_message)
    """
    if not isinstance(score, int):
        return False, "Score must be an integer"

    if score < -10 or score > 10:
        return False, "Score must be between -10 and 10"

    return True, None


def validate_module_number(module: int) -> tuple[bool, Optional[str]]:
    """
    Validate simulation module number

    Args:
        module: Module number

    Returns:
        (is_valid, error_message)
    """
    if not isinstance(module, int):
        return False, "Module must be an integer"

    if module < 1 or module > 3:
        return False, "Module must be 1, 2, or 3"

    return True, None


def sanitize_html(text: str) -> str:
    """
    Remove HTML tags from text

    Args:
        text: Text with potential HTML

    Returns:
        Text with HTML removed
    """
    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', '', text)

    # Decode HTML entities
    html_entities = {
        '&lt;': '<',
        '&gt;': '>',
        '&amp;': '&',
        '&quot;': '"',
        '&#39;': "'",
    }

    for entity, char in html_entities.items():
        clean = clean.replace(entity, char)

    return clean


def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format (basic)

    Args:
        phone: Phone number

    Returns:
        True if valid format, False otherwise
    """
    # Remove common formatting characters
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)

    # Check if remaining characters are digits
    if not cleaned.isdigit():
        return False

    # Check length (between 10 and 15 digits)
    return 10 <= len(cleaned) <= 15


def validate_url(url: str) -> bool:
    """
    Validate URL format

    Args:
        url: URL to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url, re.IGNORECASE))


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix
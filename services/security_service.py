"""
Security Service - Encryption, authentication, data protection
"""
import hashlib
import secrets
import re
from typing import Optional, Dict
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Import JWT
try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    print("⚠️  PyJWT not installed. Token auth disabled.")

# Import cryptography
try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("⚠️  cryptography not installed. Encryption disabled.")

from pydantic import BaseModel


class SecurityConfig:
    """Security configuration"""
    SECRET_KEY = SECRET_KEY
    ALGORITHM = ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES
    ENCRYPTION_KEY = Fernet.generate_key() if CRYPTO_AVAILABLE else b""

    # Rate limiting
    MAX_REQUESTS_PER_MINUTE = 60
    MAX_REQUESTS_PER_HOUR = 1000

    # Data retention
    SESSION_TTL_HOURS = 24
    CONVERSATION_RETENTION_DAYS = 30


class TokenData(BaseModel):
    """JWT token payload"""
    user_id: str
    session_id: str
    exp: datetime


class SecurityService:
    """
    Handles authentication, encryption, and security
    """

    def __init__(self):
        self.config = SecurityConfig()

        # Initialize cipher if crypto available
        if CRYPTO_AVAILABLE:
            self.cipher = Fernet(self.config.ENCRYPTION_KEY)
        else:
            self.cipher = None

        # Rate limiting storage (in production: use Redis)
        self.rate_limit_store: Dict[str, list] = {}

    def create_access_token(
        self,
        user_id: str,
        session_id: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token"""
        if not JWT_AVAILABLE:
            # Return simple token if JWT not available
            return f"{user_id}:{session_id}:{secrets.token_urlsafe(16)}"

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.config.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode = {
            "user_id": user_id,
            "session_id": session_id,
            "exp": expire.timestamp()
        }

        encoded_jwt = jwt.encode(
            to_encode,
            self.config.SECRET_KEY,
            algorithm=self.config.ALGORITHM
        )

        return encoded_jwt

    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode JWT token"""
        if not JWT_AVAILABLE:
            # Simple token verification
            parts = token.split(":")
            if len(parts) >= 3:
                return TokenData(
                    user_id=parts[0],
                    session_id=parts[1],
                    exp=datetime.utcnow() + timedelta(hours=1)
                )
            return None

        try:
            payload = jwt.decode(
                token,
                self.config.SECRET_KEY,
                algorithms=[self.config.ALGORITHM]
            )

            return TokenData(
                user_id=payload.get("user_id"),
                session_id=payload.get("session_id"),
                exp=datetime.fromtimestamp(payload.get("exp"))
            )
        except jwt.ExpiredSignatureError:
            print("Token expired")
            return None
        except jwt.JWTError as e:
            print(f"Invalid token: {e}")
            return None

    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data (PII, conversation history, etc.)"""
        if not self.cipher:
            return data  # Return unencrypted if crypto not available

        encrypted = self.cipher.encrypt(data.encode())
        return encrypted.decode()

    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if not self.cipher:
            return encrypted_data  # Return as-is if crypto not available

        decrypted = self.cipher.decrypt(encrypted_data.encode())
        return decrypted.decode()

    def hash_user_id(self, user_id: str) -> str:
        """Hash user ID for anonymization in analytics"""
        return hashlib.sha256(user_id.encode()).hexdigest()

    def check_rate_limit(
        self,
        user_id: str,
        endpoint: str,
        limit_per_minute: int = None
    ) -> bool:
        """
        Check if user has exceeded rate limit

        Returns:
            True if within limit, False if exceeded
        """
        if limit_per_minute is None:
            limit_per_minute = self.config.MAX_REQUESTS_PER_MINUTE

        key = f"{user_id}_{endpoint}"
        now = datetime.utcnow()

        # Initialize if new user
        if key not in self.rate_limit_store:
            self.rate_limit_store[key] = []

        # Clean old requests (older than 1 minute)
        self.rate_limit_store[key] = [
            req_time for req_time in self.rate_limit_store[key]
            if now - req_time < timedelta(minutes=1)
        ]

        # Check limit
        if len(self.rate_limit_store[key]) >= limit_per_minute:
            return False

        # Add current request
        self.rate_limit_store[key].append(now)

        return True

    def sanitize_user_input(self, user_input: str) -> str:
        """Sanitize user input to prevent injection attacks"""
        # Remove potentially dangerous characters
        sanitized = user_input

        # Remove script tags
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.DOTALL | re.IGNORECASE)

        # Remove SQL injection attempts
        sql_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'SELECT', '--', ';--']
        for keyword in sql_keywords:
            sanitized = sanitized.replace(keyword, '')

        # Limit length
        max_length = 2000
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]

        return sanitized.strip()

    def anonymize_for_logging(self, data: Dict) -> Dict:
        """Anonymize data for logging (GDPR compliance)"""
        anonymized = data.copy()

        # Hash PII fields
        pii_fields = ['email', 'name', 'user_id']
        for field in pii_fields:
            if field in anonymized:
                anonymized[field] = self.hash_user_id(str(anonymized[field]))

        # Remove sensitive content
        if 'conversation_history' in anonymized:
            anonymized['conversation_history'] = '[REDACTED]'

        return anonymized


# Global security service instance
security_service = SecurityService()
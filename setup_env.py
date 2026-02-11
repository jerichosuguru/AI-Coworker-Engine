"""
Generate .env file from template with secure defaults
"""
import secrets
from pathlib import Path


def generate_secret_key(length=32):
    """Generate secure random secret key"""
    return secrets.token_urlsafe(length)


def create_env_file():
    """Create .env file from .env.example"""

    env_example = Path(".env.example")
    env_file = Path(".env")

    if env_file.exists():
        response = input(".env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            return

    # Read template with UTF-8 encoding (FIX)
    if not env_example.exists():
        print("❌ .env.example not found!")
        return

    try:
        content = env_example.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        # Fallback to latin-1
        content = env_example.read_text(encoding='latin-1')

    # Replace placeholders
    content = content.replace(
        "your-secret-key-change-in-production",
        generate_secret_key(32)
    )

    # Write .env with UTF-8
    env_file.write_text(content, encoding='utf-8')

    print("✅ Created .env file")
    print("⚠️  Please add your ANTHROPIC_API_KEY to .env file")
    print(f"   Edit: {env_file.absolute()}")


if __name__ == "__main__":
    create_env_file()
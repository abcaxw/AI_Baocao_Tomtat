"""
config.py - Configuration file
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""

    # API Settings
    API_TITLE = "AI Document Summarizer"
    API_VERSION = "1.0.0"
    API_HOST = "0.0.0.0"
    API_PORT = 8000

    # AI Provider
    AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")  # "openai" or "claude"

    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

    # Models
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")

    # File Upload
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.xlsx', '.xls', '.txt']
    UPLOAD_DIR = "temp_uploads"

    # Processing
    MAX_TOKENS = 4000
    TEMPERATURE = 0.3
    MAX_DOCUMENT_LENGTH = 15000  # characters

    # Rate Limiting (optional)
    RATE_LIMIT = "100/hour"

    @classmethod
    def validate(cls):
        """Validate configuration"""
        if cls.AI_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI")

        if cls.AI_PROVIDER == "claude" and not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required when using Claude")

    @classmethod
    def get_info(cls):
        """Get config info (without sensitive data)"""
        return {
            "ai_provider": cls.AI_PROVIDER,
            "model": cls.OPENAI_MODEL if cls.AI_PROVIDER == "openai" else cls.CLAUDE_MODEL,
            "max_file_size_mb": cls.MAX_FILE_SIZE / (1024 * 1024),
            "allowed_extensions": cls.ALLOWED_EXTENSIONS
        }


if __name__ == "__main__":
    # Test configuration
    try:
        Config.validate()
        print("✅ Configuration is valid")
        print("\nConfig Info:")
        import json
        print(json.dumps(Config.get_info(), indent=2))
    except ValueError as e:
        print(f"❌ Configuration error: {e}")

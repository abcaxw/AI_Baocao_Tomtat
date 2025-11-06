"""
config.py - Configuration file with pricing
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
    API_PORT = 5000

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

    # OpenAI Pricing (USD per 1K tokens) - Updated Nov 2024
    OPENAI_PRICING = {
        "gpt-4o": {
            "input": 0.0025,   # $2.50 per 1M tokens
            "output": 0.01     # $10.00 per 1M tokens
        },
        "gpt-4o-mini": {
            "input": 0.00015,  # $0.150 per 1M tokens
            "output": 0.0006   # $0.600 per 1M tokens
        },
        "gpt-4-turbo": {
            "input": 0.01,     # $10.00 per 1M tokens
            "output": 0.03     # $30.00 per 1M tokens
        },
        "gpt-4": {
            "input": 0.03,     # $30.00 per 1M tokens
            "output": 0.06     # $60.00 per 1M tokens
        },
        "gpt-3.5-turbo": {
            "input": 0.0005,   # $0.50 per 1M tokens
            "output": 0.0015   # $1.50 per 1M tokens
        }
    }

    # Claude Pricing (USD per 1K tokens)
    CLAUDE_PRICING = {
        "claude-3-5-sonnet-20241022": {
            "input": 0.003,    # $3.00 per 1M tokens
            "output": 0.015    # $15.00 per 1M tokens
        },
        "claude-3-opus": {
            "input": 0.015,    # $15.00 per 1M tokens
            "output": 0.075    # $75.00 per 1M tokens
        },
        "claude-3-sonnet": {
            "input": 0.003,    # $3.00 per 1M tokens
            "output": 0.015    # $15.00 per 1M tokens
        },
        "claude-3-haiku": {
            "input": 0.00025,  # $0.25 per 1M tokens
            "output": 0.00125  # $1.25 per 1M tokens
        }
    }

    @classmethod
    def get_pricing(cls, model: str, provider: str = None) -> dict:
        """Get pricing for a specific model"""
        if provider is None:
            provider = cls.AI_PROVIDER

        if provider == "openai":
            return cls.OPENAI_PRICING.get(model, cls.OPENAI_PRICING["gpt-4o-mini"])
        elif provider == "claude":
            return cls.CLAUDE_PRICING.get(model, cls.CLAUDE_PRICING["claude-3-5-sonnet-20241022"])

        return {"input": 0, "output": 0}

    @classmethod
    def calculate_cost(cls, input_tokens: int, output_tokens: int, model: str, provider: str = None) -> dict:
        """Calculate cost based on token usage"""
        pricing = cls.get_pricing(model, provider)

        # Convert to cost per token (pricing is per 1K tokens)
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        total_cost = input_cost + output_cost

        return {
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(total_cost, 6),
            "currency": "USD"
        }

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
        model = cls.OPENAI_MODEL if cls.AI_PROVIDER == "openai" else cls.CLAUDE_MODEL
        pricing = cls.get_pricing(model)

        return {
            "ai_provider": cls.AI_PROVIDER,
            "model": model,
            "max_file_size_mb": cls.MAX_FILE_SIZE / (1024 * 1024),
            "allowed_extensions": cls.ALLOWED_EXTENSIONS,
            "pricing": {
                "input_per_1k_tokens": f"${pricing['input']:.6f}",
                "output_per_1k_tokens": f"${pricing['output']:.6f}",
                "currency": "USD"
            }
        }


if __name__ == "__main__":
    # Test configuration
    try:
        Config.validate()
        print("✅ Configuration is valid")
        print("\nConfig Info:")
        import json
        print(json.dumps(Config.get_info(), indent=2))

        # Test cost calculation
        print("\n--- Cost Calculation Example ---")
        test_cost = Config.calculate_cost(
            input_tokens=1000,
            output_tokens=500,
            model="gpt-4o-mini"
        )
        print(f"Input tokens: 1000")
        print(f"Output tokens: 500")
        print(f"Total cost: ${test_cost['total_cost']:.6f}")

    except ValueError as e:
        print(f"❌ Configuration error: {e}")
import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration from environment variables.

    Loads settings from .env file or environment.

    Attributes:
        GROQ_API_KEY: Groq API key for LLM inference.
        GROQ_LLM_MODELS: List of available Groq model IDs.
        DEFAULT_MODEL: Default model to use if none specified.
        TAVILY_API_KEY: Tavily API key for web search.
        LOG_LEVEL: Logging verbosity level (INFO, DEBUG, ERROR).
        APP_ENV: Environment name (development, production).
    """

    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_LLM_MODELS: list[str] = [
        "openai/gpt-oss-120b",
        "llama-3.1-8b-instant",
        "meta-llama/llama-4-scout-17b-16e-instruct",
    ]
    DEFAULT_MODEL: str = GROQ_LLM_MODELS[0]

    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    APP_ENV: str = os.getenv("APP_ENV", "development")


configs = Config()

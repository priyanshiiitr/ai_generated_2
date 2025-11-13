# config.py

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # To run, you need to create a .env file with OPENAI_API_KEY="your-key-here"
    # or set it as an environment variable.
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    OPENAI_API_KEY: str
    LLM_MODEL_NAME: str = "gpt-4o-mini"
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"

    # Scoring weights (must sum to 1.0 for the weighted average)
    # These can be externalized further if needed
    SCORING_WEIGHTS: dict = {
        'coverage': 0.35,
        'relevance': 0.25,
        'clarity': 0.1,
        'coherence': 0.1,
        'conciseness': 0.1,
        'grammar': 0.1
    }

settings = Settings()

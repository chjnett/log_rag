from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    # Database
    database_url: str = "sqlite:////data/sqlite/errors.db"

    # ChromaDB
    chroma_persist_directory: str = "/data/chroma"

    # RAG
    similarity_threshold: float = 0.8
    max_similar_cases: int = 3

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

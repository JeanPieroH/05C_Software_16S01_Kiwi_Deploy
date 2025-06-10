import os
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache

class Settings(BaseSettings):
    """
    Configuraciones del microservicio Quiz
    
    Estas configuraciones pueden cargarse desde variables de entorno
    o desde un archivo .env en la raíz del proyecto
    """
    APP_NAME: str = "kiwi-quiz-service"
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/quizdb")
    
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    DEFAULT_NUM_QUESTIONS: int = 5
    MAX_NUM_QUESTIONS: int = 15
    MIN_NUM_QUESTIONS: int = 2
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    """Crea y retorna una instancia de Settings usando caché"""
    return Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Voice AI Platform"
    VERSION: str = "1.0.0"
    
    # Database
    POSTGRES_USER: str = "voice_admin"
    POSTGRES_PASSWORD: str = "voice_password"
    POSTGRES_DB: str = "voice_system"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5433"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    # Security
    SECRET_KEY: str = "super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    WORKER_API_KEY: str = "internal-worker-secret-key"

    # LiveKit
    LIVEKIT_URL: str = "http://localhost:7885"
    LIVEKIT_API_KEY: str = "devkey"
    LIVEKIT_API_SECRET: str = "secret"

    # Memory System
    QDRANT_URL: str = "http://localhost:6333"

    # AI Providers
    DEEPGRAM_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    CARTESIA_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ELEVENLABS_API_KEY: str = ""
    
    STT_PROVIDER: str = "deepgram"
    LLM_PROVIDER: str = "groq"
    TTS_PROVIDER: str = "cartesia"

    # API Connection
    API_URL: str = "http://api:8000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

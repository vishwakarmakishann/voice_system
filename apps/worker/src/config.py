from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # LiveKit
    LIVEKIT_URL: str = "http://localhost:7885"
    LIVEKIT_API_KEY: str = "devkey"
    LIVEKIT_API_SECRET: str = "secret"

    # AI Providers
    DEEPGRAM_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    CARTESIA_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

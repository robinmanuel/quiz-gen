from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./quiz_gen.db"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    OPENAI_API_KEY: str | None = None
    # Google AI (Gemini) ? alternative provider for quiz question generation.
    # Uses Google's OpenAI-compatible endpoint via the same SDK client.
    GOOGLE_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    # When True, a failing or unavailable generation call falls back to template
    # questions instead of failing the request. Default to enabled for local dev
    # so the app remains usable without an API key.
    QUIZ_FALLBACK_ENABLED: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

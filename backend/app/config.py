from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./quiz_gen.db"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    # Google AI (Gemini) alternative provider for quiz question generation.
    GOOGLE_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-3.1-flash-lite"
    # When True, a failing or unavailable generation call falls back to template
    # questions instead of failing the request. Disabled by default so template
    # questions are not mistaken for AI-generated output.
    QUIZ_FALLBACK_ENABLED: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

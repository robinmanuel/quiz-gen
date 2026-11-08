from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./quiz_gen.db"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    # Google AI (Gemini) alternative provider for quiz question generation.
    GOOGLE_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-3.1-flash-lite"
    # When True, a failing or unavailable generation call falls back to template
    # questions instead of failing the request. Disabled by default so template
    # questions are not mistaken for AI-generated output.
    QUIZ_FALLBACK_ENABLED: bool = False
    # Rate limiting: max requests per time window for expensive endpoints.
    RATE_LIMIT_GENERATE: str = "10/minute"
    RATE_LIMIT_AUTH: str = "20/minute"
    # Comma-separated list of allowed CORS origins (use "*" for dev).
    CORS_ORIGINS: str = "*"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

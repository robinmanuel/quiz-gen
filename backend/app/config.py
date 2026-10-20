from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/quiz_gen"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    OPENAI_API_KEY: str
    # When True, a failing OpenAI call falls back to template questions instead
    # of failing the request. Handy in dev, turn it off in production.
    QUIZ_FALLBACK_ENABLED: bool = False

    class Config:
        env_file = ".env"


settings = Settings()

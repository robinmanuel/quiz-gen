import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app.database import engine, Base
from app.routers import auth, users, quizzes, health

# Create tables on startup (for dev; use Alembic migrations in production)
Base.metadata.create_all(bind=engine)

# Rate limiter — keyed by client IP; uses in-memory storage by default.
# Swap the storage_uri for Redis in production: "redis://localhost:6379/0"
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Quiz Generator API", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

logger = logging.getLogger("quizgen")

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()] or ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "A database error occurred"},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred"},
    )


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(quizzes.router)


@app.get("/")
def root():
    return {"message": "Quiz Generator API is running"}


import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import Base, get_db


def override_get_db(session_factory):
    def _get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()
    return _get_db


# Mock OpenAI to avoid needing a real API key
def mock_generate_quiz_questions(
    topic: str,
    num_questions: int = 8,
    quiz_type: str = "general",
    source_text: str | None = None,
):
    return [
        {
            "question_text": (
                f"What is {topic}?" if not source_text else "What detail appears in the source?"
            ),
            "options": ["A", "B", "C", "D"],
            "correct_option": "A",
            "explanation": "Test explanation",
        }
    ] * num_questions


@pytest.fixture(scope="function")
def client():
    # Fresh in-memory database per test (no autoincrement leakage)
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(test_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    # Create all tables
    Base.metadata.create_all(bind=test_engine)

    # Override dependencies
    app.dependency_overrides[get_db] = override_get_db(TestSessionLocal)

    # Patch quiz_service's reference to the OpenAI function
    import app.services.quiz_service as quiz_service
    quiz_service.generate_quiz_questions = mock_generate_quiz_questions

    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client

    # Clean up
    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.clear()

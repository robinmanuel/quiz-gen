import pytest
from pydantic import ValidationError

from app.schemas.quiz import QuizCreate


def test_quiz_creation_requires_an_explicit_type():
    with pytest.raises(ValidationError):
        QuizCreate.model_validate({"title": "Quiz", "topic": "Python"})

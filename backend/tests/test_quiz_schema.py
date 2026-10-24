import pytest
from pydantic import ValidationError

from app.schemas.quiz import QuizCreate, QuizManualCreate


def test_quiz_creation_requires_an_explicit_type():
    with pytest.raises(ValidationError):
        QuizCreate.model_validate({"title": "Quiz", "topic": "Python"})


def test_manual_quiz_requires_complete_questions():
    with pytest.raises(ValidationError):
        QuizManualCreate.model_validate(
            {
                "title": "Quiz",
                "topic": "Python",
                "quiz_type": "general",
                "questions": [
                    {
                        "question_text": "What is Python?",
                        "option_a": "A language",
                        "option_b": "A snake",
                        "option_c": "A tool",
                        "option_d": "A database",
                        "correct_option": "E",
                    }
                ],
            }
        )

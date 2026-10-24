from typing import Literal

from app.services.openai_service import generate_quiz_questions


QuizType = Literal["general", "niche"]


def build_quiz_data(
    topic: str,
    num_questions: int,
    quiz_type: QuizType,
    title: str | None = None,
) -> dict:
    questions = generate_quiz_questions(topic, num_questions, quiz_type)
    return {
        "title": title or f"Quiz about {topic}",
        "topic": topic,
        "quiz_type": quiz_type,
        "questions": questions,
    }

from app.services.openai_service import generate_quiz_questions


def build_quiz_data(topic: str, num_questions: int, title: str | None = None) -> dict:
    questions = generate_quiz_questions(topic, num_questions)
    return {
        "title": title or f"Quiz about {topic}",
        "topic": topic,
        "questions": questions,
    }

from app.services.openai_service import QuizType, generate_quiz_questions


def build_quiz_data(
    topic: str,
    num_questions: int,
    quiz_type: QuizType,
    title: str | None = None,
    source_text: str | None = None,
) -> dict:
    questions = generate_quiz_questions(topic, num_questions, quiz_type, source_text)
    return {
        "title": title or f"Quiz about {topic}",
        "topic": topic,
        "quiz_type": quiz_type,
        "questions": questions,
    }


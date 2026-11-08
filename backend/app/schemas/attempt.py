from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AttemptCreate(BaseModel):
    quiz_id: int
    answers: dict  # {question_id: "A" | "B" | "C" | "D"}


class QuestionReview(BaseModel):
    question_id: int
    correct_option: str
    explanation: str | None = None


class AttemptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quiz_id: int
    user_id: int
    score: int
    total_questions: int
    correct_answers: int
    submitted_at: datetime
    review: list[QuestionReview] = []


class UserAttemptOut(BaseModel):
    id: int
    quiz_id: int
    quiz_title: str
    quiz_topic: str
    score: int
    total_questions: int
    correct_answers: int
    submitted_at: datetime


class AttemptDetailOut(UserAttemptOut):
    review: list[QuestionReview] = []


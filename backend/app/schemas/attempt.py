from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AttemptCreate(BaseModel):
    quiz_id: int
    answers: dict  # {question_id: "A" | "B" | "C" | "D"}


class QuestionReview(BaseModel):
    question_id: int
    correct_option: str
    explanation: str | None = None


class AttemptOut(BaseModel):
    id: int
    quiz_id: int
    user_id: int
    score: int
    total_questions: int
    correct_answers: int
    submitted_at: datetime
    review: list["QuestionReview"] = []

    class Config:
        from_attributes = True

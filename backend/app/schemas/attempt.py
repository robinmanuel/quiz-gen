from pydantic import BaseModel
from typing import Optional


class AttemptCreate(BaseModel):
    quiz_id: int
    answers: dict  # {question_id: "A" | "B" | "C" | "D"}


class AttemptOut(BaseModel):
    id: int
    quiz_id: int
    user_id: int
    score: int
    total_questions: int
    correct_answers: int
    submitted_at: str

    class Config:
        from_attributes = True

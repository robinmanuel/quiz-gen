from typing import List, Literal

from pydantic import BaseModel

from app.schemas.question import QuestionOut


class QuizBase(BaseModel):
    title: str
    topic: str
    quiz_type: Literal["general", "niche"]


class QuizCreate(QuizBase):
    pass


class QuizOut(QuizBase):
    id: int
    owner_id: int
    questions: List[QuestionOut] = []

    class Config:
        from_attributes = True

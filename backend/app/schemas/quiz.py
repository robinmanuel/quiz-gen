from pydantic import BaseModel
from typing import List, Optional
from app.schemas.question import QuestionOut


class QuizBase(BaseModel):
    title: str
    topic: str


class QuizCreate(QuizBase):
    pass


class QuizOut(QuizBase):
    id: int
    owner_id: int
    questions: List[QuestionOut] = []

    class Config:
        from_attributes = True

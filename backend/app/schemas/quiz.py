from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel, Field

from app.schemas.question import QuestionCreate, QuestionOut


class QuizBase(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    topic: str = Field(min_length=1, max_length=120)
    quiz_type: Literal["general", "niche"]


class QuizCreate(QuizBase):
    source_text: str | None = Field(default=None, max_length=20000)


class QuizManualCreate(QuizBase):
    questions: List[QuestionCreate] = Field(min_length=1, max_length=50)


class QuizOut(QuizBase):
    id: int
    owner_id: int
    is_public: bool
    questions: List[QuestionOut] = []

    class Config:
        from_attributes = True


class QuizShareUpdate(BaseModel):
    is_public: bool


class SharedQuestionOut(BaseModel):
    id: int
    quiz_id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str


class SharedQuizOut(QuizBase):
    id: int
    quiz_type: Literal["general", "niche"]
    owner_username: str
    questions: List[SharedQuestionOut]


class PublicQuizOut(BaseModel):
    id: int
    title: str
    topic: str
    quiz_type: Literal["general", "niche"]
    owner_username: str
    question_count: int
    created_at: datetime


class LeaderboardEntry(BaseModel):
    rank: int
    username: str
    best_score: int
    correct_answers: int
    total_questions: int
    quiz_title: str
    quiz_topic: str
    submitted_at: datetime

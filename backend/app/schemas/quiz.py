from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.question import QuestionCreate, QuestionOut

QuizType = Literal["general", "niche", "beginner", "intermediate", "advanced"]


class QuizBase(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    topic: str = Field(min_length=1, max_length=120)
    quiz_type: QuizType


class QuizCreate(QuizBase):
    num_questions: int = Field(default=8, ge=1, le=20)
    source_text: str | None = Field(default=None, max_length=20000)


class QuizManualCreate(QuizBase):
    questions: List[QuestionCreate] = Field(min_length=1, max_length=50)


class QuizOut(QuizBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    is_public: bool
    questions: List[QuestionOut] = []


class QuizShareUpdate(BaseModel):
    is_public: bool


class QuizUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    topic: str | None = Field(default=None, min_length=1, max_length=120)
    quiz_type: QuizType | None = None
    is_public: bool | None = None


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
    quiz_type: QuizType
    owner_username: str
    questions: List[SharedQuestionOut]


class PublicQuizOut(BaseModel):
    id: int
    title: str
    topic: str
    quiz_type: QuizType
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


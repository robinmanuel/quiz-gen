from typing import Literal

from pydantic import BaseModel, Field


class QuestionBase(BaseModel):
    question_text: str = Field(min_length=1, max_length=2000)
    option_a: str = Field(min_length=1, max_length=500)
    option_b: str = Field(min_length=1, max_length=500)
    option_c: str = Field(min_length=1, max_length=500)
    option_d: str = Field(min_length=1, max_length=500)
    correct_option: Literal["A", "B", "C", "D"]
    explanation: str | None = Field(default=None, max_length=2000)


class QuestionCreate(QuestionBase):
    pass


class QuestionOut(QuestionBase):
    id: int
    quiz_id: int

    class Config:
        from_attributes = True

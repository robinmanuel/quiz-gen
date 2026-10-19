from pydantic import BaseModel
from typing import Optional


class QuestionBase(BaseModel):
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str  # 'A' | 'B' | 'C' | 'D'
    explanation: Optional[str] = None


class QuestionCreate(QuestionBase):
    pass


class QuestionOut(QuestionBase):
    id: int
    quiz_id: int

    class Config:
        from_attributes = True

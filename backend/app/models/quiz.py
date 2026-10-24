from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Text, false
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    quiz_type = Column(String(20), nullable=False, server_default="general")
    is_public = Column(Boolean, nullable=False, server_default=false())
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("Attempt", back_populates="quiz")

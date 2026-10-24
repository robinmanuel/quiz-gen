from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import SessionLocal, get_db
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.attempt import Attempt
from app.schemas.quiz import QuizCreate, QuizOut
from app.schemas.attempt import AttemptCreate, AttemptOut
from app.dependencies import get_current_user
from app.services.quiz_service import build_quiz_data
from app.models.user import User


router = APIRouter(prefix="/quizzes", tags=["quizzes"])

QUESTION_COUNT = 8


@router.post("/generate", response_model=QuizOut)
def generate_quiz(
    payload: QuizCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    quiz_data = build_quiz_data(
        payload.topic,
        QUESTION_COUNT,
        payload.quiz_type,
        payload.title,
    )

    db_quiz = Quiz(
        title=quiz_data["title"],
        topic=quiz_data["topic"],
        quiz_type=quiz_data["quiz_type"],
        owner_id=current_user.id,
    )
    db.add(db_quiz)
    db.flush()

    for q in quiz_data["questions"]:
        options = q.get("options", ["", "", "", ""])
        db_q = Question(
            quiz_id=db_quiz.id,
            question_text=q.get("question_text", ""),
            option_a=options[0] if len(options) > 0 else "",
            option_b=options[1] if len(options) > 1 else "",
            option_c=options[2] if len(options) > 2 else "",
            option_d=options[3] if len(options) > 3 else "",
            correct_option=q.get("correct_option", "A"),
            explanation=q.get("explanation", ""),
        )
        db.add(db_q)

    db.commit()
    db.refresh(db_quiz)
    return db_quiz


@router.get("/", response_model=List[QuizOut])
def list_quizzes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Quiz).filter(Quiz.owner_id == current_user.id).all()


@router.get("/{quiz_id}", response_model=QuizOut)
def get_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.owner_id == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz


@router.post("/{quiz_id}/submit", response_model=AttemptOut)
def submit_quiz(
    quiz_id: int,
    attempt: AttemptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()
    total = len(questions)
    correct = 0

    for q in questions:
        user_answer = attempt.answers.get(str(q.id))
        if user_answer and str(user_answer).upper() == q.correct_option.upper():
            correct += 1

    score = int((correct / total) * 100) if total else 0

    db_attempt = Attempt(
        quiz_id=quiz_id,
        user_id=current_user.id,
        score=score,
        total_questions=total,
        correct_answers=correct,
    )
    db.add(db_attempt)
    db.commit()
    db.refresh(db_attempt)
    return db_attempt

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from typing import List
from app.database import SessionLocal, get_db
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.attempt import Attempt
from app.schemas.quiz import (
    LeaderboardEntry,
    PublicQuizOut,
    QuizCreate,
    QuizOut,
    QuizShareUpdate,
    SharedQuizOut,
)
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


@router.get("/shared/{quiz_id}", response_model=SharedQuizOut)
def get_shared_quiz(quiz_id: int, db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(
        Quiz.id == quiz_id,
        Quiz.is_public.is_(True),
    ).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Public quiz not found")

    return SharedQuizOut(
        id=quiz.id,
        title=quiz.title,
        topic=quiz.topic,
        quiz_type=quiz.quiz_type,
        owner_username=quiz.owner.username,
        questions=[
            {
                "id": question.id,
                "quiz_id": question.quiz_id,
                "question_text": question.question_text,
                "option_a": question.option_a,
                "option_b": question.option_b,
                "option_c": question.option_c,
                "option_d": question.option_d,
            }
            for question in quiz.questions
        ],
    )


@router.get("/public", response_model=List[PublicQuizOut])
def list_public_quizzes(db: Session = Depends(get_db)):
    rows = (
        db.query(
            Quiz.id.label("id"),
            Quiz.title.label("title"),
            Quiz.topic.label("topic"),
            Quiz.quiz_type.label("quiz_type"),
            User.username.label("owner_username"),
            func.count(Question.id).label("question_count"),
            Quiz.created_at.label("created_at"),
        )
        .join(User, Quiz.owner_id == User.id)
        .outerjoin(Question, Question.quiz_id == Quiz.id)
        .filter(Quiz.is_public.is_(True))
        .group_by(Quiz.id, User.username)
        .order_by(Quiz.created_at.desc(), Quiz.id.desc())
        .limit(100)
        .all()
    )
    return [PublicQuizOut.model_validate(row._mapping) for row in rows]


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
def get_leaderboard(db: Session = Depends(get_db)):
    ranked_attempts = (
        db.query(
            Attempt.id.label("attempt_id"),
            func.row_number()
            .over(
                partition_by=Attempt.user_id,
                order_by=(Attempt.score.desc(), Attempt.submitted_at.asc(), Attempt.id.asc()),
            )
            .label("position"),
        )
        .join(Quiz, Attempt.quiz_id == Quiz.id)
        .filter(Quiz.is_public.is_(True))
        .subquery()
    )
    rows = (
        db.query(
            User.username.label("username"),
            Attempt.score.label("best_score"),
            Attempt.correct_answers.label("correct_answers"),
            Attempt.total_questions.label("total_questions"),
            Quiz.title.label("quiz_title"),
            Quiz.topic.label("quiz_topic"),
            Attempt.submitted_at.label("submitted_at"),
        )
        .join(ranked_attempts, ranked_attempts.c.attempt_id == Attempt.id)
        .join(User, Attempt.user_id == User.id)
        .join(Quiz, Attempt.quiz_id == Quiz.id)
        .filter(ranked_attempts.c.position == 1)
        .order_by(Attempt.score.desc(), Attempt.submitted_at.asc(), User.username.asc())
        .limit(100)
        .all()
    )
    return [
        LeaderboardEntry(rank=index, **row._mapping)
        for index, row in enumerate(rows, start=1)
    ]


@router.patch("/{quiz_id}/share", response_model=QuizOut)
def update_quiz_sharing(
    quiz_id: int,
    payload: QuizShareUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    quiz = db.query(Quiz).filter(
        Quiz.id == quiz_id,
        Quiz.owner_id == current_user.id,
    ).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    quiz.is_public = payload.is_public
    db.commit()
    db.refresh(quiz)
    return quiz


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
    quiz = db.query(Quiz).filter(
        Quiz.id == quiz_id,
        or_(Quiz.owner_id == current_user.id, Quiz.is_public.is_(True)),
    ).first()
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
    return AttemptOut(
        id=db_attempt.id,
        quiz_id=db_attempt.quiz_id,
        user_id=db_attempt.user_id,
        score=db_attempt.score,
        total_questions=db_attempt.total_questions,
        correct_answers=db_attempt.correct_answers,
        submitted_at=db_attempt.submitted_at,
        review=[
            {
                "question_id": question.id,
                "correct_option": question.correct_option,
                "explanation": question.explanation,
            }
            for question in questions
        ],
    )

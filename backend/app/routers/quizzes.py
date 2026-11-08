import asyncio
import csv
import io
import json
import time
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.attempt import Attempt
from app.schemas.quiz import (
    LeaderboardEntry,
    PublicQuizOut,
    QuizCreate,
    QuizManualCreate,
    QuizOut,
    QuizShareUpdate,
    QuizUpdate,
    SharedQuizOut,
)
from app.schemas.attempt import (
    AttemptCreate,
    AttemptDetailOut,
    AttemptOut,
    QuestionReview,
    UserAttemptOut,
)
from app.dependencies import get_current_user, get_current_admin
from app.services.quiz_service import build_quiz_data
from app.models.user import User
from app.config import settings

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/quizzes", tags=["quizzes"])

# ---------------------------------------------------------------------------
# Simple TTL in-memory cache for read-heavy public endpoints.
# Replace with Redis in production.
# ---------------------------------------------------------------------------
_cache: dict[str, tuple[object, float]] = {}
_CACHE_TTL = 30  # seconds


def _cache_get(key: str):
    entry = _cache.get(key)
    if entry and time.monotonic() - entry[1] < _CACHE_TTL:
        return entry[0]
    return None


def _cache_set(key: str, value: object) -> None:
    _cache[key] = (value, time.monotonic())


def _cache_invalidate_prefix(prefix: str) -> None:
    for key in list(_cache.keys()):
        if key.startswith(prefix):
            del _cache[key]


def _persist_quiz(
    db: Session,
    owner_id: int,
    title: str,
    topic: str,
    quiz_type: str,
    questions: list[dict],
) -> Quiz:
    quiz = Quiz(
        title=title,
        topic=topic,
        quiz_type=quiz_type,
        owner_id=owner_id,
    )
    db.add(quiz)
    db.flush()

    for question in questions:
        db.add(Question(quiz_id=quiz.id, **question))

    db.commit()
    db.refresh(quiz)
    return quiz


@router.post("/", response_model=QuizOut)
def create_quiz(
    payload: QuizManualCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _persist_quiz(
        db,
        current_user.id,
        payload.title,
        payload.topic,
        payload.quiz_type,
        [question.model_dump() for question in payload.questions],
    )


@router.post("/generate", response_model=QuizOut)
@limiter.limit(settings.RATE_LIMIT_GENERATE)
async def generate_quiz(
    request: Request,
    payload: QuizCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Run the synchronous (blocking) LLM call in a thread pool so the event
    # loop is not blocked while waiting for the AI provider response.
    loop = asyncio.get_event_loop()
    quiz_data = await loop.run_in_executor(
        None,
        lambda: build_quiz_data(
            payload.topic,
            payload.num_questions,
            payload.quiz_type,
            payload.title,
            payload.source_text.strip() if payload.source_text else None,
        ),
    )

    questions = [
        {
            "question_text": question["question_text"],
            "option_a": question["options"][0],
            "option_b": question["options"][1],
            "option_c": question["options"][2],
            "option_d": question["options"][3],
            "correct_option": question["correct_option"],
            "explanation": question.get("explanation"),
        }
        for question in quiz_data["questions"]
    ]
    return _persist_quiz(
        db,
        current_user.id,
        quiz_data["title"],
        quiz_data["topic"],
        quiz_data["quiz_type"],
        questions,
    )


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
def list_public_quizzes(
    search: str | None = Query(default=None, max_length=120),
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    cache_key = f"public_quizzes:{search or ''}:{limit}:{offset}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    query = (
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
    )
    if search and search.strip():
        pattern = f"%{search.strip()}%"
        query = query.filter(or_(Quiz.title.ilike(pattern), Quiz.topic.ilike(pattern)))

    rows = (
        query.group_by(Quiz.id, User.username)
        .order_by(Quiz.created_at.desc(), Quiz.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    result = [PublicQuizOut.model_validate(row._mapping) for row in rows]
    _cache_set(cache_key, result)
    return result


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
def get_leaderboard(db: Session = Depends(get_db)):
    cached = _cache_get("leaderboard_global")
    if cached is not None:
        return cached

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
    result = [
        LeaderboardEntry(rank=index, **row._mapping)
        for index, row in enumerate(rows, start=1)
    ]
    _cache_set("leaderboard_global", result)
    return result


@router.get("/attempts", response_model=List[UserAttemptOut])
def list_my_attempts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(
            Attempt.id.label("id"),
            Attempt.quiz_id.label("quiz_id"),
            Quiz.title.label("quiz_title"),
            Quiz.topic.label("quiz_topic"),
            Attempt.score.label("score"),
            Attempt.total_questions.label("total_questions"),
            Attempt.correct_answers.label("correct_answers"),
            Attempt.submitted_at.label("submitted_at"),
        )
        .join(Quiz, Attempt.quiz_id == Quiz.id)
        .filter(Attempt.user_id == current_user.id)
        .order_by(Attempt.submitted_at.desc(), Attempt.id.desc())
        .all()
    )
    return [UserAttemptOut.model_validate(row._mapping) for row in rows]


@router.get("/attempts/{attempt_id}", response_model=AttemptDetailOut)
def get_attempt_detail(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempt = (
        db.query(Attempt)
        .filter(Attempt.id == attempt_id, Attempt.user_id == current_user.id)
        .first()
    )
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    questions = db.query(Question).filter(Question.quiz_id == attempt.quiz_id).all()

    return AttemptDetailOut(
        id=attempt.id,
        quiz_id=attempt.quiz_id,
        quiz_title=attempt.quiz.title,
        quiz_topic=attempt.quiz.topic,
        score=attempt.score,
        total_questions=attempt.total_questions,
        correct_answers=attempt.correct_answers,
        submitted_at=attempt.submitted_at,
        review=[
            QuestionReview(
                question_id=q.id,
                correct_option=q.correct_option,
                explanation=q.explanation,
            )
            for q in questions
        ],
    )


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
    _cache_invalidate_prefix("public_quizzes")
    _cache_invalidate_prefix("leaderboard")
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


@router.get("/{quiz_id}/leaderboard", response_model=List[LeaderboardEntry])
def get_quiz_leaderboard(quiz_id: int, db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.is_public.is_(True)).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Public quiz not found")

    cache_key = f"leaderboard_quiz_{quiz_id}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

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
        .filter(Attempt.quiz_id == quiz_id)
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
    result = [
        LeaderboardEntry(rank=index, **row._mapping)
        for index, row in enumerate(rows, start=1)
    ]
    _cache_set(cache_key, result)
    return result


@router.get("/{quiz_id}/export")
def export_quiz(
    quiz_id: int,
    format: str = "json",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export a quiz owned by the current user as JSON or CSV (flashcard-ready)."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.owner_id == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    safe_title = "".join(c if c.isalnum() or c in "-_ " else "" for c in quiz.title).strip() or f"quiz_{quiz_id}"

    if format.lower() == "csv":
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["question_text", "option_a", "option_b", "option_c", "option_d", "correct_option", "explanation"])
        for q in quiz.questions:
            writer.writerow([
                q.question_text,
                q.option_a,
                q.option_b,
                q.option_c,
                q.option_d,
                q.correct_option,
                q.explanation or "",
            ])
        buf.seek(0)
        return StreamingResponse(
            iter([buf.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{safe_title}.csv"'},
        )

    if format.lower() != "json":
        raise HTTPException(status_code=400, detail="Unsupported format. Use 'json' or 'csv'.")

    export_data = {
        "title": quiz.title,
        "topic": quiz.topic,
        "quiz_type": quiz.quiz_type,
        "questions": [
            {
                "question_text": q.question_text,
                "option_a": q.option_a,
                "option_b": q.option_b,
                "option_c": q.option_c,
                "option_d": q.option_d,
                "correct_option": q.correct_option,
                "explanation": q.explanation,
            }
            for q in quiz.questions
        ],
    }
    return StreamingResponse(
        iter([json.dumps(export_data, indent=2)]),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{safe_title}.json"'},
    )


@router.delete("/{quiz_id}", status_code=204)
def delete_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.owner_id == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    db.delete(quiz)
    db.commit()
    _cache_invalidate_prefix("public_quizzes")
    _cache_invalidate_prefix("leaderboard")
    return None


@router.delete("/admin/{quiz_id}", status_code=204)
def admin_delete_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
):
    """Admin takedown endpoint — delete any quiz regardless of owner."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    db.delete(quiz)
    db.commit()
    _cache_invalidate_prefix("public_quizzes")
    _cache_invalidate_prefix("leaderboard")
    return None


@router.patch("/{quiz_id}", response_model=QuizOut)
def update_quiz(
    quiz_id: int,
    payload: QuizUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.owner_id == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    if payload.title is not None:
        quiz.title = payload.title
    if payload.topic is not None:
        quiz.topic = payload.topic
    if payload.quiz_type is not None:
        quiz.quiz_type = payload.quiz_type
    if payload.is_public is not None:
        quiz.is_public = payload.is_public

    db.commit()
    db.refresh(quiz)
    _cache_invalidate_prefix("public_quizzes")
    _cache_invalidate_prefix("leaderboard")
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
    _cache_invalidate_prefix("leaderboard")
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

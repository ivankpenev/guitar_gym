"""Progress tracking routes — sessions, stats, streaks."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.progress import ExerciseSession, ExerciseAttempt
from app.models.user import User
from app.routers.auth import get_current_user

router = APIRouter(prefix="/progress", tags=["progress"])


# --- Schemas ---

class StartSessionRequest(BaseModel):
    exercise_type: str
    difficulty: int = 1

class SessionResponse(BaseModel):
    id: UUID
    exercise_type: str
    difficulty: int
    started_at: datetime
    ended_at: datetime | None
    total_questions: int
    correct_answers: int

    model_config = {"from_attributes": True}

class RecordAttemptRequest(BaseModel):
    question_prompt: str
    correct_answer: str
    user_answer: str
    is_correct: bool

class StatsResponse(BaseModel):
    exercise_type: str
    total_sessions: int
    total_questions: int
    total_correct: int
    accuracy: float


# --- Routes ---

@router.post("/sessions", response_model=SessionResponse, status_code=201)
async def start_session(
    body: StartSessionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = ExerciseSession(
        user_id=current_user.id,
        exercise_type=body.exercise_type,
        difficulty=body.difficulty,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.post("/sessions/{session_id}/attempts", status_code=201)
async def record_attempt(
    session_id: UUID,
    body: RecordAttemptRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ExerciseSession).where(
            ExerciseSession.id == session_id,
            ExerciseSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    attempt = ExerciseAttempt(
        session_id=session_id,
        question_prompt=body.question_prompt,
        correct_answer=body.correct_answer,
        user_answer=body.user_answer,
        is_correct=body.is_correct,
    )
    db.add(attempt)

    session.total_questions += 1
    if body.is_correct:
        session.correct_answers += 1

    await db.commit()
    return {"status": "recorded"}


@router.post("/sessions/{session_id}/end", response_model=SessionResponse)
async def end_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ExerciseSession).where(
            ExerciseSession.id == session_id,
            ExerciseSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.ended_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(session)
    return session


@router.get("/stats", response_model=list[StatsResponse])
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(
            ExerciseSession.exercise_type,
            func.count(ExerciseSession.id).label("total_sessions"),
            func.sum(ExerciseSession.total_questions).label("total_questions"),
            func.sum(ExerciseSession.correct_answers).label("total_correct"),
        )
        .where(ExerciseSession.user_id == current_user.id)
        .group_by(ExerciseSession.exercise_type)
    )
    rows = result.all()
    return [
        StatsResponse(
            exercise_type=row.exercise_type,
            total_sessions=row.total_sessions,
            total_questions=row.total_questions or 0,
            total_correct=row.total_correct or 0,
            accuracy=(row.total_correct / row.total_questions * 100) if row.total_questions else 0.0,
        )
        for row in rows
    ]

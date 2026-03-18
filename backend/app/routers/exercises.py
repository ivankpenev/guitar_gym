"""Exercise routes — list exercises, generate questions, submit answers."""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.exercises import EXERCISE_REGISTRY, get_exercise

router = APIRouter(prefix="/exercises", tags=["exercises"])


# --- Schemas ---

class ExerciseInfo(BaseModel):
    exercise_type: str
    display_name: str
    description: str

class QuestionRequest(BaseModel):
    difficulty: int = 1

class QuestionResponse(BaseModel):
    exercise_type: str
    prompt: str
    choices: list[str]
    visual_data: dict[str, Any]
    # correct_answer intentionally omitted — stays server-side
    question_token: str  # opaque token to submit answer against

class AnswerRequest(BaseModel):
    question_token: str
    user_answer: str

class AnswerResponse(BaseModel):
    correct: bool
    correct_answer: str
    user_answer: str
    explanation: str


# In-memory question store (swap for Redis/DB in production)
_pending_questions: dict[str, Any] = {}
_token_counter = 0


def _make_token() -> str:
    global _token_counter
    _token_counter += 1
    return f"q-{_token_counter}"


# --- Routes ---

@router.get("/", response_model=list[ExerciseInfo])
async def list_exercises():
    return [
        ExerciseInfo(**ex.get_config())
        for ex in EXERCISE_REGISTRY.values()
    ]


@router.post("/{exercise_type}/question", response_model=QuestionResponse)
async def generate_question(exercise_type: str, body: QuestionRequest):
    try:
        exercise = get_exercise(exercise_type)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

    question = exercise.generate_question(difficulty=body.difficulty)
    token = _make_token()
    _pending_questions[token] = question

    return QuestionResponse(
        exercise_type=question.exercise_type,
        prompt=question.prompt,
        choices=question.choices,
        visual_data=question.visual_data,
        question_token=token,
    )


@router.post("/{exercise_type}/answer", response_model=AnswerResponse)
async def submit_answer(exercise_type: str, body: AnswerRequest):
    question = _pending_questions.pop(body.question_token, None)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found or already answered")

    try:
        exercise = get_exercise(exercise_type)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

    result = exercise.check_answer(question, body.user_answer)
    return AnswerResponse(
        correct=result.correct,
        correct_answer=result.correct_answer,
        user_answer=result.user_answer,
        explanation=result.explanation,
    )

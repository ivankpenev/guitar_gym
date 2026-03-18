"""Exercise registry — single place to register and discover exercises."""

from app.exercises.base import BaseExercise
from app.exercises.note_identification import NoteIdentificationExercise
from app.exercises.interval_training import IntervalTrainingExercise

# Register all exercise types here.
# To add a new exercise: import it and add an instance to this dict.
EXERCISE_REGISTRY: dict[str, BaseExercise] = {
    "note_identification": NoteIdentificationExercise(),
    "interval_training": IntervalTrainingExercise(),
}


def get_exercise(exercise_type: str) -> BaseExercise:
    """Look up an exercise by its type key."""
    exercise = EXERCISE_REGISTRY.get(exercise_type)
    if exercise is None:
        available = ", ".join(EXERCISE_REGISTRY.keys())
        raise KeyError(f"Unknown exercise type '{exercise_type}'. Available: {available}")
    return exercise

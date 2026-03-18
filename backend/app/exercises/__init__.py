"""Exercise plugin system.

Each exercise type is a subclass of BaseExercise. To add a new exercise:
1. Create a new file in this package
2. Subclass BaseExercise
3. Register it in EXERCISE_REGISTRY

The engine handles question generation, answer validation, and scoring.
"""

from app.exercises.base import BaseExercise, ExerciseQuestion, ExerciseResult
from app.exercises.registry import EXERCISE_REGISTRY, get_exercise

__all__ = [
    "BaseExercise",
    "ExerciseQuestion",
    "ExerciseResult",
    "EXERCISE_REGISTRY",
    "get_exercise",
]

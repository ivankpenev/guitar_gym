"""Base class for all exercises."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExerciseQuestion:
    """A single question presented to the user."""
    exercise_type: str
    prompt: str                       # Human-readable question text
    correct_answer: str               # The correct answer
    choices: list[str] = field(default_factory=list)  # Multiple choice options (empty = free input)
    visual_data: dict[str, Any] = field(default_factory=dict)  # Data for rendering (fret positions, etc.)
    metadata: dict[str, Any] = field(default_factory=dict)     # Extra info (difficulty, tags, etc.)


@dataclass
class ExerciseResult:
    """Result of a user's answer to a question."""
    correct: bool
    correct_answer: str
    user_answer: str
    explanation: str = ""


class BaseExercise(ABC):
    """Abstract base class for all exercise types.

    To create a new exercise:
    1. Subclass this class
    2. Implement generate_question() and check_answer()
    3. Register in the exercise registry
    """

    exercise_type: str = ""
    display_name: str = ""
    description: str = ""

    @abstractmethod
    def generate_question(self, difficulty: int = 1, **kwargs) -> ExerciseQuestion:
        """Generate a new random question.

        Args:
            difficulty: 1-5 scale controlling question complexity.
            **kwargs: Exercise-specific parameters.
        """
        ...

    @abstractmethod
    def check_answer(self, question: ExerciseQuestion, user_answer: str) -> ExerciseResult:
        """Validate the user's answer against the correct answer."""
        ...

    def get_config(self) -> dict[str, Any]:
        """Return exercise-specific configuration options."""
        return {
            "exercise_type": self.exercise_type,
            "display_name": self.display_name,
            "description": self.description,
        }

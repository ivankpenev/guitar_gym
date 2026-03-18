"""Note Identification Exercise.

Shows a position on the fretboard and asks the user to identify the note.
"""

import random

from app.exercises.base import BaseExercise, ExerciseQuestion, ExerciseResult
from app.services.music_theory import (
    CHROMATIC_SHARP,
    FretPosition,
    note_at_position,
)


class NoteIdentificationExercise(BaseExercise):
    exercise_type = "note_identification"
    display_name = "Note Identification"
    description = "Identify the note at a given fretboard position."

    # Difficulty controls which frets are included
    DIFFICULTY_FRET_RANGES = {
        1: (0, 4),    # Open position
        2: (0, 7),    # First half of neck
        3: (0, 12),   # Up to 12th fret
        4: (0, 17),   # Most of the neck
        5: (0, 24),   # Full fretboard
    }

    def generate_question(self, difficulty: int = 1, **kwargs) -> ExerciseQuestion:
        difficulty = max(1, min(5, difficulty))
        min_fret, max_fret = self.DIFFICULTY_FRET_RANGES[difficulty]

        string = random.randint(1, 6)
        fret = random.randint(min_fret, max_fret)
        position = FretPosition(string=string, fret=fret)
        note = note_at_position(position)

        # Build multiple choice options: correct + 3 random wrong notes
        wrong_choices = [n for n in CHROMATIC_SHARP if n != note.name]
        random.shuffle(wrong_choices)
        choices = [note.name] + wrong_choices[:3]
        random.shuffle(choices)

        return ExerciseQuestion(
            exercise_type=self.exercise_type,
            prompt=f"What note is at string {string}, fret {fret}?",
            correct_answer=note.name,
            choices=choices,
            visual_data={
                "string": string,
                "fret": fret,
                "highlight_positions": [{"string": string, "fret": fret}],
            },
            metadata={"difficulty": difficulty, "octave": note.octave},
        )

    def check_answer(self, question: ExerciseQuestion, user_answer: str) -> ExerciseResult:
        # Normalize: strip whitespace, handle enharmonic equivalents
        normalized = user_answer.strip()
        correct = normalized.upper() == question.correct_answer.upper()

        explanation = ""
        if not correct:
            s = question.visual_data["string"]
            f = question.visual_data["fret"]
            explanation = (
                f"The note at string {s}, fret {f} is {question.correct_answer}."
            )

        return ExerciseResult(
            correct=correct,
            correct_answer=question.correct_answer,
            user_answer=user_answer,
            explanation=explanation,
        )

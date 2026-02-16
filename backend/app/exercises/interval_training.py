"""Interval Training Exercise.

Shows two notes on the fretboard and asks the user to identify the interval.
"""

import random

from app.exercises.base import BaseExercise, ExerciseQuestion, ExerciseResult
from app.services.music_theory import (
    FretPosition,
    Interval,
    interval_between,
    note_at_position,
)


class IntervalTrainingExercise(BaseExercise):
    exercise_type = "interval_training"
    display_name = "Interval Training"
    description = "Identify the interval between two notes on the fretboard."

    # Difficulty controls which intervals can appear
    DIFFICULTY_INTERVALS = {
        1: [Interval.PERFECT_FOURTH, Interval.PERFECT_FIFTH, Interval.OCTAVE],
        2: [Interval.MAJOR_THIRD, Interval.PERFECT_FOURTH, Interval.PERFECT_FIFTH,
            Interval.OCTAVE],
        3: [Interval.MAJOR_SECOND, Interval.MAJOR_THIRD, Interval.PERFECT_FOURTH,
            Interval.PERFECT_FIFTH, Interval.MAJOR_SIXTH, Interval.OCTAVE],
        4: [i for i in Interval if i != Interval.UNISON],
        5: list(Interval),
    }

    DIFFICULTY_FRET_RANGES = {
        1: (0, 5),
        2: (0, 7),
        3: (0, 12),
        4: (0, 17),
        5: (0, 24),
    }

    def generate_question(self, difficulty: int = 1, **kwargs) -> ExerciseQuestion:
        difficulty = max(1, min(5, difficulty))
        allowed = self.DIFFICULTY_INTERVALS[difficulty]
        min_fret, max_fret = self.DIFFICULTY_FRET_RANGES[difficulty]

        # Pick a target interval
        target_interval = random.choice(allowed)

        # Generate first note randomly
        string1 = random.randint(1, 6)
        fret1 = random.randint(min_fret, max_fret)
        pos1 = FretPosition(string=string1, fret=fret1)
        note1 = note_at_position(pos1)

        # Find a second note that creates the target interval
        # Try positions on all strings
        candidates = []
        for s in range(1, 7):
            for f in range(min_fret, max_fret + 1):
                pos2 = FretPosition(string=s, fret=f)
                note2 = note_at_position(pos2)
                if interval_between(note1, note2) == target_interval:
                    if (s, f) != (string1, fret1):
                        candidates.append((s, f, pos2, note2))

        if not candidates:
            # Fallback: adjust fret on same string
            fret2 = fret1 + target_interval.semitones
            if fret2 > max_fret:
                fret2 = fret1 - target_interval.semitones
            pos2 = FretPosition(string=string1, fret=max(0, fret2))
            note2 = note_at_position(pos2)
            string2, fret2_final = string1, max(0, fret2)
        else:
            string2, fret2_final, pos2, note2 = random.choice(candidates)

        # Build choices from allowed intervals
        choice_intervals = list({i.display_name for i in allowed})
        if target_interval.display_name not in choice_intervals:
            choice_intervals.append(target_interval.display_name)
        random.shuffle(choice_intervals)
        # Limit to 4 choices
        if target_interval.display_name not in choice_intervals[:4]:
            choice_intervals = [target_interval.display_name] + choice_intervals[:3]
        else:
            choice_intervals = choice_intervals[:4]
        random.shuffle(choice_intervals)

        return ExerciseQuestion(
            exercise_type=self.exercise_type,
            prompt=f"What interval is between {note1.name} and {note2.name}?",
            correct_answer=target_interval.display_name,
            choices=choice_intervals,
            visual_data={
                "positions": [
                    {"string": string1, "fret": fret1, "label": note1.name},
                    {"string": string2, "fret": fret2_final, "label": note2.name},
                ],
            },
            metadata={
                "difficulty": difficulty,
                "interval_semitones": target_interval.semitones,
                "interval_abbreviation": target_interval.abbreviation,
            },
        )

    def check_answer(self, question: ExerciseQuestion, user_answer: str) -> ExerciseResult:
        normalized = user_answer.strip()
        correct = normalized.lower() == question.correct_answer.lower()

        # Also accept abbreviations
        if not correct:
            for interval in Interval:
                if interval.display_name == question.correct_answer:
                    if normalized.upper() == interval.abbreviation.upper():
                        correct = True
                    break

        explanation = ""
        if not correct:
            explanation = f"The correct interval is {question.correct_answer}."

        return ExerciseResult(
            correct=correct,
            correct_answer=question.correct_answer,
            user_answer=user_answer,
            explanation=explanation,
        )

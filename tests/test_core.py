import sys
import os
import random

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.music_theory import (
    FretPosition,
    Interval,
    note_at_position,
    interval_between,
    all_positions_for_note,
    note_name_from_midi,
    note_names_on_string,
    STANDARD_TUNING,
)
from app.exercises.note_identification import NoteIdentificationExercise
from app.exercises.interval_training import IntervalTrainingExercise
from app.exercises.registry import EXERCISE_REGISTRY, get_exercise


# ── Music Theory Tests ──

def test_open_strings():
    """Open strings in standard tuning should be E A D G B E."""
    expected = ["E", "A", "D", "G", "B", "E"]  # string 6 to 1
    for i, note_name in enumerate(expected):
        string_num = 6 - i  # 6, 5, 4, 3, 2, 1
        note = note_at_position(FretPosition(string=string_num, fret=0))
        assert note.name == note_name, f"String {string_num} open: expected {note_name}, got {note.name}"
    print("PASS: open strings")


def test_12th_fret_octave():
    """12th fret should be the same note name as the open string."""
    for string in range(1, 7):
        open_note = note_at_position(FretPosition(string=string, fret=0))
        fret12 = note_at_position(FretPosition(string=string, fret=12))
        assert open_note.name == fret12.name, f"String {string}: open={open_note.name}, fret12={fret12.name}"
        assert fret12.octave == open_note.octave + 1, f"String {string}: octave should increase by 1"
    print("PASS: 12th fret octave")


def test_chromatic_walk():
    """Walking up one string fret by fret should cycle through 12 notes."""
    notes = note_names_on_string(6, max_fret=12)  # Low E string
    # Fret 0=E, 1=F, 2=F#, 3=G, 4=G#, 5=A, 6=A#, 7=B, 8=C, 9=C#, 10=D, 11=D#, 12=E
    expected = ["E", "F", "F#", "G", "G#", "A", "A#", "B", "C", "C#", "D", "D#", "E"]
    assert notes == expected, f"Expected {expected}, got {notes}"
    print("PASS: chromatic walk on low E")


def test_well_known_positions():
    """Spot-check some well-known fretboard positions."""
    cases = [
        (6, 5, "A"),   # 5th fret low E = A
        (5, 5, "D"),   # 5th fret A = D
        (4, 5, "G"),   # 5th fret D = G
        (3, 5, "C"),   # 5th fret G = C
        (2, 5, "E"),   # 5th fret B = E
        (6, 3, "G"),   # 3rd fret low E = G
        (1, 1, "F"),   # 1st fret high E = F
        (5, 7, "E"),   # 7th fret A = E
    ]
    for string, fret, expected in cases:
        note = note_at_position(FretPosition(string=string, fret=fret))
        assert note.name == expected, f"String {string} fret {fret}: expected {expected}, got {note.name}"
    print("PASS: well-known positions")


def test_intervals():
    """Test interval calculation between notes."""
    # C to G = perfect fifth (7 semitones)
    c = note_at_position(FretPosition(string=5, fret=3))  # C on A string
    g = note_at_position(FretPosition(string=4, fret=5))  # G on D string
    assert c.name == "C"
    assert g.name == "G"
    assert interval_between(c, g) == Interval.PERFECT_FIFTH
    print("PASS: interval C to G = P5")

    # E to F = minor second (1 semitone)
    e = note_at_position(FretPosition(string=6, fret=0))
    f = note_at_position(FretPosition(string=6, fret=1))
    assert interval_between(e, f) == Interval.MINOR_SECOND
    print("PASS: interval E to F = m2")

    # Same note = unison
    e2 = note_at_position(FretPosition(string=6, fret=0))
    assert interval_between(e, e2) == Interval.UNISON
    print("PASS: interval unison")


def test_all_positions_for_note():
    """Should find multiple positions for any common note."""
    positions = all_positions_for_note("E", max_fret=12)
    assert len(positions) >= 6, f"Expected at least 6 E positions, got {len(positions)}"
    # Verify they're all actually E
    for pos in positions:
        assert note_at_position(pos).name == "E"
    print(f"PASS: found {len(positions)} positions for E (frets 0-12)")


# ── Exercise Tests ──

def test_note_id_exercise():
    """Note identification exercise generates valid questions and checks answers."""
    ex = NoteIdentificationExercise()

    for difficulty in range(1, 6):
        q = ex.generate_question(difficulty=difficulty)
        assert q.exercise_type == "note_identification"
        assert len(q.choices) == 4
        assert q.correct_answer in q.choices

        # Correct answer
        result = ex.check_answer(q, q.correct_answer)
        assert result.correct, f"Correct answer '{q.correct_answer}' marked wrong"

        # Wrong answer
        wrong = [c for c in q.choices if c != q.correct_answer][0]
        result = ex.check_answer(q, wrong)
        assert not result.correct

    print("PASS: note identification exercise (all difficulties)")


def test_interval_exercise():
    """Interval training exercise generates valid questions and checks answers."""
    ex = IntervalTrainingExercise()

    for difficulty in range(1, 6):
        q = ex.generate_question(difficulty=difficulty)
        assert q.exercise_type == "interval_training"
        assert len(q.choices) >= 2
        assert q.correct_answer in q.choices

        # Correct answer
        result = ex.check_answer(q, q.correct_answer)
        assert result.correct, f"Correct answer '{q.correct_answer}' marked wrong"

    print("PASS: interval training exercise (all difficulties)")


def test_interval_abbreviations():
    """Interval exercise should accept abbreviations like P5, m3."""
    ex = IntervalTrainingExercise()
    q = ex.generate_question(difficulty=1)

    # Find the abbreviation for the correct answer
    for interval in Interval:
        if interval.display_name == q.correct_answer:
            result = ex.check_answer(q, interval.abbreviation)
            assert result.correct, f"Abbreviation '{interval.abbreviation}' should be accepted"
            print(f"PASS: abbreviation '{interval.abbreviation}' accepted for '{q.correct_answer}'")
            break


def test_registry():
    """Exercise registry should have both exercises and reject unknowns."""
    assert "note_identification" in EXERCISE_REGISTRY
    assert "interval_training" in EXERCISE_REGISTRY

    ex = get_exercise("note_identification")
    assert ex.display_name == "Note Identification"

    try:
        get_exercise("nonexistent")
        assert False, "Should have raised KeyError"
    except KeyError:
        pass

    print("PASS: exercise registry")


# ── Run All ──

if __name__ == "__main__":
    random.seed(42)  # Reproducible

    tests = [
        test_open_strings,
        test_12th_fret_octave,
        test_chromatic_walk,
        test_well_known_positions,
        test_intervals,
        test_all_positions_for_note,
        test_note_id_exercise,
        test_interval_exercise,
        test_interval_abbreviations,
        test_registry,
    ]

    failed = 0
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"FAIL: {test.__name__}: {e}")
            failed += 1

    print(f"\n{'='*40}")
    print(f"{len(tests) - failed}/{len(tests)} tests passed")
    if failed:
        sys.exit(1)
    else:
        print("All tests passed!")

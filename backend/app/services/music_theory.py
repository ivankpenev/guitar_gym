"""Core music theory module for Guitar Gym.

Provides note names, fretboard mapping, and interval calculations.
This is the foundational knowledge layer that all exercises build on.
"""

from dataclasses import dataclass
from enum import Enum

# Chromatic scale using sharps (flats provided as aliases)
CHROMATIC_SHARP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
CHROMATIC_FLAT = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

# Standard guitar tuning (string 6 to string 1, low to high)
STANDARD_TUNING = ["E", "A", "D", "G", "B", "E"]
STANDARD_TUNING_MIDI = [40, 45, 50, 55, 59, 64]  # MIDI note numbers

NUM_FRETS = 24


class Interval(Enum):
    UNISON = (0, "Unison", "P1")
    MINOR_SECOND = (1, "Minor 2nd", "m2")
    MAJOR_SECOND = (2, "Major 2nd", "M2")
    MINOR_THIRD = (3, "Minor 3rd", "m3")
    MAJOR_THIRD = (4, "Major 3rd", "M3")
    PERFECT_FOURTH = (5, "Perfect 4th", "P4")
    TRITONE = (6, "Tritone", "TT")
    PERFECT_FIFTH = (7, "Perfect 5th", "P5")
    MINOR_SIXTH = (8, "Minor 6th", "m6")
    MAJOR_SIXTH = (9, "Major 6th", "M6")
    MINOR_SEVENTH = (10, "Minor 7th", "m7")
    MAJOR_SEVENTH = (11, "Major 7th", "M7")
    OCTAVE = (12, "Octave", "P8")

    def __init__(self, semitones: int, display_name: str, abbreviation: str):
        self.semitones = semitones
        self.display_name = display_name
        self.abbreviation = abbreviation


@dataclass(frozen=True)
class FretPosition:
    string: int  # 1-6, where 1 = high E, 6 = low E
    fret: int    # 0 = open, 1-24


@dataclass(frozen=True)
class Note:
    name: str       # e.g. "C", "F#"
    octave: int     # e.g. 4
    midi: int       # MIDI note number

    @property
    def full_name(self) -> str:
        return f"{self.name}{self.octave}"


def note_name_from_midi(midi: int, use_flats: bool = False) -> str:
    """Get the note name (without octave) from a MIDI number."""
    scale = CHROMATIC_FLAT if use_flats else CHROMATIC_SHARP
    return scale[midi % 12]


def octave_from_midi(midi: int) -> int:
    """Get the octave number from a MIDI number."""
    return (midi // 12) - 1


def note_at_position(position: FretPosition) -> Note:
    """Get the note at a specific fretboard position."""
    # Convert string number (1=high E) to index into tuning array (0=low E)
    string_index = 6 - position.string
    open_midi = STANDARD_TUNING_MIDI[string_index]
    midi = open_midi + position.fret
    return Note(
        name=note_name_from_midi(midi),
        octave=octave_from_midi(midi),
        midi=midi,
    )


def interval_between(note1: Note, note2: Note) -> Interval:
    """Calculate the interval between two notes (ascending from note1 to note2)."""
    semitones = (note2.midi - note1.midi) % 12
    for interval in Interval:
        if interval.semitones == semitones:
            return interval
    raise ValueError(f"Unknown interval: {semitones} semitones")


def all_positions_for_note(note_name: str, max_fret: int = NUM_FRETS) -> list[FretPosition]:
    """Find all fretboard positions where a given note name appears."""
    positions = []
    for string_num in range(1, 7):
        for fret in range(0, max_fret + 1):
            pos = FretPosition(string=string_num, fret=fret)
            if note_at_position(pos).name == note_name:
                positions.append(pos)
    return positions


def note_names_on_string(string: int, max_fret: int = NUM_FRETS) -> list[str]:
    """Get all note names on a given string up to max_fret."""
    return [
        note_at_position(FretPosition(string=string, fret=f)).name
        for f in range(0, max_fret + 1)
    ]

from dataclasses import dataclass
import z3

# Use midi value to represent
PitchMidiVarRef = z3.ArithRef
PitchMidiValue = int
# 0-11?
PitchClassVarRef = z3.ArithRef
PitchClassValue = int


@dataclass
class PitchVarRef:
    """
    A class representing a pitch variable.
    """

    midi: PitchMidiVarRef
    pitchClass: PitchClassVarRef


@dataclass
class ChordVarRef:
    """
    A class representing a chord variable.
    """

    pitches: list[PitchVarRef]

    def soprano(self):
        """Gets the soprano pitch variable."""
        return self.pitches[0]

    def alto(self):
        """Gets the alto pitch variable."""
        return self.pitches[1]

    def tenor(self):
        """Gets the tenor pitch variable."""
        return self.pitches[2]

    def bass(self):
        """Gets the bass pitch variable."""
        return self.pitches[3]


@dataclass
class StreamVarRef:
    """
    A class representing a note stream (voice/part) variable.
    """

    pitches: list[PitchVarRef]


def PitchVar(name: str) -> PitchVarRef:
    """Creates a pitch variable."""
    return PitchVarRef(z3.Int(f"{name}.pitchMidi"), z3.Int(f"{name}.pitchClass"))


def PitchMidiVar(name: str) -> PitchMidiVarRef:
    """Creates a pitch midi variable."""
    return z3.Int(f"{name}.pitchMidi")


def PitchClassVar(name: str) -> PitchClassVarRef:
    """Creates a pitch class variable."""
    return z3.Int(f"{name}.pitchClass")


def StreamVar(var_names: list[str]) -> StreamVarRef:
    """Creates a note stream (part/voice) variable."""
    return StreamVarRef([PitchVar(name) for name in var_names])


def ChordVar(var_names: list[str]) -> ChordVarRef:
    """Creates a chord variable."""
    return ChordVarRef([PitchVar(name) for name in var_names])

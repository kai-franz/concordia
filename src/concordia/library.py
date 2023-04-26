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
    midi: PitchMidiVarRef
    pitchClass: PitchClassVarRef


@dataclass
class ChordVarRef:
    pitches: list[PitchVarRef]

    def soprano(self):
        return self.pitches[0]

    def alto(self):
        return self.pitches[1]

    def tenor(self):
        return self.pitches[2]

    def bass(self):
        return self.pitches[3]


@dataclass
class StreamVarRef:
    pitches: list[PitchVarRef]


def PitchVar(name: str) -> PitchVarRef:
    return PitchVarRef(z3.Int(f"{name}.pitchMidi"), z3.Int(f"{name}.pitchClass"))


def PitchMidiVar(name: str) -> PitchMidiVarRef:
    return z3.Int(f"{name}.pitchMidi")


def PitchClassVar(name: str) -> PitchClassVarRef:
    return z3.Int(f"{name}.pitchClass")


def StreamVar(var_names: list[str]) -> StreamVarRef:
    return StreamVarRef([PitchVar(name) for name in var_names])


def ChordVar(var_names: list[str]) -> ChordVarRef:
    return ChordVarRef([PitchVar(name) for name in var_names])

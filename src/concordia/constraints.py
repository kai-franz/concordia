from music21.pitch import Pitch
from music21.roman import RomanNumeral
import itertools as it
from src.concordia.library import *
from music21 import *


# Constraints
def PitchMidiEq(pitch_var: PitchVarRef, name: str):
    return pitch_var.midi == Pitch(name).midi


def PitchClassEq(pitch_var: PitchVarRef, pitch: Pitch):
    return pitch_var.pitchClass == pitch.pitchClass


def PitchRange(pitch_var: PitchVarRef, low, high, soft=False):
    # TODO(yuchen): Add option for soft check (M2 off)
    return z3.And(Pitch(low).midi <= pitch_var.midi, pitch_var.midi <= Pitch(high).midi)


def SopranoRange(pitch_var: PitchVarRef):
    return PitchRange(pitch_var, "C4", "G5")


def AltoRange(pitch_var: PitchVarRef):
    return PitchRange(pitch_var, "G3", "D5")


def TenorRange(pitch_var: PitchVarRef):
    return PitchRange(pitch_var, "C3", "G4")


def BassRange(pitch_var: PitchVarRef):
    return PitchRange(pitch_var, "E2", "D4")


PITCH_CLASSES_COUNT = 12


def PitchClassMidiRelation(pitch_var: PitchVarRef):
    return pitch_var.midi % PITCH_CLASSES_COUNT == pitch_var.pitchClass


def ChordEqRoman(chord_var: ChordVarRef, key: str, roman: str):
    chord = RomanNumeral(roman, key)
    bass = PitchClassEq(chord_var.bass(), chord.bass())
    all_chord_tones = z3.And(
        [z3.Or([pitch_var.pitchClass == pitchClass for pitchClass in chord.pitchClasses]) for pitch_var in
         chord_var.pitches])
    complete_chord = z3.And(
        [z3.Or([pitch_var.pitchClass == pitchClass for pitch_var in chord_var.pitches]) for pitchClass in
         chord.pitchClasses])
    return z3.And(bass, all_chord_tones, complete_chord)


def NoVoiceOverlap(chord_var: ChordVarRef):
    s, a, t, b = chord_var.pitches
    return z3.And([b.midi <= t.midi, t.midi <= a.midi, a.midi <= s.midi])


def NoVoiceCrossing(first: ChordVarRef, second: ChordVarRef):
    s0, a0, t0, b0 = first.pitches
    s1, a1, t1, b1 = second.pitches
    return z3.And(b1.midi <= t0.midi,
                  b0.midi <= t1.midi, t1.midi <= a0.midi,
                  t0.midi <= a1.midi, a1.midi <= s0.midi,
                  a0.midi <= s1.midi
                  )


def VoicesWithinInterval(upper: StreamVarRef, lower: StreamVarRef, interv: str):
    interv = interval.Interval(interv)
    return z3.And([u.midi - l.midi <= interv.semitones for u, l in zip(upper.pitches, lower.pitches)])


def Abs(var):
    return z3.If(var >= 0, var, -var)


def NoParallelFifth(first: ChordVarRef, second: ChordVarRef):
    first_diffs = [Abs(a.midi - b.midi) % PITCH_CLASSES_COUNT for a, b in it.combinations(first.pitches, 2)]
    second_diffs = [Abs(a.midi - b.midi) for a, b in it.combinations(second.pitches, 2)]
    P5 = interval.Interval('P5')
    d5 = interval.Interval('d5')
    # TODO: bass ^2 to ^3 d5 -> P5 OK
    return z3.And([
        z3.Not(z3.And(
            z3.Or(f == d5.semitones, f == P5.semitones),
            s == P5.semitones))
        for f, s in zip(first_diffs, second_diffs)])


def NoParallelOctave(first: ChordVarRef, second: ChordVarRef):
    first_diffs = [Abs(a.midi - b.midi) for a, b in it.combinations(first.pitches, 2)]
    second_diffs = [Abs(a.midi - b.midi) for a, b in it.combinations(second.pitches, 2)]
    P8 = interval.Interval('P8')
    return z3.And([
        z3.Not(z3.And(
            f == P8.semitones,
            s == P8.semitones))
        for f, s in zip(first_diffs, second_diffs)])


def DoubleRoot(chord_var: ChordVarRef, key: str, roman: str):
    chord = RomanNumeral(roman, key)
    root = chord.root()
    use_root_conditions = [z3.If(PitchClassEq(pitch_var, root), 1, 0) for pitch_var in chord_var.pitches]
    return sum(use_root_conditions) == 2


def DoubleBass(chord_var: ChordVarRef, key: str, roman: str):
    chord = RomanNumeral(roman, key)
    bass = chord.bass()
    use_bass_conditions = [z3.If(PitchClassEq(pitch_var, bass), 1, 0) for pitch_var in chord_var.pitches]
    return sum(use_bass_conditions) == 2


def DoubleThird(chord_var: ChordVarRef, key: str, roman: str):
    chord = RomanNumeral(roman, key)
    third = chord.third
    use_third_conditions = [z3.If(PitchClassEq(pitch_var, third), 1, 0) for pitch_var in chord_var.pitches]
    return sum(use_third_conditions) == 2


def SmoothVoice(stream_var: StreamVarRef, interv: str):
    interv = interval.Interval(interv)
    return z3.And(
        [Abs(a.midi - b.midi) <= interv.semitones for a, b in zip(stream_var.pitches, stream_var.pitches[1:])])


def FourPartRange(part_streams):
    s, a, t, b = part_streams
    return z3.And(
        z3.And([SopranoRange(p) for p in s.pitches]),
        z3.And([AltoRange(p) for p in a.pitches]),
        z3.And([TenorRange(p) for p in t.pitches]),
        z3.And([BassRange(p) for p in b.pitches]),
    )

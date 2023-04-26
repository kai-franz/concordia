import z3
from music21 import *


class ConcordiaSolver:
    """
    Class that keeps track of harmony constraints + z3 solver.
    """

    def __init__(self, key, stream_vars):
        self.solver = z3.Solver()
        self.key = key
        self.stream_vars = stream_vars
        self.model = None

    def add(self, *args):
        self.solver.add(*args)

    def solve(self):
        self.solver.check()
        self.model = self.solver.model()

    def display_results(self):
        s_val, a_val, t_val, b_val = stream_vals = [stream.Voice() for _ in range(4)]

        key_sig = key.KeySignature(key.Key(self.key).sharps)
        for stream_val, stream_var in zip(stream_vals, self.stream_vars):
            stream_val.keySignature = key_sig
            for pitch_var in stream_var.pitches:
                n = note.Note(self.model[pitch_var.midi].as_long())
                stream_val.append(n)

        treble_part = stream.PartStaff([s_val, a_val])
        treble_part.clef = clef.TrebleClef()
        treble_part.keySignature = key_sig
        bass_part = stream.PartStaff([t_val, b_val])
        bass_part.clef = clef.BassClef()
        bass_part.keySignature = key_sig

        score = stream.Score([treble_part, bass_part])
        score.keySignature = key_sig
        score.show()
        score.show('midi')

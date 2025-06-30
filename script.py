from music21 import converter, note, chord, stream
from fractions import Fraction
import numpy as np

def parse_musicxml(file_path):
    score = converter.parse(file_path)
    result = []

    for element in score.recurse().notesAndRests:
        if isinstance(element, note.Note):
            transposed = element.transpose(-2)
            midi = transposed.pitch.midi
            duration = element.quarterLength
            result.append((midi, duration))

        elif isinstance(element, chord.Chord):
            transposed = element.transpose(-2)
            midi = transposed.root().midi
            duration = element.quarterLength
            result.append((midi, duration))

        elif isinstance(element, note.Rest):
            duration = element.quarterLength
            result.append(('rest', duration))

    return result

file_path = ""
data = parse_musicxml(file_path)

# data format: (MIDI or 'rest', Duration)

MIDI_data = []
duration_data = []

for d in data:
    MIDI_data.append(d[0] if d[0] != 'rest' else 0)
    if type(d[1]) == Fraction:
        duration_data.append(d[1].numerator / d[1].denominator)
    else:
        duration_data.append(d[1])

u = np.unique(duration_data)
key_to_dur = {}
dur_to_key = {}

for i in range(len(u)):
    key_to_dur[i] = u[i]
    dur_to_key[u[i]] = i

# create Markov transition matrix
P = np.array([[0 for _ in range(len(u))] for __ in range(len(u))])
P = P.astype(float)

transitions = {}
for i in range(len(duration_data)-1):
    d = duration_data[i]
    transitions[d] = transitions.get(d, []) + [duration_data[i+1]]

for dur, next in transitions.items():
    i = dur_to_key[dur]
    for z in next:
        j = dur_to_key[z]
        P[i][j] += 1
    P[i] = P[i] / len(next)

# Select n values
n = 128
samples = []
current_state = np.random.choice(len(P))  # Random start state

# Sample a sequence
for _ in range(n):
    samples.append(key_to_dur[current_state])
    current_state = np.random.choice(len(P), p=P[current_state])

ret = ""
for _ in samples:
    ret += str(_) + " "

print(ret)
"""Self-rendered audio: sound effects and a public-domain music bed.

We synthesise the music ourselves from public-domain scores, so we own the
recording outright and no Content ID claim can apply. PIECES is the library;
a Short picks one with `music.piece` in short.yaml, and DEFAULT is the fallback.

    python -m lib.audio sfx assets/sfx                     # write tick/pop/snip/chime .wav
    python -m lib.audio music out/music.wav 46 [piece-key] # write a 46 s music bed
"""
from __future__ import annotations

import re
import sys
import wave
from dataclasses import dataclass
from pathlib import Path

import numpy as np

SR = 44_100


def _write(path: Path, x: np.ndarray) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    x = np.clip(x, -1, 1)
    pcm = (x * 32767).astype(np.int16)
    stereo = np.stack([pcm, pcm], axis=1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(stereo.tobytes())
    return path


def _t(dur: float) -> np.ndarray:
    return np.arange(int(dur * SR)) / SR


def _env(n: int, attack: float = 0.004, decay: float = 6.0) -> np.ndarray:
    t = np.arange(n) / SR
    a = np.minimum(1.0, t / attack)
    return a * np.exp(-decay * t)


# --- sound effects ---------------------------------------------------------------
def tick() -> np.ndarray:
    t = _t(0.05)
    return 0.5 * np.sin(2 * np.pi * 1900 * t) * _env(len(t), 0.001, 90)


def pop() -> np.ndarray:
    t = _t(0.12)
    f = 950 * np.exp(-t * 14) + 380
    return 0.6 * np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(len(t), 0.002, 30)


def snip() -> np.ndarray:
    rng = np.random.default_rng(7)
    n = int(0.16 * SR)
    noise = np.diff(rng.standard_normal(n + 1))          # crude high-pass
    return 0.25 * noise * _env(n, 0.002, 28)


def chime() -> np.ndarray:
    t = _t(1.2)
    x = sum(a * np.sin(2 * np.pi * f * t) for f, a in ((1046.5, 0.5), (1568.0, 0.35), (2093.0, 0.15)))
    return 0.5 * x * _env(len(t), 0.003, 3.2)


def write_sfx(folder: str | Path) -> dict[str, Path]:
    folder = Path(folder)
    return {name: _write(folder / f"{name}.wav", fn()) for name, fn in
            (("tick", tick), ("pop", pop), ("snip", snip), ("chime", chime))}


# --- default bed: Bach BWV 846, bars 1-11 --------------------------------------
BWV846_BARS = [  # MIDI note numbers, the five notes of each bar's broken chord
    [60, 64, 67, 72, 76], [60, 62, 69, 74, 77], [59, 62, 67, 74, 77], [60, 64, 67, 72, 76],
    [60, 64, 69, 76, 81], [60, 62, 66, 69, 74], [59, 62, 67, 74, 79], [59, 60, 64, 67, 72],
    [57, 60, 64, 67, 72], [50, 57, 62, 66, 72], [55, 59, 62, 67, 71],
]


def _piano(freq: float, dur: float) -> np.ndarray:
    t = _t(dur)
    partials = ((1, 1.0), (2, 0.45), (3, 0.2), (4, 0.1))
    x = sum(a * np.sin(2 * np.pi * freq * k * t) for k, a in partials)
    return x * _env(len(t), 0.006, 2.2)


def _bwv846(duration: float, bpm: float) -> np.ndarray:
    sixteenth = 60.0 / bpm / 4
    out = np.zeros(int((duration + 3) * SR))
    pos, bar = 0.0, 0
    while pos < duration:
        n = BWV846_BARS[bar % len(BWV846_BARS)]
        for half in range(2):
            pattern = [n[0], n[1], n[2], n[3], n[4], n[2], n[3], n[4]]
            for i, m in enumerate(pattern):
                ring = (8 - i) * sixteenth if i < 2 else 3 * sixteenth   # bass notes sustain
                start = int((pos + (half * 8 + i) * sixteenth) * SR)
                note = _piano(440.0 * 2 ** ((m - 69) / 12), ring + 0.6) * (0.9 if i < 2 else 0.6)
                out[start:start + len(note)] += note[: len(out) - start]
        pos += 16 * sixteenth
        bar += 1
    return out


# --- scores -----------------------------------------------------------------------
# A voice is bars split by "|". A token is PITCH[+PITCH...][:beats] or r[:beats]; beats carry over
# from the previous token. Pitches are spelled as in the score, so a transcription reads against it.
# Ties aren't written: a tied note is struck once and followed by rests.
_SEMITONE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
_PITCH = re.compile(r"([A-G])([#b]?)(\d)")


def midi(pitch: str) -> int:
    m = _PITCH.fullmatch(pitch)
    if not m:
        raise ValueError(f"bad pitch {pitch!r}")
    return 12 * (int(m[3]) + 1) + _SEMITONE[m[1]] + {"": 0, "#": 1, "b": -1}[m[2]]


def parse_voice(text: str) -> list[list[tuple[tuple[int, ...], float]]]:
    """Text -> bars of (midi notes, beats); an empty note tuple is a rest."""
    bars, beats = [], None
    for bar_text in text.split("|"):
        tokens = bar_text.split()
        if not tokens:
            continue
        bar = []
        for token in tokens:
            name, _, dur = token.partition(":")
            beats = float(dur) if dur else beats
            bar.append(((() if name == "r" else tuple(midi(n) for n in name.split("+"))), beats))
        bars.append(bar)
    return bars


@dataclass(frozen=True)
class Piece:
    key: str
    credit: str                  # exactly what the YouTube description says after "Music: "
    mood: str
    bpm: float                   # score beats per minute
    bar: float = 4               # beats in a bar
    voices: tuple[tuple[float, str], ...] = ()   # (gain, notes); empty = has its own renderer


def _sequence(piece: Piece, duration: float) -> np.ndarray:
    """Play the voices together, looping from the top until `duration` is covered."""
    beat = 60.0 / piece.bpm
    out = np.zeros(int((duration + 3) * SR))
    parsed = [(gain, parse_voice(text)) for gain, text in piece.voices]
    bars = max(len(voice) for _, voice in parsed)
    for loop in range(int(duration / (bars * piece.bar * beat)) + 1):
        for gain, voice in parsed:
            pos = loop * bars * piece.bar
            for notes, beats in (event for bar in voice for event in bar):
                start = int(pos * beat * SR)
                for m in notes:
                    if start >= len(out):
                        continue
                    note = _piano(440.0 * 2 ** ((m - 69) / 12), beats * beat + 0.6) * gain
                    out[start:start + len(note)] += note[: len(out) - start]
                pos += beats
    return out


# Transcribed from the public-domain scores; LICENSES.csv names the edition checked against each.
_CANON = (                        # the opening of the one line all three violins play, 2 bars apart
    "F#5:1 E5 D5 C#5 | B4 A4 B4 C#5 | D5 C#5 B4 A4 | G4 F#4 G4 E4 | "
    "D4:0.5 F#4 A4 G4 F#4 D4 F#4 E4 | D4 B3 D4 A4 G4 B4 A4 G4 | "
    "F#4 D4 E4 C#5 D5 F#5 A5 A4 | B4 G4 A4 F#4 D4 D5 D5:0.75 C#5:0.25 | "
    "D5 C#5 D5 D4 C#4 A4 E4 F#4 D4 D5 C#5 B4 C#5 F#5 A5 B5 | "
    "G5 F#5 E5 G5 F#5 E5 D5 C#5 B4 A4 G4 F#4 E4 G4 F#4 E4 |"
)
_CANON_BARS = _CANON.split("|")
_G, _D = "r:1 B3+D4+F#4:2 |", "r:1 A3+C#4+F#4:2 |"
_ELISE_A = (                      # bars 1-7 of Für Elise, right hand then left, in sixteenths
    "E5:1 D#5 E5 B4 D5 C5 | A4:2 r:1 C4 E4 A4 | B4:2 r:1 E4 G#4 B4 | C5:2 r:1 E4 E5 D#5 | "
    "E5 D#5 E5 B4 D5 C5 | A4:2 r:1 C4 E4 A4 | B4:2 r:1 E4 C5 B4 |",
    "r:6 | A2:1 E3 A3 r:3 | E2:1 E3 G#3 r:3 | A2:1 E3 A3 r:3 | r:6 | A2:1 E3 A3 r:3 | E2:1 E3 G#3 r:3 |",
)
_MINUET_RH_1_4 = "D5:1 G4:0.5 A4 B4 C5 | D5:1 G4 G4 | E5:1 C5:0.5 D5 E5 F#5 | G5:1 G4 G4 | "
_MINUET_RH_5_6 = "C5:1 D5:0.5 C5 B4 A4 | B4:1 C5:0.5 B4 A4 G4 | "
_MINUET_LH_1_4 = "G3+B3+D4:2 A3:1 | B3:3 | C4:3 | B3:3 | "

PIECES = {p.key: p for p in (
    Piece("bwv846", "J. S. Bach, Prelude in C, BWV 846", "steady, unhurried", 70.0),
    Piece("pachelbel-canon", "Johann Pachelbel, Canon in D", "warm, building", 60.0, voices=(
        (0.9, "r:4 | r:4 | " + _CANON),
        (0.7, "r:4 | r:4 | r:4 | r:4 | " + "|".join(_CANON_BARS[:8]) + "|"),
        (0.7, "r:4 | r:4 | r:4 | r:4 | r:4 | r:4 | " + "|".join(_CANON_BARS[:6]) + "|"),
        (0.8, "D3:1 A2 B2 F#2 | G2 D2 G2 A2 | " * 6),
    )),
    Piece("gymnopedie-1", "Erik Satie, Gymnopédie No. 1", "slow, sparse", 72.0, bar=3, voices=(
        (0.9, "r:3 | r | r | r | r:1 F#5 A5 | G5 F#5 C#5 | B4 C#5 D5 | A4:3 | F#4 | r | r | r | "
              "r:1 F#5 A5 | G5 F#5 C#5 | B4 C#5 D5 | A4:3 | C#5 | F#5 | E4 | r | r |"),
        (0.5, f"{_G} {_D} " * 8 + f"{_D} {_G} r:1 G3+B3:2 | r:1 B3+D4+G4:2 | r:1 F3+A3+D4:2 |"),
        (0.7, "G2:3 | D2 | " * 8 + "F#2 | B1 | E2 | E2 | D2 |"),
    )),
    Piece("k545", "W. A. Mozart, Piano Sonata in C, K. 545", "bright, quick", 112.0, voices=(
        (0.9, "C5:2 E5:1 G5 | B4:1.5 C5:0.25 D5 C5:1 r | A5:2 G5:1 C6 | G5:1 F5:0.5 E5:0.25 F5 E5:1 r | "
              "A4:0.5 B4:0.25 C5 D5 E5 F5 G5 A5 G5 F5 E5 D5 C5 B4 A4 | "
              "G4:0.5 A4:0.25 B4 C5 D5 E5 F5 G5 F5 E5 D5 C5 B4 A4 G4 | "
              "F4:0.5 G4:0.25 A4 B4 C5 D5 E5 F5 E5 D5 C5 B4 A4 G4 F4 | "
              "E4:0.5 F4:0.25 G4 A4 B4 C5 D5 E5 D5 C5 B4 A4 G4 F4 E4 | "
              "D4:0.5 E4:0.25 F4 G4 A4 B4 C#5 D5 A4 B4 C#5 D5 E5 F5 G5 | "
              "A5 B5 C6 B5 A5 G5 F5 E5 F5 G5 A5 G5 F5 E5 D5 C5 | "
              "B4:0.5 G5 E5 C5 D5 G5 E5 C5 | D5:1 B4+D5+G5 G4 r |"),
        (0.55, "C4:0.5 G4 E4 G4 C4 G4 E4 G4 | D4 G4 F4 G4 C4 G4 E4 G4 | C4 A4 F4 A4 C4 G4 E4 G4 | "
               "B3 G4 D4 G4 C4 G4 E4 G4 | F4:1 r r F3+C4 | E3+C4 r r E3+C4 | D3+C4 r r D3+B3 | "
               "C3+C4 r r C3+E3 | F3+A3:4 | F3:1.5 G3:0.5 A3:1.5 F#3:0.5 | "
               "G2:0.25 B2 D3 G3 G2 C3 E3 G3 G2 B2 D3 G3 G2 C3 E3 G3 | G2:1 G3 G2 r |"),
    )),
    Piece("minuet-g", "Christian Petzold, Minuet in G, BWV Anh. 114", "light, dancing", 120.0, bar=3, voices=(
        (0.9, _MINUET_RH_1_4 + _MINUET_RH_5_6 + "F#4:1 G4:0.5 A4 B4 G4 | A4:3 | " +
              _MINUET_RH_1_4 + _MINUET_RH_5_6 + "A4:1 B4:0.5 A4 G4 F#4 | G4:3 |"),
        (0.6, _MINUET_LH_1_4 + "A3:3 | G3 | D4:1 B3 G3 | D4:1 D3:0.5 C4 B3 A3 | B3:2 A3:1 | G3 B3 G3 | "
              "C4:3 | B3:1 C4:0.5 B3 A3 G3 | A3:2 F#3:1 | G3:2 B3:1 | C4 D4 D3 | G3:2 G2:1 |"),
    )),
    Piece("fur-elise", "L. van Beethoven, Für Elise, WoO 59", "tense, mysterious", 252.0, bar=6, voices=(
        (0.9, "r:4 E5:1 D#5 | " + _ELISE_A[0] + " A4:4 E5:1 D#5 | " + _ELISE_A[0] + " A4:2 r:1 B4 C5 D5 | "
              "E5:3 G4:1 F5 E5 | D5:3 F4:1 E5 D5 | C5:3 E4:1 D5 C5 | B4:2 r:1 E4 E5 r | "
              "r E5 E6 r r D#5 | E5:2 r:1 D#5 E5 D#5 | E5 D#5 E5 B4 D5 C5 | "
              "A4:2 r:1 C4 E4 A4 | B4:2 r:1 E4 G#4 B4 | C5:2 r:1 E4 E5 D#5 | E5 D#5 E5 B4 D5 C5 | "
              "A4:2 r:1 C4 E4 A4 | B4:2 r:1 E4 C5 B4 | A4:6 |"),
        (0.6, "r:6 | " + _ELISE_A[1] + " A2:1 E3 A3 r:3 | " + _ELISE_A[1] + " A2:1 E3 A3 r:3 | "
              "C3:1 G3 C4 r:3 | G2:1 G3 B3 r:3 | A2:1 E3 A3 r:3 | E2:1 E3 E4 r r E4 | "
              "E5 r r D#5 E5 r | r D#5 E5 r r r | r:6 | "
              "A2:1 E3 A3 r:3 | E2:1 E3 G#3 r:3 | A2:1 E3 A3 r:3 | r:6 | "
              "A2:1 E3 A3 r:3 | E2:1 E3 G#3 r:3 | A2:1 E3 A3 r:3 |"),
    )),
)}
DEFAULT = "bwv846"


def piece(key: str | None) -> Piece:
    """The library entry for a Short's `music.piece`. No value means the default; a typo is an error."""
    key = key or DEFAULT
    if key not in PIECES:
        raise ValueError(f"unknown music piece {key!r}; choose from: {', '.join(PIECES)}")
    return PIECES[key]


def music(duration: float, key: str | None = None) -> np.ndarray:
    p = piece(key)
    out = _sequence(p, duration) if p.voices else _bwv846(duration, p.bpm)
    out = out[: int(duration * SR)]
    fade_in, fade_out = int(0.6 * SR), int(2.5 * SR)
    out[:fade_in] *= np.linspace(0, 1, fade_in)
    out[-fade_out:] *= np.linspace(1, 0, fade_out)
    return 0.6 * out / (np.abs(out).max() + 1e-9)


def write_music(path: str | Path, duration: float, key: str | None = None) -> Path:
    return _write(Path(path), music(duration, key))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "sfx":
        print(write_sfx(sys.argv[2]))
    elif cmd == "music":
        print(write_music(sys.argv[2], float(sys.argv[3]), *sys.argv[4:5]))
    else:
        raise SystemExit(__doc__)

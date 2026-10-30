"""Self-rendered audio: sound effects and a public-domain music bed.

We synthesise the music ourselves from a public-domain score, so we own the
recording outright and no Content ID claim can apply. The composition here is
J. S. Bach, Prelude in C major, BWV 846 (Well-Tempered Clavier I, 1722) -- the
first 11 bars, looped.

    python -m lib.audio sfx assets/sfx          # write tick/pop/snip/chime .wav
    python -m lib.audio music out/music.wav 46  # write a 46 s music bed
"""
from __future__ import annotations

import sys
import wave
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


# --- music bed: Bach BWV 846, bars 1-11 ----------------------------------------
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


def music(duration: float, bpm: float = 70.0) -> np.ndarray:
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
    out = out[: int(duration * SR)]
    fade_in, fade_out = int(0.6 * SR), int(2.5 * SR)
    out[:fade_in] *= np.linspace(0, 1, fade_in)
    out[-fade_out:] *= np.linspace(1, 0, fade_out)
    return 0.6 * out / (np.abs(out).max() + 1e-9)


def write_music(path: str | Path, duration: float) -> Path:
    return _write(Path(path), music(duration))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "sfx":
        print(write_sfx(sys.argv[2]))
    elif cmd == "music":
        print(write_music(sys.argv[2], float(sys.argv[3])))
    else:
        raise SystemExit(__doc__)

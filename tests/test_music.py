"""The music library: scores are well formed and every piece renders."""
import hashlib

import numpy as np
import pytest

from lib import audio

SCORED = [p for p in audio.PIECES.values() if p.voices]
KEYS = {"pachelbel-canon": "D", "gymnopedie-1": "D", "k545": "C", "minuet-g": "G", "fur-elise": "C"}
SCALE = {"C": {0, 2, 4, 5, 7, 9, 11}, "D": {2, 4, 6, 7, 9, 11, 1}, "G": {7, 9, 11, 0, 2, 4, 6}}
# Written accidentals outside the key signature, per piece: pc -> the transcription's only uses.
ACCIDENTALS = {"gymnopedie-1": {5}, "k545": {1, 6}, "minuet-g": set(), "fur-elise": {3, 8}, "pachelbel-canon": set()}


@pytest.mark.parametrize("p", SCORED, ids=lambda p: p.key)
def test_every_bar_adds_up_and_voices_match(p):
    lengths = set()
    for _, text in p.voices:
        bars = audio.parse_voice(text)
        lengths.add(len(bars))
        for i, bar in enumerate(bars, 1):
            assert sum(beats for _, beats in bar) == pytest.approx(p.bar), f"{p.key} bar {i}"
    assert len(lengths) == 1, f"{p.key} voices differ in length: {lengths}"


@pytest.mark.parametrize("p", SCORED, ids=lambda p: p.key)
def test_notes_stay_in_key(p):
    allowed = SCALE[KEYS[p.key]] | ACCIDENTALS[p.key]
    pcs = {m % 12 for _, text in p.voices for bar in audio.parse_voice(text) for notes, _ in bar for m in notes}
    assert pcs <= allowed


def test_pitch_names():
    assert audio.midi("C4") == 60 and audio.midi("A4") == 69 and audio.midi("F#5") == 78 and audio.midi("Bb3") == 58
    with pytest.raises(ValueError):
        audio.midi("H4")


def test_default_bed_is_unchanged():
    assert hashlib.sha256(audio.music(46.0).tobytes()).hexdigest() == (
        "a018ab7d7c8fc035ace06801d3fdefdf3e1f015cfc734409c915d10bae1a350e")


@pytest.mark.parametrize("key", list(audio.PIECES))
def test_every_piece_fills_the_duration(key):
    x = audio.music(50.0, key)
    assert len(x) == 50 * audio.SR
    assert 0.5 < np.abs(x).max() <= 0.6 + 1e-9
    seconds = [np.abs(x[i * audio.SR:(i + 1) * audio.SR]).max() for i in range(1, 47)]
    assert min(seconds) > 0.003, f"{key} goes silent mid-Short"


def test_unknown_piece_and_fallback():
    assert audio.piece(None).key == audio.DEFAULT == "bwv846"
    with pytest.raises(ValueError, match="unknown music piece"):
        audio.piece("Bach, free text")

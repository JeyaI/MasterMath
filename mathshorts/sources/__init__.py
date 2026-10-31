"""Source parsers. Each parser turns one raw book text into catalog records:

    {"id": "<source>-087", "source": "<source>", "number": 87, "title": "...",
     "section": "...", "text": "...", "solution": "..." | null,
     "has_figure": bool}

Register new parsers in PARSERS and the source itself in catalog/sources.yaml.
"""
from .dudeney import parse as parse_dudeney

PARSERS = {"dudeney": parse_dudeney}

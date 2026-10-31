"""Parser for H. E. Dudeney's books as plain text on Project Gutenberg.

Layout (confirmed for Amusements in Mathematics, #16713):

    MONEY PUZZLES.                      <- section heading: caps, own line, column 0

    1.--A POST-OFFICE PERPLEXITY.       <- puzzle heading: N.--TITLE.

    In every business of life ...       <- puzzle text until the next heading
    [Illustration]                      <- figure placeholder (sometimes ASCII art inside)

    SOLUTIONS.                          <- solutions section
    1.--A POST-OFFICE PERPLEXITY.       <- solution entry: title repeated, text below
                                           (a plain "1. ..." style is tolerated too)
    INDEX.                              <- back matter; ends the solutions

Robustness: puzzle and solution numbers must strictly increase, so a stray
"3." at the start of a prose line can't be mistaken for an entry. The table of
contents (indented, with page numbers) is ignored.

The real text has slips: see TYPOS and NO_PERIOD. One wrong number is costly, since
the increasing-number rule then rejects every heading up to it.
"""
from __future__ import annotations

import re

START = re.compile(r"\*\*\*\s*START OF (THE|THIS) PROJECT GUTENBERG", re.I)
END = re.compile(r"\*\*\*\s*END OF (THE|THIS) PROJECT GUTENBERG", re.I)
PUZZLE = re.compile(r"^(\d{1,3})\.\s*(?:--|—|–)\s*(.+?)\s*$")
SOLUTION = re.compile(r"^(\d{1,3})\.\s*(?:(?:--|—|–)\s*)?(.*)$")
# A few headings lost their period ("44--A CENSUS PUZZLE.", "180-- THE FOUR SONS."). Caps only,
# because solutions are full of prose like "96--namely" and move lists like "8--1, 7--2".
NO_PERIOD = re.compile(r"^(\d{1,3})--\s*([^a-z]*[A-Z][^a-z]*?)\s*$")
SECTION = re.compile(r"^[A-Z][A-Z ,'&\-]{3,}\.?$")        # column-0 caps line, no digits
SOLUTIONS_HEAD = re.compile(r"^SOLUTIONS\.?\s*$")
INDEX_HEAD = re.compile(r"^INDEX\.?\s*$")
# The placeholder often sits just above the heading, so a mention counts too; box art is ASCII.
FIGURE = re.compile(r"[Ii]llustration|^\s*\+-", re.M)
TYPOS = {"384.--THE CROSS TARGET.": "284.--THE CROSS TARGET."}   # misprinted number in #16713


def _heading(line: str):
    return PUZZLE.match(line) or NO_PERIOD.match(line)


def _strip_gutenberg(text: str) -> str:
    text = text.replace("\r\n", "\n")
    m = START.search(text)
    if m:
        text = text[text.index("\n", m.end()) + 1:]
    m = END.search(text)
    if m:
        text = text[: m.start()]
    for wrong, right in TYPOS.items():
        text = text.replace(wrong, right)
    return text


def _clean_title(t: str) -> str:
    t = t.strip().rstrip(".")
    if not t.isupper():
        return t
    return re.sub(r"(?<=\w)'S\b", "'s", t.title())    # str.title() gives "Wilson'S"


def _clean_body(lines: list[str]) -> str:
    body = "\n".join(lines).strip("\n")
    return re.sub(r"\n{3,}", "\n\n", body).strip()


def _is_section(lines: list[str], i: int) -> bool:
    """A section heading is a short column-0 caps line with blank lines (or edges) around it."""
    line = lines[i]
    if not (SECTION.match(line) and line == line.lstrip() and len(line) < 70):
        return False
    before = i == 0 or not lines[i - 1].strip()
    after = i + 1 >= len(lines) or not lines[i + 1].strip()
    return before and after


def _split_puzzles(lines: list[str]):
    """Yield (number, title, section, body_lines) in order, numbers strictly increasing."""
    section, cur, last = None, None, 0
    for i, line in enumerate(lines):
        m = _heading(line)
        if m and int(m.group(1)) > last and line == line.lstrip():
            if cur:
                yield cur
            last = int(m.group(1))
            cur = (last, _clean_title(m.group(2)), section, [])
            continue
        if _is_section(lines, i):
            section = _clean_title(line)
            if cur:
                yield cur
                cur = None
            continue
        if cur:
            cur[3].append(line)
    if cur:
        yield cur


def _split_solutions(lines: list[str], titles: dict[int, str]) -> dict[int, str]:
    # A book uses one style for solution entries: "N.--" or plain "N.". If the dashed form is
    # common, accept only that, so prose lines like "3. That is..." can't start an entry.
    dashed = sum(1 for l in lines if PUZZLE.match(l) and int(PUZZLE.match(l).group(1)) in titles)
    entry = _heading if dashed >= max(1, len(titles) // 2) else SOLUTION.match
    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())  # noqa: E731
    sols, cur, buf, last = {}, None, [], 0
    for i, line in enumerate(lines):
        if _is_section(lines, i):            # repeated section headings inside SOLUTIONS
            continue
        m = entry(line)
        if m and line == line.lstrip():
            n = int(m.group(1))
            if n > last and n in titles:
                if cur is not None:
                    sols[cur] = _clean_body(buf)
                cur, last, buf = n, n, []
                rest = m.group(2).strip()
                # Drop a repeated title (sometimes reworded: "A PUZZLE IN REVERSALS"), keep real text.
                if rest and not rest.isupper() and norm(rest) != norm(titles[n]):
                    buf.append(rest)
                continue
        if cur is not None:
            buf.append(line)
    if cur is not None:
        sols[cur] = _clean_body(buf)
    return sols


def parse(text: str, source_id: str) -> list[dict]:
    lines = _strip_gutenberg(text).split("\n")
    sol_at = next((i for i, l in enumerate(lines) if SOLUTIONS_HEAD.match(l)), len(lines))
    puzzles = list(_split_puzzles(lines[:sol_at]))
    numbers = {n for n, *_ in puzzles}
    tail = lines[sol_at + 1:]
    tail = tail[:next((i for i, l in enumerate(tail) if INDEX_HEAD.match(l)), len(tail))]
    sols = _split_solutions(tail, {n: t for n, t, *_ in puzzles})
    width = max(3, len(str(max(numbers, default=0))))
    records = []
    for n, title, section, body in puzzles:
        text_ = _clean_body(body)
        records.append({
            "id": f"{source_id}-{n:0{width}d}",
            "source": source_id,
            "number": n,
            "title": title,
            "section": section,
            "text": text_,
            "solution": sols.get(n),
            "has_figure": bool(FIGURE.search(text_)),
        })
    return records

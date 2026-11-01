"""ms - Master Math USA pipeline. See OPERATING.md for the playbook.

Catalog (rarely)
  ms sources list                     registered sources and how many puzzles each has
  ms sources add <source> [--file F]  scrape a source into catalog/ (F = a downloaded .txt)
                          [--rescore]  also re-run the heuristic on entries it scored
  ms show <catalog-id>                read one puzzle, its solution and annotation

Drafting (weekly session, mostly via Claude Code /draft-short)
  ms suggest [-n 5]                   ranked shortlist for the next Short, with reasons
  ms new <catalog-id> | --blank T     create shorts/NNNN-slug/ (status: drafting)
  ms verify <short>                   run verify.py
  ms preview <short> [--at 0:12]      full preview, or just the beat containing 0:12 (--open)
  ms compare <short>                  newest preview next to the previous one (--open)
  ms note <short> "0:12 text"         add a review note (open notes block approval)
  ms music [<key>]                    the music library and who used what; a key writes a WAV to hear
  ms approve <short>                  human sign-off -> built in tonight's batch

Nightly (automatic)
  ms batch [<short>] [--commit]       render + mix every approved Short -> out/ready/

Mornings
  ms inbox                            what's ready, failed, waiting
  ms reject <short> "note"            back to drafting with a note
  ms published <short> <url>          record the upload

Anytime
  ms status                           every Short by status
"""
from __future__ import annotations

import argparse
import re
import sys

from . import batch, catalog, paths, render, selector, yamlio
from .shorts import STATUSES, Short, StatusError, all_shorts, find, next_number, slugify, used_catalog_ids


def p(*a):
    print(*a, flush=True)


# --- catalog ----------------------------------------------------------------------------
def cmd_sources(a):
    if a.action == "list":
        counts = {}
        for r in catalog.records():
            counts[r["source"]] = counts.get(r["source"], 0) + 1
        for sid, s in catalog.sources().items():
            n = counts.get(sid, 0)
            p(f"{sid:<22} {n:>4} puzzles   {s['title']} ({s['year']})" + ("" if n else "   <- not scraped yet"))
        return
    if not a.source:
        sys.exit("ms: which source? see `ms sources list`")
    from pathlib import Path
    info = catalog.add_source(a.source, Path(a.file) if a.file else None, a.refresh, a.rescore)
    p(f"{a.source}: {info['puzzles']} puzzles ({info['with_solution']} with solutions, "
      f"{info['with_figure']} with figures) -> {info['path'].relative_to(paths.root())}")
    p(f"annotations: {info['annotations_added']} new heuristic entries in catalog/annotations.yaml"
      + (f", {info['annotations_rescored']} rescored" if a.rescore else ""))
    p(f"sections: {', '.join(info['sections'][:12])}{' …' if len(info['sections']) > 12 else ''}")
    p("next: skim the top of `ms suggest`, fix any scores that look wrong (scored_by: human), commit.")


def cmd_show(a):
    r = catalog.get(a.id)
    ann = catalog.annotations().get(a.id) or {}
    p(f"{r['id']}  ·  {r['title']}  ·  {r.get('section') or '-'}")
    p(f"annotation: visual {ann.get('visual_potential', '?')}/5, tags {list(ann.get('tags') or [])}, "
      f"scored_by {ann.get('scored_by', '-')}" + (", SKIP" if ann.get("skip") else ""))
    if r.get("has_figure"):
        p(f"figure: see {catalog.sources()[r['source']].get('html', 'the HTML edition')} (puzzle {r['number']})")
    p("\n" + r["text"] + "\n")
    p("SOLUTION\n" + (r.get("solution") or "(none in book)"))


# --- drafting ---------------------------------------------------------------------------
def _recent() -> list[dict]:
    out = []
    for s in sorted(all_shorts(), key=lambda s: s.number, reverse=True):
        d = s.data()
        out.append({"tags": list(d.get("tags") or []), "source": (d.get("source") or {}).get("kind")})
    return out


def cmd_suggest(a):
    recs = catalog.records()
    if not recs:
        sys.exit("ms: the catalog is empty. Run `ms sources add dudeney-amusements` first.")
    cfg = yamlio.load(paths.config() / "selector.yaml")
    picks = selector.rank(recs, catalog.annotations(), used_catalog_ids(), _recent(), cfg, n=a.n)
    if not picks:
        sys.exit("ms: nothing qualifies. Lower min_visual in config/selector.yaml or add a source.")
    for i, c in enumerate(picks, 1):
        r = c.record
        first = re.sub(r"\s+", " ", r["text"])[:150]
        p(f"{i}. {r['id']}  {r['title']}   [score {c.score}]")
        p(f"   {r.get('section') or '-'} · {'; '.join(c.reasons)}")
        p(f"   {first}…\n")
    p("read one: ms show <id>    start one: /draft-short <id> in Claude Code (or ms new <id>)")


def _new_short(record: dict | None, title: str | None):
    from ruamel.yaml.comments import CommentedMap
    from ruamel.yaml.scalarstring import LiteralScalarString as L

    title = record["title"] if record else title
    num = next_number()
    folder = paths.shorts() / f"{num}-{slugify(title)}"
    folder.mkdir(parents=True)
    ann = (catalog.annotations().get(record["id"]) or {}) if record else {}
    src = catalog.sources().get(record["source"], {}) if record else {}

    d = CommentedMap()
    d["id"] = num
    d["title"] = title
    d["status"] = "drafting"
    d["catalog_id"] = record["id"] if record else None
    d["tags"] = list(ann.get("tags") or [])
    d["source"] = CommentedMap(
        kind=record["source"] if record else "original",
        credit=(f"After {src.get('author', '')}, {src.get('title', '')} ({src.get('year', '')}), no. {record['number']}"
                if record else "Original problem"),
        license=src.get("license", "original work"),
    )
    if record:
        d["puzzle"] = CommentedMap(text=L(record["text"] + "\n"), solution=L((record.get("solution") or "(none)") + "\n"))
    d["level1"] = CommentedMap(statement="TODO", answer="TODO", insight="TODO")
    d["level2"] = CommentedMap(statement="TODO: same trick, one step further; solvable without a calculator",
                               answer="TODO", accept=[], why="TODO")
    d["captions"] = []
    audio = render._audio()
    d["music"] = CommentedMap(piece=audio.DEFAULT,
                              license="public-domain composition; recording synthesised by lib/audio.py")
    d["youtube"] = CommentedMap(title="TODO", description=L(f"TODO\nMusic: {audio.PIECES[audio.DEFAULT].credit}.\n"),
                                tags=["math puzzle", "puzzle"],
                                video_id=None, url=None, published_at=None)
    yamlio.write_atomic(folder / "short.yaml",
                        "# One Short. Change `status` only through ms commands (see OPERATING.md).\n" + yamlio.dump_str(d))
    (folder / "verify.py").write_text(
        '"""Check every claim the video makes, in code. `ms approve` refuses until this passes."""\n\n'
        "def main() -> None:\n    raise SystemExit(\"TODO: write the checks for this Short\")\n\n\n"
        'if __name__ == "__main__":\n    main()\n')
    (folder / "scene.py").write_text(SCENE_STUB.format(title=title.replace('"', "'")))
    return Short(folder)


SCENE_STUB = '''"""Draft scene. Build from lib/components.py; import checked numbers/shapes from verify.py."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parents[1]), str(HERE)]

from manim import DOWN, FadeIn, Scene  # noqa: E402

from lib.layout import ACCENT  # noqa: E402
from lib.components import Captions, beat, footer, hook  # noqa: E402


class Short(Scene):
    def construct(self):
        cap = Captions(self)
        beat(self, "hook")
        title = hook("{title}")
        self.play(FadeIn(title, shift=0.3 * DOWN), FadeIn(footer("TODO source credit")), run_time=0.5)
        cap.show("TODO: draft this Short", ACCENT)
        self.wait(2)
'''


def cmd_new(a):
    if a.blank:
        s = _new_short(None, a.blank)
    else:
        if not a.id:
            sys.exit("ms: give a catalog id (see `ms suggest`) or --blank \"Title\"")
        if a.id in used_catalog_ids():
            sys.exit(f"ms: {a.id} is already used by a Short")
        s = _new_short(catalog.get(a.id), None)
    p(f"created {s.folder.relative_to(paths.root())}  (status: drafting)")
    p(f"next: write verify.py, then scene.py, then `ms preview {s.number}`")


def cmd_verify(a):
    s = find(a.short)
    ok, out = s.verify()
    p(out)
    sys.exit(0 if ok else 1)


def cmd_preview(a):
    s = find(a.short)
    try:
        r = render.preview(s, a.at)
    except render.RenderError as e:
        sys.exit(f"ms: {e}")
    rel = r["path"].relative_to(paths.root()) if r["path"].is_relative_to(paths.root()) else r["path"]
    if r["beat"]:
        p(f"beat \"{r['beat']['name']}\" (from {render.fmt_time(r['beat']['t'])}) -> {rel}  ({r['duration']:.1f}s)")
    else:
        n = len(render.beats(s))
        p(f"v{r['version']} -> {rel}  ({r['duration']:.1f}s, {n} beats)")
    p(f"compare with the previous one: ms compare {s.number}")
    if a.open:
        render.open_file(r["path"])


def cmd_compare(a):
    s = find(a.short)
    dst = render.compare(s)
    p(f"side-by-side -> {dst.relative_to(paths.root()) if dst.is_relative_to(paths.root()) else dst}")
    if a.open:
        render.open_file(dst)


def cmd_note(a):
    s = find(a.short)
    text, beat = a.text, None
    m = re.match(r"^\s*(\d+:\d+(?:\.\d+)?)\s+(.*)$", text)
    if m:
        t = render.parse_time(m.group(1))
        try:
            b, _ = render.beat_at(s, t)
            beat = f"{m.group(1)} (beat \"{b['name']}\")"
        except SystemExit:
            beat = m.group(1)
        text = m.group(2)
    p(s.add_note(text, beat))


def cmd_music(a):
    audio = render._audio()
    if a.key:
        try:
            audio.piece(a.key)
        except ValueError as e:
            sys.exit(f"ms: {e}")
        path = audio.write_music(paths.out() / "music" / f"{a.key}.wav", 46.0, a.key)
        p(f"{a.key}: {path}")
        if a.open:
            render.open_file(path)
        return
    used: dict[str, list[str]] = {}
    for s in reversed(all_shorts()):     # newest Short first
        used.setdefault((s.data().get("music") or {}).get("piece") or audio.DEFAULT, []).append(s.number)
    newest = lambda key: int(used[key][0]) if key in used else 0  # noqa: E731
    p("least recently used first:")
    for key in sorted(audio.PIECES, key=newest):
        piece = audio.PIECES[key]
        p(f"  {key:<16} {', '.join(used.get(key, [])) or 'unused':<20} {piece.credit} ({piece.mood})")


def cmd_approve(a):
    s = find(a.short)
    for f in ("scene.py", "verify.py"):
        if not (s.folder / f).exists():
            sys.exit(f"ms: {s.name} has no {f}")
    try:
        credit = f"Music: {render.music_piece(s).credit}"
    except ValueError as e:
        sys.exit(f"ms: {s.name}: {e}")
    if credit not in ((s.data().get("youtube") or {}).get("description") or ""):
        sys.exit(f"ms: {s.name}'s YouTube description must credit its music: \"{credit}\"")
    ok, out = s.verify()
    if not ok:
        sys.exit(f"ms: verify.py fails, not approving.\n{out}")
    open_notes = s.open_notes()
    if open_notes and not a.force:
        sys.exit(f"ms: {len(open_notes)} open note(s) in NOTES.md; resolve them (or --force):\n  " + "\n  ".join(open_notes))
    try:
        s.transition("approve")
    except StatusError as e:
        sys.exit(f"ms: {e}")
    p(f"{s.name}: approved. Tonight's batch will render it (or run `ms batch {s.number}` now).")


# --- batch & mornings -------------------------------------------------------------------
def cmd_batch(a):
    only = find(a.short) if a.short else None
    r = batch.run(only=only, commit=a.commit)
    p(f"batch done: {len(r['ready'])} ready, {len(r['failed'])} failed, {len(r['skipped'])} skipped")
    sys.exit(1 if r["failed"] else 0)


def cmd_inbox(a):
    by = {st: [] for st in STATUSES}
    for s in all_shorts():
        by.setdefault(s.status, []).append(s)
    p(f"READY TO WATCH & UPLOAD ({len(by['ready'])}; aim to keep about a week's buffer)")
    for s in by["ready"]:
        kit = batch.ready_dir(s)
        p(f"  {s.name:<32} {kit.relative_to(paths.root()) if kit.is_relative_to(paths.root()) else kit}")
    if by["failed"]:
        p(f"\nFAILED ({len(by['failed'])}): open in Claude Code, fix, `ms approve` again")
        for s in by["failed"]:
            p(f"  {s.name:<32} {s.data().get('last_error')}")
    p(f"\nAPPROVED, rendering tonight ({len(by['approved'])}): {', '.join(s.name for s in by['approved']) or '-'}")
    drafting = [f"{s.name} ({len(s.open_notes())} open notes)" for s in by["drafting"]]
    p(f"DRAFTING ({len(drafting)}): {', '.join(drafting) or '-'}")


def cmd_reject(a):
    s = find(a.short)
    s.add_note(a.note, source="reject")
    try:
        s.transition("reject")
    except StatusError as e:
        sys.exit(f"ms: {e}")
    kit = batch.ready_dir(s)
    if kit.exists():
        import shutil
        shutil.rmtree(kit)
    p(f"{s.name}: back to drafting with your note. In Claude Code: /draft-short {s.number}")


def cmd_published(a):
    s = find(a.short)
    m = re.search(r"(?:shorts/|youtu\.be/|[?&]v=)([A-Za-z0-9_-]{11})", a.url)
    if not m:
        sys.exit("ms: that doesn't look like a YouTube video URL")
    import datetime as dt
    try:
        s.transition("publish")
    except StatusError as e:
        sys.exit(f"ms: {e}")
    s.update(**{"youtube.video_id": m.group(1), "youtube.url": a.url, "youtube.published_at": dt.date.today().isoformat()})
    p(f"{s.name}: published ({m.group(1)}). You can delete its folder in out/ready/ whenever.")


def cmd_status(a):
    shorts = all_shorts()
    if not shorts:
        p("no Shorts yet. Start with `ms suggest`.")
        return
    for st in STATUSES:
        group = [s for s in shorts if s.status == st]
        if group:
            p(f"{st.upper()} ({len(group)})")
            for s in group:
                d = s.data()
                p(f"  {s.name:<32} {d.get('title', '')}")


# --- wiring -----------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(prog="ms", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True, metavar="command")

    def add(name, fn, help_):
        sp = sub.add_parser(name, help=help_)
        sp.set_defaults(fn=fn)
        return sp

    sp = add("sources", cmd_sources, "list or scrape puzzle sources")
    sp.add_argument("action", choices=["list", "add"])
    sp.add_argument("source", nargs="?")
    sp.add_argument("--file", help="parse this downloaded .txt instead of fetching")
    sp.add_argument("--refresh", action="store_true", help="re-download even if cached")
    sp.add_argument("--rescore", action="store_true",
                    help="re-run the heuristic on entries still marked scored_by: heuristic")
    add("show", cmd_show, "read one catalog puzzle").add_argument("id")
    add("suggest", cmd_suggest, "ranked shortlist for the next Short").add_argument("-n", type=int, default=5)
    sp = add("new", cmd_new, "create a Short from a catalog puzzle")
    sp.add_argument("id", nargs="?")
    sp.add_argument("--blank", metavar="TITLE", help="an original problem, not from the catalog")
    add("verify", cmd_verify, "run verify.py").add_argument("short")
    sp = add("preview", cmd_preview, "fast preview render")
    sp.add_argument("short")
    sp.add_argument("--at", metavar="M:SS", help="only the beat containing this time")
    sp.add_argument("--open", action="store_true", help="open the video when done")
    sp = add("compare", cmd_compare, "newest preview vs previous")
    sp.add_argument("short")
    sp.add_argument("--open", action="store_true", help="open the video when done")
    sp = add("note", cmd_note, "add a review note")
    sp.add_argument("short")
    sp.add_argument("text", help='e.g. "0:12 slide is too fast"')
    sp = add("music", cmd_music, "the music library; a key writes a WAV to listen to")
    sp.add_argument("key", nargs="?")
    sp.add_argument("--open", action="store_true", help="open the WAV when done")
    sp = add("approve", cmd_approve, "human sign-off")
    sp.add_argument("short")
    sp.add_argument("--force", action="store_true", help="approve despite open notes")
    sp = add("batch", cmd_batch, "render + mix approved Shorts")
    sp.add_argument("short", nargs="?")
    sp.add_argument("--commit", action="store_true", help="git-commit the status changes")
    add("inbox", cmd_inbox, "what needs you this morning")
    sp = add("reject", cmd_reject, "send back to drafting with a note")
    sp.add_argument("short")
    sp.add_argument("note")
    sp = add("published", cmd_published, "record an upload")
    sp.add_argument("short")
    sp.add_argument("url")
    add("status", cmd_status, "every Short by status")

    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()

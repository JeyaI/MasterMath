# Master Math USA

Animated math-puzzle YouTube Shorts, rendered with Manim Community Edition.

- **Running the channel:** [OPERATING.md](OPERATING.md), the playbook.
- **Improving the software:** [ISSUES.md](ISSUES.md), the backlog (`/work-issue` in Claude Code).
- **How the code is organized:** [CLAUDE.md](CLAUDE.md).

```bash
pip install -e ".[dev]"     # plus ffmpeg, LaTeX + dvisvgm, Cairo/Pango, Inter (see OPERATING.md), or use the Dockerfile
ms status
python -m pytest -q
```

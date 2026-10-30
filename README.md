# mathshorts

Animated math-puzzle YouTube Shorts, rendered with Manim Community Edition.

```bash
pip install -e .            # needs ffmpeg, LaTeX + dvisvgm, Cairo/Pango, Inter font (or use the Dockerfile)
ms status
ms verify 0001              # check every answer in code
ms preview 0001             # fast 540x960 draft -> out/preview/
ms approve 0001             # your sign-off
ms render 0001 && ms mix 0001   # 1080x1920 + music -> out/final/
```

See `CLAUDE.md` for the format, licensing rules, status flow and the roadmap.

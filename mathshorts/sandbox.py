"""Where job-written code runs (#29): in the `mathshorts-job` container, never beside the secrets.

Jobs write scene.py and verify.py, and `ms tick` then runs them to check and render. Both happen
in a container that sees only the files it needs and gets only CLAUDE_CODE_OAUTH_TOKEN, so
nothing a job writes can read the YouTube or Discord tokens in ~/.config (rule 4 by design).

    sandbox: docker | host     in config/pipeline.yaml (MS_SANDBOX overrides); host is for tests
                               and for trying a change before rebuilding the image

Build the image: `docker build -t mathshorts . && docker build -t mathshorts-job -f Dockerfile.job .`

Moving the orchestrator into a container later (#13): it starts job containers through the host's
Docker socket, so mount paths must be host paths. Mount the repo and MS_CACHE at the same absolute
path inside and out; if that's impossible, MS_HOST_MAP="/inside=/on-host,..." rewrites them.
"""
from __future__ import annotations

import datetime as dt
import os
import shutil
import subprocess
import sys
from pathlib import Path

from . import paths, yamlio

IMAGE = "mathshorts-job"


def mode() -> str:
    if os.environ.get("MS_SANDBOX"):
        return os.environ["MS_SANDBOX"]
    p = paths.config() / "pipeline.yaml"
    cfg = (yamlio.load(p) or {}) if p.exists() else {}
    return str(cfg.get("sandbox", "docker"))


def host_path(p: Path) -> str:
    s = str(Path(p).resolve())
    for pair in filter(None, os.environ.get("MS_HOST_MAP", "").split(",")):
        inside, _, outside = pair.partition("=")
        if s == inside or s.startswith(inside.rstrip("/") + "/"):
            return outside.rstrip("/") + s[len(inside.rstrip("/")):]
    return s


def docker(argv: list[str], mounts: list[tuple[Path, str, str]], env: dict[str, str],
           pass_env: tuple[str, ...] = ()) -> list[str]:
    """`docker run` for argv. mounts: (host path, container path, "rw" | "ro"). `env` values appear
    in the command line; names in `pass_env` are passed by name, so a secret never does."""
    cmd = ["docker", "run", "--rm", "-u", f"{os.getuid()}:{os.getgid()}", "-w", "/app",
           "-e", "HOME=/tmp", "-e", "PYTHONDONTWRITEBYTECODE=1"]
    for k, v in env.items():
        cmd += ["-e", f"{k}={v}"]
    for k in pass_env:
        cmd += ["-e", k]
    for src, dest, how in mounts:
        cmd += ["-v", f"{host_path(src)}:{dest}:{how}"]
    return [*cmd, IMAGE, *argv]


class Checks:
    """verify, check and the final render of one Short, with the main checkout's code.

    A job's worktree is thrown away; only its Short folder is copied back, so a job that edited
    mathshorts/ or lib/ can't change what checks it.
    """

    def __init__(self, how: str | None = None):
        self.how = how or mode()

    def ms(self, *args: str, out: Path) -> tuple[bool, str]:
        out.mkdir(parents=True, exist_ok=True)
        if self.how == "docker":
            (out / "sfx").mkdir(exist_ok=True)     # scenes rewrite assets/sfx on import (lib/audio.py)
            cmd = docker(["ms", *args], [(paths.root(), "/app", "ro"), (out, "/out", "rw"),
                                         (out / "sfx", "/app/assets/sfx", "rw")],
                         {"MS_ROOT": "/app", "MS_OUT": "/out"})
            env = None
        else:
            cmd = [sys.executable, "-m", "mathshorts.cli", *args]
            env = {**os.environ, "MS_OUT": str(out)}
        r = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=paths.root())
        return r.returncode == 0, (r.stdout + r.stderr).strip()

    def _scratch(self, short, what: str) -> Path:
        stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        return paths.cache() / "sandbox" / f"{short.number}-{what}-{stamp}"

    def run(self, short, *args: str) -> tuple[bool, str]:
        tmp = self._scratch(short, args[0])
        try:
            return self.ms(*args, short.number, out=tmp)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def verify(self, short) -> tuple[bool, str]:
        return self.run(short, "verify")

    def check(self, short) -> tuple[bool, str]:
        return self.run(short, "check")

    def render(self, short, dest: Path) -> tuple[bool, str]:
        """The final video (1080x1920, mixed) for review; it is the file that later goes public.
        Its thumbnail (the frame where the problem is posed, #41) lands beside it as vN.png."""
        tmp = self._scratch(short, "render")
        try:
            ok, log = self.ms("render", short.number, "--out", "/out/kit" if self.how == "docker" else str(tmp / "kit"),
                              out=tmp)
            src = tmp / "kit" / f"{short.name}.mp4"
            if ok and src.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), dest)
                thumb = tmp / "kit" / "thumbnail.png"
                if thumb.exists():
                    shutil.move(str(thumb), dest.with_suffix(".png"))
                return True, log
            return False, log or "no video"
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

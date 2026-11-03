"""Unattended Claude jobs (#28): one `claude -p` run in a throwaway git worktree.

The job sees a clean checkout at HEAD, writes one Short's folder, and that folder is copied back.
It holds no Discord or YouTube credentials, cannot run git or change a status, and is denied any
command not on the allowlist instead of waiting for a person. Prompts are in scripts/jobs/.

Every run is logged to out/logs/jobs.jsonl with its seconds, turns and `total_cost_usd`
(an estimate; jobs run on the Pro token, so it isn't a bill).
"""
from __future__ import annotations

import datetime as dt
import json
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from . import paths

PROMPTS = paths.REPO / "scripts" / "jobs"
BUDGET_USD = {"script": 10, "revise": 10}
ALLOWED = ["Read", "Write", "Edit", "Glob", "Grep",
           "Bash(ms show:*)", "Bash(ms suggest:*)", "Bash(ms new:*)", "Bash(ms verify:*)", "Bash(ms music:*)",
           "Bash(ms status:*)", "Bash(python:*)", "Bash(ls:*)"]
DENIED = ["Bash(git:*)", "Bash(ms approve:*)", "Bash(ms reject:*)", "Bash(ms published:*)",
          "Bash(ms batch:*)", "Bash(ms tick:*)", "Bash(ms discord:*)"]
SCHEMA = {"type": "object", "required": ["short", "verify_passed", "summary"],
          "properties": {"short": {"type": "string", "description": "the Short's folder name, e.g. 0006-the-six-frogs"},
                         "catalog_id": {"type": "string"}, "verify_passed": {"type": "boolean"},
                         "summary": {"type": "string", "description": "two or three lines for the reviewer"}}}


@dataclass
class JobResult:
    ok: bool
    short: str | None = None              # folder name, copied back into shorts/
    summary: str = ""
    error: str = ""
    usage: dict = field(default_factory=dict)


def _env(tree: Path) -> dict:
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("CLAUDECODE", "CLAUDE_PID", "CLAUDE_EFFORT", "CLAUDE_CODE_", "DISCORD_", "MS_DISCORD_"))
           or k == "CLAUDE_CODE_OAUTH_TOKEN"}
    env.pop("ANTHROPIC_API_KEY", None)      # it would override the Pro token
    env["MS_ROOT"] = str(tree)
    env.pop("MS_OUT", None)
    venv = Path.home() / ".venvs" / "mathshorts" / "bin"
    env["PATH"] = f"{venv}:{env.get('PATH', '')}"
    return env


def prompt(kind: str, short: str | None = None, comment: str | None = None) -> str:
    if kind == "script":
        return "Run the script job for a new Master Math USA Short."
    return (f"Run the revise job for Short {short}. The reviewer's comment, verbatim:\n\n"
            f"<comment>\n{comment}\n</comment>")


def run(kind: str, short: str | None = None, comment: str | None = None) -> JobResult:
    """The real runner. `ms tick` takes any callable with this signature, so tests fake it."""
    root = paths.root()
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    tree = paths.cache() / "jobs" / f"{kind}-{stamp}"
    tree.parent.mkdir(parents=True, exist_ok=True)
    add = subprocess.run(["git", "worktree", "add", "-q", "--detach", str(tree)], cwd=root,
                         capture_output=True, text=True)
    if add.returncode:
        return JobResult(False, error=f"git worktree: {add.stderr.strip()}")
    log = paths.out() / "logs" / f"job-{kind}-{stamp}.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    started = dt.datetime.now()
    try:
        cmd = ["claude", "-p", prompt(kind, short, comment),
               "--append-system-prompt-file", str(PROMPTS / f"{kind}.md"),
               "--permission-prompts", "none",
               "--allowedTools", *ALLOWED, "--disallowedTools", *DENIED,
               "--max-budget-usd", str(BUDGET_USD[kind]),
               "--output-format", "stream-json", "--verbose", "--json-schema", json.dumps(SCHEMA)]
        with open(log, "w") as out, open(log.with_suffix(".err"), "w") as err:
            code = subprocess.run(cmd, cwd=tree, env=_env(tree), stdout=out, stderr=err).returncode
        result = parse(log)
        usage = {"job": kind, "short": short, "exit": code,
                 "seconds": int((dt.datetime.now() - started).total_seconds()),
                 **{k: result.get(k) for k in ("subtype", "is_error", "num_turns", "total_cost_usd")},
                 "log": log.name}
        _log_usage(usage)
        out_ = result.get("structured_output") or {}
        name = out_.get("short") or short
        if code or result.get("is_error") or not name:
            return JobResult(False, name, error=f"exit {code}, {result.get('subtype') or 'no result'} (log: {log.name})",
                             usage=usage)
        src = tree / "shorts" / name
        if not src.is_dir():
            return JobResult(False, name, error=f"the job reported {name} but wrote no such folder", usage=usage)
        dest = paths.shorts() / name
        if kind == "script" and dest.exists():
            return JobResult(False, name, error=f"{name} already exists in the main checkout", usage=usage)
        shutil.copytree(src, dest, dirs_exist_ok=True)
        return JobResult(True, name, out_.get("summary", ""), usage=usage)
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(tree)], cwd=root, capture_output=True)


def parse(log: Path) -> dict:
    result = {}
    if log.exists():
        for line in log.read_text(errors="replace").splitlines():
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if row.get("type") == "result":
                result = row
    return result


def _log_usage(row: dict) -> None:
    path = paths.out() / "logs" / "jobs.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps({"at": dt.datetime.now().isoformat(timespec="seconds"), **row}) + "\n")

#!/usr/bin/env bash
# Nightly batch: render + mix every approved Short, then commit the status changes.
# Schedule it (see OPERATING.md > One-time setup), or just run it by hand.
# Exits non-zero if a Short failed or the status changes could not be committed.
#
#   MS_USE_DOCKER=1  render inside the mathshorts Docker image instead of the local install
#   MS_BIN=...       path to the ms command; the default is ms on PATH, then ~/.venvs/mathshorts/bin/ms
set -uo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"
mkdir -p out/logs

commit_status() {
  git add shorts || return 1
  git diff --cached --quiet && return 0
  git commit -q -m "batch $(date +%F)"
}

{
  echo "=== $(date -Is) nightly batch"
  if [[ "${MS_USE_DOCKER:-0}" == "1" ]]; then
    docker run --rm -u "$(id -u):$(id -g)" -e HOME=/tmp -v "$root":/app mathshorts ms batch
  else
    "${MS_BIN:-$(command -v ms || echo "$HOME/.venvs/mathshorts/bin/ms")}" batch
  fi
  status=$?                         # 1 = at least one Short failed; the others still built
  # With the repo under /mnt/c, the working directory can stop resolving for a while after
  # the container exits, so git fails. Return by absolute path, and retry.
  committed=0
  for _ in 1 2 3 4 5 6; do
    cd "$root" && commit_status && { committed=1; break; }
    sleep 5
  done
  if [[ $committed == 0 ]]; then
    echo "ERROR: status changes not committed; run: git add shorts && git commit -m 'batch $(date +%F)'"
    [[ $status == 0 ]] && status=2
  fi
  echo "=== done (exit $status)"
} >> "$root/out/logs/nightly.log" 2>&1
exit "$status"

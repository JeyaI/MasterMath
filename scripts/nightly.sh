#!/usr/bin/env bash
# Nightly batch: render + mix every approved Short, then commit the status changes.
# Schedule it (see OPERATING.md > One-time setup), or just run it by hand.
#
#   MS_USE_DOCKER=1  render inside the mathshorts Docker image instead of the local install
#   MS_BIN=...       path to the ms command if it isn't on the scheduler's PATH
set -uo pipefail
cd "$(dirname "$0")/.."
mkdir -p out/logs
{
  echo "=== $(date -Is) nightly batch"
  if [[ "${MS_USE_DOCKER:-0}" == "1" ]]; then
    docker run --rm -u "$(id -u):$(id -g)" -e HOME=/tmp -v "$PWD":/app mathshorts ms batch
  else
    "${MS_BIN:-ms}" batch
  fi
  status=$?                         # 1 = at least one Short failed; the others still built
  git add shorts
  git diff --cached --quiet || git commit -q -m "batch $(date +%F)"
  echo "=== done (exit $status)"
} >> out/logs/nightly.log 2>&1

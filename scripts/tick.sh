#!/usr/bin/env bash
# The script loop's orchestrator (#28). Schedule it, e.g. in WSL's crontab:
#   */5 * * * *  ~/mathshorts/scripts/tick.sh            read Discord, run revise jobs
#   0 2 * * *    ~/mathshorts/scripts/tick.sh --draft    also write one new script
# Secrets come from ~/.config/mathshorts.env (template: config/mathshorts.env.example).
set -uo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"
mkdir -p out/logs
set -a; . "$HOME/.config/mathshorts.env"; set +a
export PATH="$HOME/.venvs/mathshorts/bin:$HOME/.local/bin:$PATH"
{
  echo "=== $(date -Is) tick $*"
  ms tick "$@"
  status=$?
  echo "=== done (exit $status)"
} >> out/logs/tick.log 2>&1
exit "$status"

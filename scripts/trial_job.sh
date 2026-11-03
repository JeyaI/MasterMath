#!/usr/bin/env bash
# Phase 0 trial (#25): run one pipeline job through `claude -p` on the Pro token, in a worktree.
#
#   scripts/trial_job.sh script    choose a puzzle, write SCRIPT.md, pass verify.py
#   scripts/trial_job.sh animate   build and preview the scene from that script
#
# The token comes from ~/.config/mathshorts.env. The Short stays in ~/mathshorts-trial, uncommitted,
# on branch trial/25. Logs go to out/trial/<job>.jsonl; the last line holds the cost and usage.
set -uo pipefail

job="${1:?usage: trial_job.sh script|animate}"
case "$job" in
  script)  budget=10 ;;
  animate) budget=25 ;;
  *) echo "unknown job: $job" >&2; exit 2 ;;
esac

root="$(cd "$(dirname "$0")/.." && pwd)"
tree="$HOME/mathshorts-trial"
log="$root/out/trial/$job.jsonl"
mkdir -p "$root/out/trial"

if [[ ! -d "$tree" ]]; then
  git -C "$root" worktree add -q -b trial/25 "$tree" || exit 1
fi

# Start clean: no parent session's variables, and no API key to override the Pro token.
for v in $(compgen -e | grep -E '^(CLAUDECODE|CLAUDE_PID|CLAUDE_EFFORT|CLAUDE_CODE_)'); do unset "$v"; done
unset ANTHROPIC_API_KEY
set -a; . "$HOME/.config/mathshorts.env"; set +a

export MS_ROOT="$tree"
export PATH="$HOME/.venvs/mathshorts/bin:$PATH"
cd "$tree" || exit 1

schema='{"type":"object","required":["short","catalog_id","verify_passed","summary"],"properties":{"short":{"type":"string"},"catalog_id":{"type":"string"},"verify_passed":{"type":"boolean"},"summary":{"type":"string"}}}'

start=$(date +%s)
claude -p "Run the $job job for a new Master Math USA Short." \
  --append-system-prompt-file "$root/scripts/trial/${job}_job.md" \
  --permission-prompts none \
  --allowedTools Read Write Edit Glob Grep \
    'Bash(ms:*)' 'Bash(python:*)' 'Bash(ffmpeg:*)' 'Bash(ffprobe:*)' 'Bash(ls:*)' 'Bash(mkdir:*)' \
  --disallowedTools 'Bash(git:*)' 'Bash(ms approve:*)' 'Bash(ms reject:*)' 'Bash(ms published:*)' 'Bash(ms batch:*)' \
  --max-budget-usd "$budget" \
  --output-format stream-json --verbose \
  --json-schema "$schema" \
  > "$log" 2> "$log.err"
status=$?

python3 - "$log" "$status" "$(( $(date +%s) - start ))" <<'EOF'
import json, sys
path, status, secs = sys.argv[1:]
result = None
for line in open(path):
    try:
        row = json.loads(line)
    except ValueError:
        continue
    if row.get("type") == "result":
        result = row
if result is None:
    sys.exit(f"exit {status} after {secs}s: no result line, see {path}.err")
keep = ("subtype", "is_error", "num_turns", "total_cost_usd", "duration_api_ms", "structured_output")
print(json.dumps({"exit": int(status), "seconds": int(secs), **{k: result.get(k) for k in keep},
                  "models": list((result.get("modelUsage") or {}))}, indent=2))
EOF
exit "$status"

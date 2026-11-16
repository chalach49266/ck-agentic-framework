#!/usr/bin/env bash
set -euo pipefail
live=false
workspace=devfab
usage() { echo 'Usage: smoke.sh [--live] [--workspace devfab|nv|washu]'; }
while (($#)); do
  case "$1" in
    --live) live=true; shift ;;
    --workspace) [[ $# -ge 2 ]] || { usage >&2; exit 2; }; workspace=$2; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
done
CK_RUN=${CK_RUN:-"$HOME/.local/bin/ck-run"}
"$CK_RUN" models
"$CK_RUN" --help
if ! "$live"; then
  echo 'Offline CLI smoke passed. Use --live to launch opus, sol and grok in auto mode.'
  exit 0
fi
run_dir="$HOME/PhD_local/agent_runs"
mkdir -p "$run_dir"
prompt=$(mktemp "$run_dir/ck-smoke-XXXXXX.md")
cat > "$prompt" <<'PROMPT'
This is an installation smoke test. Do not edit workspace files or use network tools.
Use only your own run folder for result.md and summary.md, following the ck-run OUTPUT CONTRACT.
Report that the CLI started and returned, name the model only if known, and mark unknown details UNKNOWN.
Use verification not_checked. Do not claim that lab work or a hardware check happened.
PROMPT
ask_output=$("$CK_RUN" ask open --words 'Run the installation smoke race.' --size S \
  --title 'Installation smoke race' --pattern race --models opus,sol,grok)
printf '%s\n' "$ask_output"
ask=${ask_output%%$'\n'*}
"$CK_RUN" race --ask "$ask" --prompt-file "$prompt" --title 'Installation smoke race' \
  --workspace "$workspace" --models opus,sol,grok --mode auto
printf 'Race launched. Inspect results with: %q race show --ask %q\n' "$CK_RUN" "$ask"

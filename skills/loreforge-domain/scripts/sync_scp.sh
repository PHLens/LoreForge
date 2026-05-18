#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: sync_scp.sh --remote <user@host:path> [--wiki <path>] [--dry-run]

Run LoreForge's canonical SCP publish flow.

Options:
  --wiki <path>       Local wiki checkout. Defaults to WIKI_PATH or ~/wiki.
  --remote <target>   scp remote target, for example user@example.com:/srv/wiki.
  --dry-run           Print the ssh/scp commands without running them.
  -h, --help          Show this help.
EOF
}

shell_quote() {
  local value="$1"
  printf "'%s'" "${value//\'/\'\\\'\'}"
}

print_command() {
  printf '%q' "$1"
  shift
  for arg in "$@"; do
    printf ' %q' "$arg"
  done
  printf '\n'
}

wiki="${WIKI_PATH:-~/wiki}"
remote=""
dry_run=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --wiki)
      [[ $# -ge 2 ]] || { echo "missing value for --wiki" >&2; exit 2; }
      wiki="$2"
      shift 2
      ;;
    --remote)
      [[ $# -ge 2 ]] || { echo "missing value for --remote" >&2; exit 2; }
      remote="$2"
      shift 2
      ;;
    --dry-run)
      dry_run=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$remote" ]]; then
  echo "--remote is required" >&2
  exit 2
fi

case "$wiki" in
  "~")
    wiki="$HOME"
    ;;
  "~/"*)
    wiki="$HOME/${wiki#~/}"
    ;;
esac

if [[ "$remote" != *:* ]]; then
  echo "--remote must use scp target syntax: user@host:path" >&2
  exit 2
fi

remote_host="${remote%%:*}"
remote_path="${remote#*:}"

if [[ -z "$remote_host" || -z "$remote_path" ]]; then
  echo "--remote must include both host and path: user@host:path" >&2
  exit 2
fi

mkdir_cmd=(
  ssh
  "$remote_host"
  "mkdir -p -- $(shell_quote "$remote_path")"
)
scp_cmd=(
  scp
  -r
  "${wiki%/}/."
  "$remote"
)

if [[ "$dry_run" -eq 1 ]]; then
  print_command "${mkdir_cmd[@]}"
  print_command "${scp_cmd[@]}"
  exit 0
fi

"${mkdir_cmd[@]}"
exec "${scp_cmd[@]}"

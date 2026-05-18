#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: sync_rclone.sh --remote <remote:path> [--wiki <path>] [--resync] [--dry-run]

Run LoreForge's canonical rclone bisync flow.

Options:
  --wiki <path>       Local wiki checkout. Defaults to WIKI_PATH or ~/wiki.
  --remote <target>   rclone remote:path target, for example wiki-sftp:LoreForgeWiki.
  --resync            Use for first sync or recovery after confirming the local wiki should seed the remote.
  --dry-run           Print the rclone command without running it.
  -h, --help          Show this help.
EOF
}

wiki="${WIKI_PATH:-~/wiki}"
remote=""
resync=0
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
    --resync)
      resync=1
      shift
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

cmd=(
  rclone
  bisync
  "$wiki"
  "$remote"
  --create-empty-src-dirs
  --resilient
  --recover
  --max-lock
  2m
  --compare
  size,modtime
  --conflict-resolve
  none
  --conflict-loser
  num
)

if [[ "$resync" -eq 1 ]]; then
  cmd+=(--resync)
fi

cmd+=(-P -v)

if [[ "$dry_run" -eq 1 ]]; then
  printf '%q' "${cmd[0]}"
  for arg in "${cmd[@]:1}"; do
    printf ' %q' "$arg"
  done
  printf '\n'
  exit 0
fi

exec "${cmd[@]}"

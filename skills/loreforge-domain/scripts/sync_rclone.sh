#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: sync_rclone.sh --remote <remote:path> [--wiki <path>] [--mode pull|push|bootstrap] [--delete-excluded] [--dry-run]

Run LoreForge's canonical rclone sync flow.

Default mode is remote-first pull. Agents should run pull before reading or
editing a rclone-backed wiki, then run push only after successful local edits.

Options:
  --wiki <path>          Local wiki checkout. Defaults to WIKI_PATH or ~/wiki.
  --remote <target>      rclone remote:path target, for example wiki-sftp:LoreForgeWiki.
  --mode pull            Remote -> local. This is the default and treats remote as authoritative.
  --mode push            Local -> remote. Use only after pulling first and completing local edits.
  --mode bootstrap       Local -> remote for first sync or recovery after confirming local should seed remote.
  --resync               Deprecated alias for --mode bootstrap.
  --delete-excluded      Pass --delete-excluded to rclone sync.
  --dry-run              Print the rclone command without running it.
  -h, --help             Show this help.
EOF
}

wiki="${WIKI_PATH:-~/wiki}"
remote=""
mode="pull"
dry_run=0
delete_excluded=0

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
    --mode)
      [[ $# -ge 2 ]] || { echo "missing value for --mode" >&2; exit 2; }
      mode="$2"
      shift 2
      ;;
    --resync)
      mode="bootstrap"
      shift
      ;;
    --delete-excluded)
      delete_excluded=1
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

case "$mode" in
  pull|push|bootstrap)
    ;;
  *)
    echo "--mode must be one of: pull, push, bootstrap" >&2
    exit 2
    ;;
esac

if [[ "$wiki" == "~" ]]; then
  wiki="$HOME"
elif [[ "$wiki" == "~/"* ]]; then
  wiki="$HOME/${wiki#"~/"}"
fi

src="$remote"
dst="$wiki"
if [[ "$mode" == "push" || "$mode" == "bootstrap" ]]; then
  src="$wiki"
  dst="$remote"
fi

cmd=(
  rclone
  sync
  "$src"
  "$dst"
  --create-empty-src-dirs
  --exclude
  ".obsidian*/**"
  --exclude
  ".obsidian*"
)

if [[ "$delete_excluded" -eq 1 ]]; then
  cmd+=(--delete-excluded)
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

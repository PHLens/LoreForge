#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

NAME_REGEX='^[A-Za-z0-9._-]+$'
TARGET_NAME_REGEX='^[A-Za-z0-9_-]+$'
DEFAULT_MODE="generic"
DEFAULT_READ_ROOT="."
DEFAULT_TARGET="notes"
DEFAULT_TARGET_SPEC="notes=.:Default writeback target"
DEFAULT_REGISTRY="${LOREFORGE_REGISTRY:-$HOME/.config/loreforge/registry.toml}"

usage() {
  cat <<'EOF'
Usage:
  setup-binding.sh <name> <target_repo> [options]

Options:
  --mode MODE              generic or native, default: generic
  --init-native-template   Copy templates/wiki into an empty native target
  --description TEXT       Binding description
  --remote URL             Optional target repo remote
  --state-dir PATH         Runtime state path
  --registry PATH          Registry path, default: ~/.config/loreforge/registry.toml
  --read-root PATH         Add read root, repeatable, default: .
  --target SPEC            Add target as name=path[:description], repeatable
  --default-target NAME    Default writeback target
  --no-default             Do not make this binding the registry default
  --no-git                 Do not run git init for native starter creation
  -h, --help               Show help
EOF
}

die() {
  printf 'setup-binding: %s\n' "$*" >&2
  exit 1
}

need_value() {
  local option="$1"
  local value="${2:-}"

  if [ -z "$value" ]; then
    die "$option requires a value"
  fi
}

reject_newline() {
  local label="$1"
  local value="$2"

  if [[ "$value" == *$'\n'* ]]; then
    die "$label cannot contain newlines"
  fi
}

expand_tilde() {
  local path="$1"

  case "$path" in
    "~")
      printf '%s\n' "$HOME"
      ;;
    "~/"*)
      printf '%s/%s\n' "$HOME" "${path#~/}"
      ;;
    *)
      printf '%s\n' "$path"
      ;;
  esac
}

absolute_path() {
  local path
  path="$(expand_tilde "$1")"

  if command -v realpath >/dev/null 2>&1; then
    realpath -m -- "$path"
    return
  fi

  case "$path" in
    /*)
      printf '%s\n' "$path"
      ;;
    *)
      printf '%s/%s\n' "$(pwd -P)" "$path"
      ;;
  esac
}

toml_escape() {
  local value="$1"
  value="${value//\\/\\\\}"
  value="${value//\"/\\\"}"
  printf '%s' "$value"
}

toml_string() {
  printf '"%s"' "$(toml_escape "$1")"
}

toml_array() {
  local first=1
  local item

  printf '['
  for item in "$@"; do
    if [ "$first" -eq 0 ]; then
      printf ', '
    fi
    toml_string "$item"
    first=0
  done
  printf ']'
}

path_inside_root() {
  local root="$1"
  local path="$2"

  [ "$path" = "$root" ] || [[ "$path" == "$root/"* ]]
}

resolve_inside_root() {
  local root="$1"
  local rel_path="$2"
  local label="$3"
  local resolved

  reject_newline "$label" "$rel_path"

  if [ -z "$rel_path" ]; then
    die "$label cannot be empty"
  fi

  case "$rel_path" in
    /*)
      die "$label must be relative to the target repo: $rel_path"
      ;;
  esac

  resolved="$(absolute_path "$root/$rel_path")"
  if ! path_inside_root "$root" "$resolved"; then
    die "$label escapes target repo: $rel_path"
  fi

  printf '%s\n' "$resolved"
}

target_seen() {
  local needle="$1"
  local target

  for target in "${target_names[@]}"; do
    if [ "$target" = "$needle" ]; then
      return 0
    fi
  done

  return 1
}

add_target_spec() {
  local spec="$1"
  local target_name
  local rest
  local target_path
  local target_description

  reject_newline "--target" "$spec"

  if [[ "$spec" != *=* ]]; then
    die "--target must use name=path[:description]: $spec"
  fi

  target_name="${spec%%=*}"
  rest="${spec#*=}"

  if [ -z "$target_name" ] || [ -z "$rest" ]; then
    die "--target must include non-empty name and path: $spec"
  fi

  if ! [[ "$target_name" =~ $TARGET_NAME_REGEX ]]; then
    die "target name must match $TARGET_NAME_REGEX: $target_name"
  fi

  if target_seen "$target_name"; then
    die "duplicate target: $target_name"
  fi

  if [[ "$rest" == *:* ]]; then
    target_path="${rest%%:*}"
    target_description="${rest#*:}"
  else
    target_path="$rest"
    target_description=""
  fi

  if [ -z "$target_path" ]; then
    die "--target path cannot be empty: $spec"
  fi

  reject_newline "target path" "$target_path"
  reject_newline "target description" "$target_description"

  target_names+=("$target_name")
  target_paths+=("$target_path")
  target_descriptions+=("$target_description")
}

write_state() {
  mkdir -p \
    "$STATE_DIR/packages/ingest" \
    "$STATE_DIR/packages/writeback" \
    "$STATE_DIR/packages/archive" \
    "$STATE_DIR/reports" \
    "$STATE_DIR/cache" \
    "$STATE_DIR/locks" \
    "$STATE_DIR/tmp"

  {
    printf 'schema_version = "0.1"\n'
    printf 'binding = '
    toml_string "$NAME"
    printf '\n'
    printf 'target_repo = '
    toml_string "$TARGET_REPO"
    printf '\n'
  } > "$STATE_DIR/state.toml"
}

write_native_config() {
  mkdir -p "$TARGET_REPO/.loreforge"

  {
    printf '# LoreForge wiki instance metadata\n\n'
    printf 'schema_version = "0.1"\n'
    printf 'name = '
    toml_string "$NAME"
    printf '\n'
    printf 'description = '
    toml_string "$DESCRIPTION"
    printf '\n\n'
    printf '# Entry files, relative to wiki root.\n'
    printf 'agents_file = "AGENTS.md"\n'
    printf 'vault_map = "00_System/Vault Map.md"\n'
    printf 'schema_file = "00_System/Schema.md"\n'
    printf 'index_file = "00_System/+Wiki Index.md"\n'
    printf 'log_file = "00_System/Wiki Log.md"\n'
    printf 'views_dir = "00_System/Views"\n\n'
    printf '# Default task view used when no more specific view is requested.\n'
    printf 'default_view = "default"\n\n'
    printf '[views]\n'
    printf 'default = "00_System/Views/default.md"\n'
    printf 'query = "00_System/Views/query.md"\n'
    printf 'ingest = "00_System/Views/ingest.md"\n'
    printf 'writeback = "00_System/Views/writeback.md"\n'
    printf 'promote = "00_System/Views/promote.md"\n'
    printf 'maintenance = "00_System/Views/maintenance.md"\n\n'
    printf '[paths]\n'
    printf 'inbox = "10_Inbox"\n'
    printf 'ingest = "10_Inbox/ingest"\n'
    printf 'writeback = "10_Inbox/writeback"\n'
    printf 'cards = "Cards"\n'
    printf 'sources = "Sources"\n'
    printf 'mocs = "MOCs"\n'
    printf 'archive = "Archive"\n\n'
    printf '[git]\n'
    printf 'remote = '
    toml_string "$REMOTE"
    printf '\n'
    printf 'default_branch = "main"\n'
  } > "$TARGET_REPO/.loreforge/wiki.toml"
}

target_is_empty_or_missing() {
  if [ ! -e "$TARGET_REPO" ]; then
    return 0
  fi

  [ -d "$TARGET_REPO" ] || die "target repo exists but is not a directory: $TARGET_REPO"

  if find "$TARGET_REPO" -mindepth 1 -print -quit | grep -q .; then
    return 1
  fi

  return 0
}

init_native_template() {
  if ! target_is_empty_or_missing; then
    die "native template setup requires an empty or missing target repo: $TARGET_REPO"
  fi

  mkdir -p "$TARGET_REPO"
  cp -R "$ROOT/templates/wiki/." "$TARGET_REPO/"
  write_native_config

  if [ "$NO_GIT" -eq 0 ] && command -v git >/dev/null 2>&1 && [ ! -d "$TARGET_REPO/.git" ]; then
    git -C "$TARGET_REPO" init >/dev/null
  fi
}

ensure_target_dirs() {
  local index
  local target_path
  local target_abs

  for index in "${!target_names[@]}"; do
    target_path="${target_paths[$index]}"
    target_abs="$(resolve_inside_root "$TARGET_REPO" "$target_path" "target path")"
    mkdir -p "$target_abs"
  done
}

validate_read_roots() {
  local read_root

  for read_root in "${read_roots[@]}"; do
    resolve_inside_root "$TARGET_REPO" "$read_root" "read root" >/dev/null
  done
}

write_binding_block() {
  local file="$1"
  local index

  {
    printf '[[bindings]]\n'
    printf 'name = '
    toml_string "$NAME"
    printf '\n'
    printf 'target_repo = '
    toml_string "$TARGET_REPO"
    printf '\n'
    printf 'state_dir = '
    toml_string "$STATE_DIR"
    printf '\n'
    printf 'mode = '
    toml_string "$MODE"
    printf '\n'
    printf 'remote = '
    toml_string "$REMOTE"
    printf '\n'
    printf 'description = '
    toml_string "$DESCRIPTION"
    printf '\n'
    printf 'default_target = '
    toml_string "$DEFAULT_TARGET_NAME"
    printf '\n'
    printf 'read_roots = '
    toml_array "${read_roots[@]}"
    printf '\n'

    for index in "${!target_names[@]}"; do
      printf '\n'
      printf '[bindings.targets.%s]\n' "${target_names[$index]}"
      printf 'path = '
      toml_string "${target_paths[$index]}"
      printf '\n'
      printf 'description = '
      toml_string "${target_descriptions[$index]}"
      printf '\n'
    done

    if [ "$MODE" = "native" ]; then
      printf '\n'
      printf '[bindings.native]\n'
      printf 'index_file = "00_System/+Wiki Index.md"\n'
      printf 'log_file = "00_System/Wiki Log.md"\n'
      printf 'views_dir = "00_System/Views"\n'
    fi
  } > "$file"
}

filter_registry() {
  local source="$1"
  local dest="$2"
  local strip_default="$3"

  if [ ! -f "$source" ]; then
    : > "$dest"
    return
  fi

  awk -v name="$NAME" -v strip_default="$strip_default" '
    function trim(value) {
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
      return value
    }

    function unquote(value) {
      value = trim(value)
      sub(/^"/, "", value)
      sub(/"$/, "", value)
      return value
    }

    function flush_block() {
      if (in_block) {
        if (block_name != name) {
          printf "%s", block
        }
      }
      in_block = 0
      block = ""
      block_name = ""
    }

    /^[[:space:]]*\[\[bindings\]\][[:space:]]*$/ {
      flush_block()
      in_block = 1
      block = $0 ORS
      next
    }

    in_block {
      block = block $0 ORS
      if (block_name == "" && $0 ~ /^[[:space:]]*name[[:space:]]*=/) {
        value = $0
        sub(/^[^=]*=[[:space:]]*/, "", value)
        block_name = unquote(value)
      }
      next
    }

    {
      if (strip_default == "1" && $0 ~ /^[[:space:]]*default[[:space:]]*=/) {
        next
      }
      print
    }

    END {
      flush_block()
    }
  ' "$source" > "$dest"
}

emit_default() {
  local source="$1"
  local dest="$2"
  local default_line

  default_line="default = \"$(toml_escape "$NAME")\""

  awk -v default_line="$default_line" '
    !inserted && $0 !~ /^[[:space:]]*#/ && $0 !~ /^[[:space:]]*$/ {
      print default_line
      print ""
      inserted = 1
    }
    { print }
    END {
      if (!inserted) {
        print default_line
      }
    }
  ' "$source" > "$dest"
}

update_registry() {
  local registry_dir
  local tmp_dir
  local filtered
  local with_default
  local new_block
  local strip_default

  registry_dir="$(dirname "$REGISTRY")"
  mkdir -p "$registry_dir"

  tmp_dir="$(mktemp -d)"
  filtered="$tmp_dir/filtered.toml"
  with_default="$tmp_dir/with-default.toml"
  new_block="$tmp_dir/new-binding.toml"

  if [ "$NO_DEFAULT" -eq 0 ]; then
    strip_default=1
  else
    strip_default=0
  fi

  filter_registry "$REGISTRY" "$filtered" "$strip_default"

  if [ "$NO_DEFAULT" -eq 0 ]; then
    emit_default "$filtered" "$with_default"
  else
    cp "$filtered" "$with_default"
  fi

  write_binding_block "$new_block"

  {
    if [ -s "$with_default" ]; then
      cat "$with_default"
      printf '\n'
    fi
    cat "$new_block"
    printf '\n'
  } > "$REGISTRY"

  rm -rf "$tmp_dir"
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

if [ "$#" -lt 2 ]; then
  usage >&2
  exit 1
fi

NAME="$1"
TARGET_REPO_INPUT="$2"
shift 2

MODE="$DEFAULT_MODE"
MODE_SET=0
INIT_NATIVE_TEMPLATE=0
DESCRIPTION=""
REMOTE=""
STATE_DIR_INPUT=""
REGISTRY_INPUT="$DEFAULT_REGISTRY"
DEFAULT_TARGET_NAME="$DEFAULT_TARGET"
NO_DEFAULT=0
NO_GIT=0
read_roots=()
target_names=()
target_paths=()
target_descriptions=()

while [ "$#" -gt 0 ]; do
  case "$1" in
    --mode)
      need_value "$1" "${2:-}"
      MODE="$2"
      MODE_SET=1
      shift 2
      ;;
    --init-native-template)
      INIT_NATIVE_TEMPLATE=1
      shift
      ;;
    --description)
      need_value "$1" "${2:-}"
      DESCRIPTION="$2"
      shift 2
      ;;
    --remote)
      need_value "$1" "${2:-}"
      REMOTE="$2"
      shift 2
      ;;
    --state-dir)
      need_value "$1" "${2:-}"
      STATE_DIR_INPUT="$2"
      shift 2
      ;;
    --registry)
      need_value "$1" "${2:-}"
      REGISTRY_INPUT="$2"
      shift 2
      ;;
    --read-root)
      need_value "$1" "${2:-}"
      reject_newline "--read-root" "$2"
      read_roots+=("$2")
      shift 2
      ;;
    --target)
      need_value "$1" "${2:-}"
      add_target_spec "$2"
      shift 2
      ;;
    --default-target)
      need_value "$1" "${2:-}"
      DEFAULT_TARGET_NAME="$2"
      shift 2
      ;;
    --no-default)
      NO_DEFAULT=1
      shift
      ;;
    --no-git)
      NO_GIT=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "unknown option: $1"
      ;;
  esac
done

reject_newline "name" "$NAME"
reject_newline "target repo" "$TARGET_REPO_INPUT"
reject_newline "description" "$DESCRIPTION"
reject_newline "remote" "$REMOTE"
reject_newline "default target" "$DEFAULT_TARGET_NAME"

if ! [[ "$NAME" =~ $NAME_REGEX ]]; then
  die "name must match $NAME_REGEX: $NAME"
fi

case "$MODE" in
  generic|native)
    ;;
  *)
    die "--mode must be generic or native: $MODE"
    ;;
esac

if [ "$INIT_NATIVE_TEMPLATE" -eq 1 ]; then
  if [ "$MODE_SET" -eq 0 ]; then
    MODE="native"
  elif [ "$MODE" != "native" ]; then
    die "--init-native-template requires --mode native"
  fi
fi

if [ "${#read_roots[@]}" -eq 0 ]; then
  read_roots+=("$DEFAULT_READ_ROOT")
fi

if [ "${#target_names[@]}" -eq 0 ]; then
  add_target_spec "$DEFAULT_TARGET_SPEC"
fi

if ! [[ "$DEFAULT_TARGET_NAME" =~ $TARGET_NAME_REGEX ]]; then
  die "default target must match $TARGET_NAME_REGEX: $DEFAULT_TARGET_NAME"
fi

if ! target_seen "$DEFAULT_TARGET_NAME"; then
  die "default target is not configured: $DEFAULT_TARGET_NAME"
fi

if [ -z "$STATE_DIR_INPUT" ]; then
  STATE_DIR_INPUT="$HOME/.local/state/loreforge/$NAME"
fi

TARGET_REPO="$(absolute_path "$TARGET_REPO_INPUT")"
STATE_DIR="$(absolute_path "$STATE_DIR_INPUT")"
REGISTRY="$(absolute_path "$REGISTRY_INPUT")"

if [ "$MODE" = "generic" ]; then
  if [ -e "$TARGET_REPO" ] && [ ! -d "$TARGET_REPO" ]; then
    die "target repo exists but is not a directory: $TARGET_REPO"
  fi
  mkdir -p "$TARGET_REPO"
elif [ "$INIT_NATIVE_TEMPLATE" -eq 1 ]; then
  init_native_template
elif [ ! -d "$TARGET_REPO" ]; then
  die "native target repo does not exist; use --init-native-template to create it: $TARGET_REPO"
fi

validate_read_roots
ensure_target_dirs
write_state
update_registry

printf 'Binding "%s" written to %s\n' "$NAME" "$REGISTRY"

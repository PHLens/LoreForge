#!/usr/bin/env bash
# Read-only protocol health check for a LoreForge binding.
set -euo pipefail

DEFAULT_REGISTRY="${LOREFORGE_REGISTRY:-$HOME/.config/loreforge/registry.toml}"

usage() {
  cat <<'EOF'
Usage:
  lint-protocol.sh [--registry PATH] [binding-name]
EOF
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

resolve_from_base() {
  local base="$1"
  local path="$2"

  case "$path" in
    /*)
      absolute_path "$path"
      ;;
    *)
      absolute_path "$base/$path"
      ;;
  esac
}

path_inside_root() {
  local root="$1"
  local path="$2"

  if [ "$root" = "/" ]; then
    [[ "$path" == /* ]]
    return
  fi

  [ "$path" = "$root" ] || [[ "$path" == "$root/"* ]]
}

registry_default() {
  local registry="$1"

  awk '
    function trim(value) {
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
      return value
    }

    function unquote(value) {
      value = trim(value)
      if (value ~ /^".*"$/) {
        sub(/^"/, "", value)
        sub(/"$/, "", value)
        gsub(/\\"/, "\"", value)
        gsub(/\\\\/, "\\", value)
      }
      return value
    }

    /^[[:space:]]*#/ || /^[[:space:]]*$/ { next }
    /^[[:space:]]*\[/ { exit }
    /^[[:space:]]*default[[:space:]]*=/ {
      sub(/^[^=]*=[[:space:]]*/, "", $0)
      print unquote($0)
      exit
    }
  ' "$registry"
}

parse_registry() {
  local registry="$1"
  local wanted="$2"

  awk -v wanted="$wanted" '
    function trim(value) {
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
      return value
    }

    function unquote(value) {
      value = trim(value)
      if (value ~ /^".*"$/) {
        sub(/^"/, "", value)
        sub(/"$/, "", value)
        gsub(/\\"/, "\"", value)
        gsub(/\\\\/, "\\", value)
      }
      return value
    }

    function key_name(line) {
      sub(/[[:space:]]*=.*/, "", line)
      return trim(line)
    }

    function value_after_equals(line) {
      sub(/^[^=]*=[[:space:]]*/, "", line)
      return trim(line)
    }

    function emit_read_roots(value, body, parts, count, idx, item) {
      body = trim(value)
      sub(/^\[/, "", body)
      sub(/\]$/, "", body)
      count = split(body, parts, ",")
      for (idx = 1; idx <= count; idx++) {
        item = unquote(parts[idx])
        if (item != "") {
          printf "read_root\t\t%s\n", item
        }
      }
    }

    /^[[:space:]]*#/ || /^[[:space:]]*$/ { next }

    /^[[:space:]]*\[\[bindings\]\][[:space:]]*$/ {
      in_binding = 1
      selected = 0
      section = "binding"
      target_name = ""
      next
    }

    in_binding && /^[[:space:]]*\[bindings\.targets\.[A-Za-z0-9_-]+\][[:space:]]*$/ {
      section = "target"
      target_name = $0
      sub(/^[[:space:]]*\[bindings\.targets\./, "", target_name)
      sub(/\][[:space:]]*$/, "", target_name)
      next
    }

    in_binding && /^[[:space:]]*\[bindings\.[^]]+\][[:space:]]*$/ {
      section = "other"
      target_name = ""
      next
    }

    /^[[:space:]]*\[/ {
      in_binding = 0
      selected = 0
      section = ""
      target_name = ""
      next
    }

    in_binding && /^[[:space:]]*[A-Za-z0-9_-]+[[:space:]]*=/ {
      key = key_name($0)
      value = value_after_equals($0)

      if (section == "binding") {
        value = unquote(value)
        if (key == "name") {
          if (value == wanted) {
            selected = 1
            printf "binding\tname\t%s\n", value
          } else {
            selected = 0
          }
          next
        }

        if (selected) {
          if (key == "read_roots") {
            emit_read_roots(value)
          } else {
            printf "binding\t%s\t%s\n", key, value
          }
        }
        next
      }

      if (selected && section == "target" && key == "path") {
        printf "target\t%s\t%s\n", target_name, unquote(value)
      }
    }
  ' "$registry"
}

parse_manifest() {
  local manifest="$1"

  awk '
    function trim(value) {
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
      return value
    }

    function unquote(value) {
      value = trim(value)
      if (value ~ /^".*"$/) {
        sub(/^"/, "", value)
        sub(/"$/, "", value)
        gsub(/\\"/, "\"", value)
        gsub(/\\\\/, "\\", value)
      }
      return value
    }

    function key_name(line) {
      sub(/[[:space:]]*=.*/, "", line)
      return trim(line)
    }

    function value_after_equals(line) {
      sub(/^[^=]*=[[:space:]]*/, "", line)
      return unquote(line)
    }

    /^[[:space:]]*#/ || /^[[:space:]]*$/ { next }

    /^[[:space:]]*\[\[outputs\]\][[:space:]]*$/ {
      output_index++
      section = "output"
      printf "output_start\t%d\t\n", output_index
      next
    }

    /^[[:space:]]*\[\[[^]]+\]\][[:space:]]*$/ {
      section = "other"
      next
    }

    /^[[:space:]]*\[[^]]+\][[:space:]]*$/ {
      section = "other"
      next
    }

    /^[[:space:]]*[A-Za-z0-9_-]+[[:space:]]*=/ {
      key = key_name($0)
      value = value_after_equals($0)

      if (section == "output") {
        printf "output\t%d.%s\t%s\n", output_index, key, value
      } else if (section == "") {
        printf "field\t%s\t%s\n", key, value
      }
    }
  ' "$manifest"
}

field_value() {
  local name="$1"

  case "$name" in
    type)
      printf '%s\n' "$manifest_type"
      ;;
    status)
      printf '%s\n' "$manifest_status"
      ;;
    binding)
      printf '%s\n' "$manifest_binding"
      ;;
    created_at)
      printf '%s\n' "$manifest_created_at"
      ;;
  esac
}

target_path_for() {
  local wanted="$1"
  local index

  for index in "${!target_names[@]}"; do
    if [ "${target_names[$index]}" = "$wanted" ]; then
      printf '%s\n' "${target_paths[$index]}"
      return 0
    fi
  done

  return 1
}

binding_issue() {
  printf '  - %s\n' "$*"
  binding_issues=$((binding_issues + 1))
}

runtime_issue() {
  printf '  - %s\n' "$*"
  runtime_issues=$((runtime_issues + 1))
}

package_issue() {
  printf '  - %s\n' "$*"
  package_issues=$((package_issues + 1))
}

validate_manifest() {
  local manifest="$1"
  local package_dir="$2"
  local package_root_type="$3"
  local record_type
  local key
  local value
  local output_index
  local output_field
  local required
  local target_path
  local target_base
  local output_abs
  local candidate_abs
  local patch_abs
  local index

  manifest_type=""
  manifest_status=""
  manifest_binding=""
  manifest_created_at=""

  local -a output_indices=()
  local -a output_kind=()
  local -a output_target=()
  local -a output_path=()
  local -a output_mode=()
  local -a output_candidate=()
  local -a output_patch=()

  while IFS=$'\t' read -r record_type key value; do
    [ -n "$record_type" ] || continue
    case "$record_type" in
      field)
        case "$key" in
          type)
            manifest_type="$value"
            ;;
          status)
            manifest_status="$value"
            ;;
          binding)
            manifest_binding="$value"
            ;;
          created_at)
            manifest_created_at="$value"
            ;;
        esac
        ;;
      output_start)
        output_indices+=("$key")
        ;;
      output)
        output_index="${key%%.*}"
        output_field="${key#*.}"
        case "$output_field" in
          kind)
            output_kind[$output_index]="$value"
            ;;
          target)
            output_target[$output_index]="$value"
            ;;
          path)
            output_path[$output_index]="$value"
            ;;
          mode)
            output_mode[$output_index]="$value"
            ;;
          candidate)
            output_candidate[$output_index]="$value"
            ;;
          patch)
            output_patch[$output_index]="$value"
            ;;
        esac
        ;;
    esac
  done < <(parse_manifest "$manifest")

  for required in type status binding created_at; do
    if [ -z "$(field_value "$required")" ]; then
      package_issue "invalid manifest: $manifest missing or empty $required"
    fi
  done

  if [ -n "$manifest_type" ] && [ "$manifest_type" != "$package_root_type" ]; then
    package_issue "invalid manifest: $manifest type $manifest_type does not match $package_root_type package root"
  fi

  if [ -n "$manifest_binding" ] && [ "$manifest_binding" != "$binding_name" ]; then
    package_issue "invalid manifest: $manifest binding $manifest_binding does not match $binding_name"
  fi

  for index in "${output_indices[@]}"; do
    if [ -z "${output_kind[$index]:-}" ]; then
      package_issue "invalid manifest: $manifest output $index missing or empty kind"
    fi
    if [ -z "${output_target[$index]:-}" ]; then
      package_issue "invalid manifest: $manifest output $index missing or empty target"
    fi
    if [ -z "${output_path[$index]:-}" ]; then
      package_issue "invalid manifest: $manifest output $index missing or empty path"
    fi
    if [ -z "${output_mode[$index]:-}" ]; then
      package_issue "invalid manifest: $manifest output $index missing or empty mode"
    fi
    if [ -z "${output_candidate[$index]:-}" ] && [ -z "${output_patch[$index]:-}" ]; then
      package_issue "invalid manifest: $manifest output $index missing candidate or patch"
    fi

    if [ "${output_kind[$index]:-}" = "file" ] && [ -z "${output_candidate[$index]:-}" ]; then
      package_issue "invalid manifest: $manifest file output $index missing candidate"
    fi
    if [ "${output_kind[$index]:-}" = "patch" ] && [ -z "${output_patch[$index]:-}" ]; then
      package_issue "invalid manifest: $manifest patch output $index missing patch"
    fi

    if [ -n "${output_target[$index]:-}" ]; then
      if ! target_path="$(target_path_for "${output_target[$index]}")"; then
        package_issue "invalid manifest: $manifest output $index target not configured: ${output_target[$index]}"
      elif [ -n "${output_path[$index]:-}" ]; then
        target_base="$(resolve_from_base "$target_repo_abs" "$target_path")"
        output_abs="$(resolve_from_base "$target_base" "${output_path[$index]}")"
        if ! path_inside_root "$target_base" "$output_abs"; then
          package_issue "invalid manifest: $manifest output path escapes target: ${output_path[$index]}"
        elif [ "${output_mode[$index]:-}" = "create" ] && [ -e "$output_abs" ]; then
          package_issue "invalid manifest: $manifest create output already exists: ${output_path[$index]}"
        fi
      fi
    fi

    if [ -n "${output_candidate[$index]:-}" ]; then
      candidate_abs="$(resolve_from_base "$package_dir" "${output_candidate[$index]}")"
      if ! path_inside_root "$package_dir" "$candidate_abs"; then
        package_issue "invalid manifest: $manifest candidate path escapes package: ${output_candidate[$index]}"
      elif [ ! -f "$candidate_abs" ]; then
        package_issue "invalid manifest: $manifest candidate file missing: ${output_candidate[$index]}"
      fi
    fi

    if [ -n "${output_patch[$index]:-}" ]; then
      patch_abs="$(resolve_from_base "$package_dir" "${output_patch[$index]}")"
      if ! path_inside_root "$package_dir" "$patch_abs"; then
        package_issue "invalid manifest: $manifest patch path escapes package: ${output_patch[$index]}"
      elif [ ! -f "$patch_abs" ]; then
        package_issue "invalid manifest: $manifest patch file missing: ${output_patch[$index]}"
      fi
    fi
  done
}

registry="$DEFAULT_REGISTRY"
binding_arg=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --registry)
      if [ -z "${2:-}" ]; then
        usage >&2
        exit 1
      fi
      registry="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --*)
      usage >&2
      exit 1
      ;;
    *)
      if [ -n "$binding_arg" ]; then
        usage >&2
        exit 1
      fi
      binding_arg="$1"
      shift
      ;;
  esac
done

registry="$(absolute_path "$registry")"
binding_name="$binding_arg"
if [ -z "$binding_name" ] && [ -f "$registry" ]; then
  binding_name="$(registry_default "$registry" || true)"
fi

binding_label="${binding_name:-<unspecified>}"

binding_found=0
target_repo=""
state_dir=""
target_repo_abs=""
state_dir_abs=""
read_roots=()
target_names=()
target_paths=()

if [ -f "$registry" ] && [ -n "$binding_name" ]; then
  while IFS=$'\t' read -r record_type key value; do
    [ -n "$record_type" ] || continue
    case "$record_type" in
      binding)
        if [ "$key" = "name" ]; then
          binding_found=1
        elif [ "$key" = "target_repo" ]; then
          target_repo="$value"
        elif [ "$key" = "state_dir" ]; then
          state_dir="$value"
        fi
        ;;
      read_root)
        read_roots+=("$value")
        ;;
      target)
        target_names+=("$key")
        target_paths+=("$value")
        ;;
    esac
  done < <(parse_registry "$registry" "$binding_name")
fi

if [ -n "$target_repo" ]; then
  target_repo_abs="$(absolute_path "$target_repo")"
fi
if [ -n "$state_dir" ]; then
  state_dir_abs="$(absolute_path "$state_dir")"
fi

echo "=== LoreForge Protocol Lint Report: $binding_label ==="
echo ""

echo "## Binding"
binding_issues=0
if [ ! -f "$registry" ]; then
  binding_issue "missing registry: $registry"
elif [ -z "$binding_name" ]; then
  binding_issue "missing binding: no binding-name provided and registry default is unset"
elif [ "$binding_found" -eq 0 ]; then
  binding_issue "missing binding: $binding_name"
else
  if [ -z "$target_repo" ]; then
    binding_issue "missing target_repo for binding: $binding_name"
  elif [ ! -d "$target_repo_abs" ]; then
    binding_issue "target_repo is not a directory: $target_repo"
  fi

  if [ -z "$state_dir" ]; then
    binding_issue "missing state_dir for binding: $binding_name"
  elif [ ! -d "$state_dir_abs" ]; then
    binding_issue "state_dir is not a directory: $state_dir"
  fi

  if [ -n "$target_repo_abs" ]; then
    for read_root in "${read_roots[@]}"; do
      read_root_abs="$(resolve_from_base "$target_repo_abs" "$read_root")"
      if ! path_inside_root "$target_repo_abs" "$read_root_abs"; then
        binding_issue "read_root escapes target_repo: $read_root"
      fi
    done

    for target_path in "${target_paths[@]}"; do
      target_abs="$(resolve_from_base "$target_repo_abs" "$target_path")"
      if ! path_inside_root "$target_repo_abs" "$target_abs"; then
        binding_issue "target path escapes target_repo: $target_path"
      fi
    done
  fi
fi
echo "  Binding issues: $binding_issues"
echo ""

echo "## Runtime State"
runtime_issues=0
if [ "$binding_found" -eq 1 ] && [ -n "$state_dir_abs" ] && [ -d "$state_dir_abs" ]; then
  for required_dir in packages/ingest packages/writeback packages/archive reports cache locks tmp; do
    if [ ! -d "$state_dir_abs/$required_dir" ]; then
      runtime_issue "missing runtime dir: $required_dir"
    fi
  done
fi
echo "  Runtime issues: $runtime_issues"
echo ""

echo "## Packages"
package_issues=0
if [ "$binding_found" -eq 1 ] && [ -n "$target_repo_abs" ] && [ -d "$target_repo_abs" ] && [ -n "$state_dir_abs" ] && [ -d "$state_dir_abs" ]; then
  for package_root_type in ingest writeback; do
    package_root="$state_dir_abs/packages/$package_root_type"
    [ -d "$package_root" ] || continue
    while IFS= read -r -d '' manifest; do
      package_dir="$(dirname "$manifest")"
      validate_manifest "$manifest" "$package_dir" "$package_root_type"
    done < <(find "$package_root" -mindepth 2 -maxdepth 2 -type f -name manifest.toml -print0 2>/dev/null | sort -z)
  done
fi
echo "  Package issues: $package_issues"
echo ""

echo "=== Protocol Lint Complete ==="

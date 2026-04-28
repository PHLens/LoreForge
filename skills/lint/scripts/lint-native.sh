#!/usr/bin/env bash
# Read-only native structure health check for a LoreForge native repo.
# Usage: bash lint-native.sh [wiki_path]
set -euo pipefail

VAULT="${1:-.}"
cd "$VAULT"
VAULT_ROOT="$(pwd -P)"

CONFIG=".loreforge/wiki.toml"

absolute_path() {
  local path="$1"

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

path_inside_root() {
  local root="$1"
  local path="$2"

  [ "$path" = "$root" ] || [[ "$path" == "$root/"* ]]
}

toml_get() {
  local section="$1"
  local key="$2"
  local fallback="$3"

  if [ ! -f "$CONFIG" ]; then
    printf '%s\n' "$fallback"
    return
  fi

  local value
  if [ -z "$section" ]; then
    value="$(
      awk -v key="$key" '
        /^[[:space:]]*\[/ { exit }
        $0 ~ "^[[:space:]]*" key "[[:space:]]*=" {
          sub(/^[^=]*=[[:space:]]*/, "", $0)
          gsub(/^[[:space:]]*"|"[[:space:]]*$/, "", $0)
          print
          exit
        }
      ' "$CONFIG"
    )"
  else
    value="$(
      awk -v section="$section" -v key="$key" '
        $0 ~ "^[[:space:]]*\\[" section "\\][[:space:]]*$" { in_section=1; next }
        /^[[:space:]]*\[/ && in_section { exit }
        in_section && $0 ~ "^[[:space:]]*" key "[[:space:]]*=" {
          sub(/^[^=]*=[[:space:]]*/, "", $0)
          gsub(/^[[:space:]]*"|"[[:space:]]*$/, "", $0)
          print
          exit
        }
      ' "$CONFIG"
    )"
  fi

  printf '%s\n' "${value:-$fallback}"
}

toml_section_values() {
  local section="$1"

  if [ ! -f "$CONFIG" ]; then
    return
  fi

  awk -v section="$section" '
    $0 ~ "^[[:space:]]*\\[" section "\\][[:space:]]*$" { in_section=1; next }
    /^[[:space:]]*\[/ && in_section { exit }
    in_section && /^[[:space:]]*[A-Za-z0-9_-]+[[:space:]]*=/ {
      sub(/^[^=]*=[[:space:]]*/, "", $0)
      gsub(/^[[:space:]]*"|"[[:space:]]*$/, "", $0)
      print
    }
  ' "$CONFIG"
}

has_file_named() {
  local title="$1"
  local path_title="${title%.md}"
  local base
  base="$(basename "$path_title")"

  [ -f "${path_title}.md" ] && return 0
  find . -type f -name "${base}.md" -print -quit 2>/dev/null | grep -q .
}

is_attachment_link() {
  local link="$1"
  [[ "$link" =~ \.(png|jpg|jpeg|gif|svg|webp|pdf|mp4|mp3|wav|zip|tar|gz)$ ]]
}

markdown_without_fenced_code() {
  while IFS= read -r -d '' md_file; do
    awk '
      /^```/ { in_code = !in_code; next }
      !in_code { print }
    ' "$md_file"
  done < <(find . -name "*.md" -type f -print0 2>/dev/null)
}

frontmatter_text() {
  local file="$1"
  awk '
    NR == 1 && $0 == "---" { in_frontmatter = 1; next }
    in_frontmatter && $0 == "---" { exit }
    in_frontmatter { print }
  ' "$file"
}

manifest_field() {
  local file="$1"
  local key="$2"
  frontmatter_text "$file" | awk -v key="$key" '
    $0 ~ "^[[:space:]]*" key ":[[:space:]]*" {
      sub(/^[^:]*:[[:space:]]*/, "", $0)
      gsub(/^[[:space:]]*"|"[[:space:]]*$/, "", $0)
      print
      exit
    }
  '
}

manifest_section() {
  local file="$1"
  local section="$2"
  frontmatter_text "$file" | awk -v section="$section" '
    $0 ~ "^[[:space:]]*" section ":[[:space:]]*$" { in_section = 1; next }
    in_section && $0 ~ "^[A-Za-z0-9_-]+:[[:space:]]*" { exit }
    in_section { print }
  '
}

section_list_items() {
  local file="$1"
  local section="$2"
  manifest_section "$file" "$section" | awk '
    /^[[:space:]]*-[[:space:]]+/ {
      line=$0
      sub(/^[[:space:]]*-[[:space:]]*/, "", line)
      print line
    }
  '
}

section_has_items() {
  local file="$1"
  local section="$2"
  section_list_items "$file" "$section" | grep -q .
}

has_frontmatter() {
  local file="$1"
  head -n 1 "$file" | grep -qx -- '---'
}

frontmatter_value() {
  local file="$1"
  local key="$2"
  frontmatter_text "$file" | awk -v key="$key" '
    $0 ~ "^[[:space:]]*" key ":[[:space:]]*" {
      sub(/^[^:]*:[[:space:]]*/, "", $0)
      gsub(/^[[:space:]]*"|"[[:space:]]*$/, "", $0)
      print
      exit
    }
  '
}

has_nonempty_up() {
  local file="$1"
  local up_value
  up_value="$(frontmatter_value "$file" "up")"
  if [ -n "$up_value" ] && [ "$up_value" != '""' ]; then
    return 0
  fi
  rg '^up::[[:space:]]*.' "$file" >/dev/null 2>&1
}

has_x_links() {
  local file="$1"
  rg '^X::[[:space:]]*\[\[' "$file" >/dev/null 2>&1
}

stable_note_paths() {
  find "$CARDS_DIR" "$MOCS_DIR" -type f -name "*.md" 2>/dev/null \
    ! -name "README.md" \
    ! -path "$INDEX_FILE" \
    ! -path "$LOG_FILE"
}

has_semantic_inbound() {
  local card="$1"
  local title="$2"
  while IFS= read -r note; do
    [ -z "$note" ] && continue
    [ "$note" = "$card" ] && continue
    if rg -F "[[$title" "$note" >/dev/null 2>&1; then
      return 0
    fi
  done < <(stable_note_paths)
  return 1
}

validate_manifest() {
  local manifest="$1"
  local expected_type="$2"
  local issues=0
  local package_dir
  local package_root

  package_dir="$(dirname "$manifest")"
  package_root="$(absolute_path "$package_dir")"

  if ! has_frontmatter "$manifest"; then
    echo "  - invalid manifest: $manifest missing frontmatter"
    MANIFEST_ISSUES=1
    return
  fi

  local type
  local status
  local value
  for field in type source_type status created promotion_reason; do
    value="$(manifest_field "$manifest" "$field")"
    if [ -z "$value" ]; then
      echo "  - invalid manifest: $manifest missing or empty $field"
      issues=$((issues + 1))
    fi
  done

  type="$(manifest_field "$manifest" "type")"
  if [ -n "$type" ] && [ "$type" != "ingest" ] && [ "$type" != "writeback" ]; then
    echo "  - invalid manifest: $manifest type must be ingest or writeback"
    issues=$((issues + 1))
  fi
  if [ -n "$expected_type" ] && [ -n "$type" ] && [ "$type" != "$expected_type" ]; then
    echo "  - invalid manifest: $manifest type $type does not match $expected_type package root"
    issues=$((issues + 1))
  fi

  status="$(manifest_field "$manifest" "status")"
  if [ -n "$status" ] && [ "$status" != "staged" ]; then
    echo "  - invalid manifest: $manifest status must be staged"
    issues=$((issues + 1))
  fi

  for section in provenance candidate_notes; do
    if ! section_has_items "$manifest" "$section"; then
      echo "  - invalid manifest: $manifest $section must include at least one item"
      issues=$((issues + 1))
    fi
  done

  local candidate_notes
  local updates
  local candidate
  local candidate_abs
  local update
  local update_abs
  candidate_notes="$(section_list_items "$manifest" "candidate_notes" || true)"
  updates="$(section_list_items "$manifest" "updates" || true)"

  if printf '%s\n' "$candidate_notes" | rg '(^|[[:space:]])path:' >/dev/null 2>&1; then
    echo "  - invalid manifest: $manifest candidate_notes must be simple path list items, not path/kind objects"
    issues=$((issues + 1))
  fi
  if printf '%s\n' "$candidate_notes" | rg '(^|[[:space:]])kind:' >/dev/null 2>&1; then
    echo "  - invalid manifest: $manifest candidate_notes must not use kind objects"
    issues=$((issues + 1))
  fi

  while IFS= read -r candidate; do
    [ -z "$candidate" ] && continue
    case "$candidate" in
      /*)
        echo "  - invalid manifest: $manifest candidate path must be package-relative: $candidate"
        issues=$((issues + 1))
        continue
        ;;
    esac
    case "$candidate" in
      Cards/*|Sources/*|MOCs/*)
        ;;
      *)
        echo "  - invalid manifest: $manifest candidate path must start with Cards/, Sources/, or MOCs/: $candidate"
        issues=$((issues + 1))
        ;;
    esac
    candidate_abs="$(absolute_path "$package_dir/$candidate")"
    if ! path_inside_root "$package_root" "$candidate_abs"; then
      echo "  - invalid manifest: $manifest candidate path escapes package: $candidate"
      issues=$((issues + 1))
    elif [ ! -f "$candidate_abs" ]; then
      echo "  - invalid manifest: $manifest candidate file missing: $candidate"
      issues=$((issues + 1))
    fi
  done <<< "$candidate_notes"

  while IFS= read -r update; do
    [ -z "$update" ] && continue
    case "$update" in
      /*)
        echo "  - invalid manifest: $manifest update path must be target-repo-relative: $update"
        issues=$((issues + 1))
        continue
        ;;
    esac
    update_abs="$(absolute_path "$VAULT_ROOT/$update")"
    if ! path_inside_root "$VAULT_ROOT" "$update_abs"; then
      echo "  - invalid manifest: $manifest update path escapes target repo: $update"
      issues=$((issues + 1))
    fi
  done <<< "$updates"

  if printf '%s\n' "$candidate_notes" | rg -q "^${CARDS_DIR}/|^Cards/"; then
    if ! printf '%s\n' "$updates" | grep -Fxq "$INDEX_FILE"; then
      echo "  - invalid manifest: $manifest card candidates require $INDEX_FILE in updates"
      issues=$((issues + 1))
    fi
  else
    if [ -z "$updates" ]; then
      :
    fi
  fi

  MANIFEST_ISSUES="$issues"
}

AGENTS_FILE="$(toml_get "" "agents_file" "AGENTS.md")"
VAULT_MAP="$(toml_get "" "vault_map" "00_System/Vault Map.md")"
SCHEMA_FILE="$(toml_get "" "schema_file" "00_System/Schema.md")"
INDEX_FILE="$(toml_get "" "index_file" "00_System/+Wiki Index.md")"
LOG_FILE="$(toml_get "" "log_file" "00_System/Wiki Log.md")"
VIEWS_DIR="$(toml_get "" "views_dir" "00_System/Views")"
INBOX_DIR="$(toml_get "paths" "inbox" "10_Inbox")"
INGEST_DIR="$(toml_get "paths" "ingest" "${INBOX_DIR}/ingest")"
WRITEBACK_DIR="$(toml_get "paths" "writeback" "${INBOX_DIR}/writeback")"
CARDS_DIR="$(toml_get "paths" "cards" "Cards")"
SOURCES_DIR="$(toml_get "paths" "sources" "Sources")"
MOCS_DIR="$(toml_get "paths" "mocs" "MOCs")"
ARCHIVE_DIR="$(toml_get "paths" "archive" "Archive")"

echo "=== LoreForge Native Lint Report: $(basename "$(pwd)") ==="
echo ""

echo "## 1. Discovery Health"
discovery_issues=0
for required in "$CONFIG" "$AGENTS_FILE" "$VAULT_MAP" "$SCHEMA_FILE" "$INDEX_FILE" "$LOG_FILE" "$VIEWS_DIR"; do
  if [ ! -e "$required" ]; then
    echo "  - missing: $required"
    discovery_issues=$((discovery_issues + 1))
  fi
done

view_values="$(toml_section_values "views" || true)"
if [ -z "$view_values" ] && [ -d "$VIEWS_DIR" ]; then
  view_values="$(find "$VIEWS_DIR" -maxdepth 1 -type f -name "*.md" -print 2>/dev/null || true)"
fi
while IFS= read -r view_file; do
  [ -z "$view_file" ] && continue
  if [ ! -f "$view_file" ]; then
    echo "  - missing view: $view_file"
    discovery_issues=$((discovery_issues + 1))
  fi
done <<< "$view_values"
echo "  Count: $discovery_issues"
echo ""

echo "## 2. Type-First Structure"
structure_issues=0
for required_dir in "$INBOX_DIR" "$INGEST_DIR" "$WRITEBACK_DIR" "$CARDS_DIR" "$SOURCES_DIR" "$MOCS_DIR" "$ARCHIVE_DIR"; do
  if [ ! -d "$required_dir" ]; then
    echo "  - missing dir: $required_dir"
    structure_issues=$((structure_issues + 1))
  fi
done
echo "  Count: $structure_issues"
echo ""

echo "## 3. Unresolved Links"
unresolved=0
links="$(
  markdown_without_fenced_code \
    | rg -o '\[\[[^\]]+\]\]' 2>/dev/null \
    | sed 's/^\[\[//;s/\]\]$//;s/[|#].*$//' \
    | sort -u || true
)"
while IFS= read -r link; do
  [ -z "$link" ] && continue
  is_attachment_link "$link" && continue
  if ! has_file_named "$link"; then
    echo "  - [[$link]]"
    unresolved=$((unresolved + 1))
  fi
done <<< "$links"
echo "  Count: $unresolved"
echo ""

echo "## 4. Duplicate/Near-Duplicate Titles"
dupes=0
duplicate_groups="$(
  find . -name "*.md" -type f ! -name "README.md" ! -name "+Wiki Index.md" -printf "%f\t%p\n" 2>/dev/null \
    | awk -F '\t' '$1 != "manifest.md" { print }' \
    | awk -F '\t' '
      {
        title=$1
        sub(/\.md$/, "", title)
        norm=tolower(title)
        gsub(/[ _-]+/, "", norm)
        paths[norm]=paths[norm] "  - " $2 "\n"
        counts[norm]++
      }
      END {
        for (norm in counts) {
          if (counts[norm] > 1) {
            print paths[norm]
          }
        }
      }
    ' || true
)"
if [ -n "$duplicate_groups" ]; then
  printf '%s\n' "$duplicate_groups"
  dupes="$(printf '%s\n' "$duplicate_groups" | grep -c '^  - ' || true)"
fi
echo "  Count: $dupes files in duplicate groups"
echo ""

echo "## 5. Staged Material"
staged=0
package_issues=0
if [ -d "$INBOX_DIR" ]; then
  staged="$(find "$INBOX_DIR" -type f -name "*.md" ! -name "README.md" 2>/dev/null | wc -l | tr -d ' ')"
  echo "  Inbox: $INBOX_DIR"
  if [ "$staged" -gt 0 ]; then
    find "$INBOX_DIR" -type f -name "*.md" ! -name "README.md" -printf "  - %p\n" 2>/dev/null | head -20
  fi
  for package_root in "$INGEST_DIR" "$WRITEBACK_DIR"; do
    if [ -d "$package_root" ]; then
      while IFS= read -r -d '' package_dir; do
        expected_type="writeback"
        if [ "$package_root" = "$INGEST_DIR" ]; then
          expected_type="ingest"
        fi
        if [ ! -f "$package_dir/manifest.md" ]; then
          echo "  - staged package missing manifest: $package_dir"
          package_issues=$((package_issues + 1))
        else
          validate_manifest "$package_dir/manifest.md" "$expected_type"
          package_issues=$((package_issues + MANIFEST_ISSUES))
        fi
      done < <(find "$package_root" -mindepth 1 -maxdepth 1 -type d -print0 2>/dev/null)
    fi
  done
else
  echo "  - missing inbox dir: $INBOX_DIR"
  staged=1
fi
echo "  Count: $staged"
echo "  Package issues: $package_issues"
echo ""

echo "## 6. Flat Cards"
flat_card_issues=0
if [ -d "$CARDS_DIR" ]; then
  while IFS= read -r nested_card; do
    [ -z "$nested_card" ] && continue
    [ "$(basename "$nested_card")" = "README.md" ] && continue
    echo "  - nested card: $nested_card"
    flat_card_issues=$((flat_card_issues + 1))
  done < <(find "$CARDS_DIR" -mindepth 2 -type f -name "*.md" 2>/dev/null)
fi
echo "  Count: $flat_card_issues"
echo ""

echo "## 7. Card Discoverability"
integrated=0
index_only=0
unindexed=0
orphan=0
stale_index=0

if [ -d "$CARDS_DIR" ]; then
  while IFS= read -r -d '' card; do
    [ "$(basename "$card")" = "README.md" ] && continue
    title="$(basename "$card" .md)"
    indexed=""
    if [ -f "$INDEX_FILE" ] && rg -F "[[$title" "$INDEX_FILE" >/dev/null 2>&1; then
      indexed=1
    fi
    semantic=""
    if has_nonempty_up "$card" || has_x_links "$card" || has_semantic_inbound "$card" "$title"; then
      semantic=1
    fi

    if [ -n "$indexed" ] && [ -n "$semantic" ]; then
      integrated=$((integrated + 1))
    elif [ -n "$indexed" ]; then
      echo "  - index-only: $card"
      index_only=$((index_only + 1))
    elif [ -n "$semantic" ]; then
      echo "  - unindexed: $card"
      unindexed=$((unindexed + 1))
    else
      echo "  - orphan: $card"
      orphan=$((orphan + 1))
    fi
  done < <(find "$CARDS_DIR" -maxdepth 1 -type f -name "*.md" -print0 2>/dev/null)
fi

if [ -f "$INDEX_FILE" ]; then
  index_links="$(
    awk '/^## Optional MOC Pointers/ { exit } { print }' "$INDEX_FILE" \
      | rg -o '\[\[[^\]]+\]\]' 2>/dev/null \
      | sed 's/^\[\[//;s/\]\]$//;s/[|#].*$//' \
      | sort -u || true
  )"
  while IFS= read -r index_link; do
    [ -z "$index_link" ] && continue
    if ! has_file_named "$index_link"; then
      echo "  - stale index: [[$index_link]]"
      stale_index=$((stale_index + 1))
    fi
  done <<< "$index_links"
fi

echo "  Integrated: $integrated"
echo "  Index-only warnings: $index_only"
echo "  Unindexed errors: $unindexed"
echo "  Orphan errors: $orphan"
echo "  Stale index errors: $stale_index"
echo ""

echo "## 8. Source Reference Health"
source_warnings=0
if [ -d "$SOURCES_DIR" ]; then
  while IFS= read -r -d '' source_note; do
    [ "$(basename "$source_note")" = "README.md" ] && continue
    title="$(basename "$source_note" .md)"
    linked_from_stable="$(rg -F -l "[[$title" "$CARDS_DIR" "$MOCS_DIR" 2>/dev/null | head -1 || true)"
    linked_from_provenance="$(rg -F -l "$source_note" "$INBOX_DIR" "$ARCHIVE_DIR" "$LOG_FILE" 2>/dev/null | head -1 || true)"
    if [ -z "$linked_from_stable" ] && [ -z "$linked_from_provenance" ]; then
      echo "  - unreferenced source: $source_note"
      source_warnings=$((source_warnings + 1))
    fi
  done < <(find "$SOURCES_DIR" -type f -name "*.md" -print0 2>/dev/null)
fi
echo "  Warnings: $source_warnings"
echo ""

echo "## 9. Metadata Drift"
drift=0
empty_tags="$(rg -o '#[A-Za-z0-9_-]*/' --type md --no-filename . 2>/dev/null | sort -u || true)"
while IFS= read -r tag; do
  [ -z "$tag" ] && continue
  echo "  - empty sub-tag: $tag"
  drift=$((drift + 1))
done <<< "$empty_tags"

for note_dir in "$CARDS_DIR" "$MOCS_DIR" "$SOURCES_DIR"; do
  [ -d "$note_dir" ] || continue
  while IFS= read -r -d '' note; do
    [ "$(basename "$note")" = "README.md" ] && continue
    case "$note" in
      "$INDEX_FILE"|"$LOG_FILE"|"$VAULT_MAP"|"$SCHEMA_FILE")
        continue
        ;;
    esac
    if ! has_frontmatter "$note"; then
      echo "  - stable note missing frontmatter: $note"
      drift=$((drift + 1))
      continue
    fi
    if [ -z "$(frontmatter_value "$note" "kind")" ]; then
      echo "  - stable note missing kind: $note"
      drift=$((drift + 1))
    fi
  done < <(find "$note_dir" -type f -name "*.md" -print0 2>/dev/null)
done
echo "  Count: $drift"
echo ""

echo "## Configured Paths"
echo "  agents: $AGENTS_FILE"
echo "  vault_map: $VAULT_MAP"
echo "  schema: $SCHEMA_FILE"
echo "  index: $INDEX_FILE"
echo "  log: $LOG_FILE"
echo "  views: $VIEWS_DIR"
echo "  inbox: $INBOX_DIR"
echo "  ingest: $INGEST_DIR"
echo "  writeback: $WRITEBACK_DIR"
echo "  cards: $CARDS_DIR"
echo "  sources: $SOURCES_DIR"
echo "  mocs: $MOCS_DIR"
echo "  archive: $ARCHIVE_DIR"
echo ""

echo "=== Native Lint Complete ==="

#!/usr/bin/env bash
# Read-only structural health check for a LoreForge wiki instance.
# Usage: bash lint-wiki.sh [wiki_path]
set -euo pipefail

VAULT="${1:-.}"
cd "$VAULT"

CONFIG=".loreforge/wiki.toml"

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

AGENTS_FILE="$(toml_get "" "agents_file" "AGENTS.md")"
VAULT_MAP="$(toml_get "" "vault_map" "00_System/Vault Map.md")"
SCHEMA_FILE="$(toml_get "" "schema_file" "00_System/Schema.md")"
LOG_FILE="$(toml_get "" "log_file" "00_System/Wiki Log.md")"
VIEWS_DIR="$(toml_get "" "views_dir" "00_System/Views")"
INBOX_DIR="$(toml_get "paths" "inbox" "10_Inbox")"
CAPTURE_DIR="$(toml_get "paths" "capture" "${INBOX_DIR}/capture")"
INGEST_DIR="$(toml_get "paths" "ingest" "${INBOX_DIR}/ingest")"
WRITEBACK_DIR="$(toml_get "paths" "writeback" "${INBOX_DIR}/writeback")"
DOMAINS_DIR="$(toml_get "paths" "domains" "20_Domains")"
SHARED_DIR="$(toml_get "paths" "shared" "30_Shared")"
ARCHIVE_DIR="$(toml_get "paths" "archive" "40_Archive")"

echo "=== LoreForge Lint Report: $(basename "$(pwd)") ==="
echo ""

echo "## 1. Discovery Health"
discovery_issues=0
for required in "$CONFIG" "$AGENTS_FILE" "$VAULT_MAP" "$SCHEMA_FILE" "$LOG_FILE" "$VIEWS_DIR"; do
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

echo "## 2. Domain Health"
domain_issues=0
if [ ! -d "$DOMAINS_DIR" ]; then
  echo "  - missing domains dir: $DOMAINS_DIR"
  domain_issues=$((domain_issues + 1))
else
  while IFS= read -r -d '' domain_dir; do
    domain_name="$(basename "$domain_dir")"
    map_count="$(find "$domain_dir" -maxdepth 1 -type f -name "* Map.md" 2>/dev/null | wc -l | tr -d ' ')"
    if [ "$map_count" -eq 0 ]; then
      echo "  - $domain_name: missing domain map (* Map.md)"
      domain_issues=$((domain_issues + 1))
    fi
    if [ ! -f "$domain_dir/+Wiki Index.md" ]; then
      echo "  - $domain_name: missing +Wiki Index.md"
      domain_issues=$((domain_issues + 1))
    fi
    for subdir in Cards Sources MOCs; do
      if [ ! -d "$domain_dir/$subdir" ]; then
        echo "  - $domain_name: missing $subdir/"
        domain_issues=$((domain_issues + 1))
      fi
    done
  done < <(find "$DOMAINS_DIR" -mindepth 1 -maxdepth 1 -type d -print0 2>/dev/null)
fi
echo "  Count: $domain_issues"
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
        if [ ! -f "$package_dir/manifest.md" ]; then
          echo "  - staged package missing manifest: $package_dir"
          package_issues=$((package_issues + 1))
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

echo "## 6. Card Discoverability"
undiscoverable=0
if [ -d "$DOMAINS_DIR" ]; then
  while IFS= read -r -d '' card; do
    [ "$(basename "$card")" = "README.md" ] && continue
    title="$(basename "$card" .md)"
    domain_root="${card%%/Cards/*}"
    index_file="$domain_root/+Wiki Index.md"
    inbound="$(rg -F -l "[[$title" --type md . 2>/dev/null | grep -vxF "$card" | head -1 || true)"
    has_index=""
    if [ -f "$index_file" ]; then
      has_index="$(rg -F "[[$title" "$index_file" 2>/dev/null || true)"
    fi
    has_up="$(rg '^up:[[:space:]]*.' "$card" 2>/dev/null || true)"
    if [ -z "$inbound" ] && [ -z "$has_index" ] && [ -z "$has_up" ]; then
      echo "  - $card"
      undiscoverable=$((undiscoverable + 1))
    fi
  done < <(find "$DOMAINS_DIR" -path "*/Cards/*.md" -type f -print0 2>/dev/null)
fi
echo "  Count: $undiscoverable"
echo ""

echo "## 7. Metadata Drift"
drift=0
empty_tags="$(rg -o '#[A-Za-z0-9_-]+/' --type md --no-filename . 2>/dev/null | sort -u || true)"
while IFS= read -r tag; do
  [ -z "$tag" ] && continue
  echo "  - empty sub-tag: $tag"
  drift=$((drift + 1))
done <<< "$empty_tags"

if [ -d "$DOMAINS_DIR" ]; then
  while IFS= read -r -d '' card; do
    [ "$(basename "$card")" = "README.md" ] && continue
    if ! head -n 1 "$card" | grep -qx -- '---'; then
      echo "  - stable card missing frontmatter: $card"
      drift=$((drift + 1))
    fi
  done < <(find "$DOMAINS_DIR" -path "*/Cards/*.md" -type f -print0 2>/dev/null)
fi
echo "  Count: $drift"
echo ""

echo "## Configured Paths"
echo "  agents: $AGENTS_FILE"
echo "  vault_map: $VAULT_MAP"
echo "  log: $LOG_FILE"
echo "  views: $VIEWS_DIR"
echo "  inbox: $INBOX_DIR"
echo "  capture: $CAPTURE_DIR"
echo "  ingest: $INGEST_DIR"
echo "  writeback: $WRITEBACK_DIR"
echo "  domains: $DOMAINS_DIR"
echo "  shared: $SHARED_DIR"
echo "  archive: $ARCHIVE_DIR"
echo ""

echo "=== Lint Complete ==="

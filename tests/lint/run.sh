#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LINT="$ROOT/skills/lint/scripts/lint-wiki.sh"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

fail() {
  printf 'FAIL: %s\n' "$*" >&2
  exit 1
}

pass() {
  printf 'PASS: %s\n' "$*"
}

assert_no_findings() {
  local name="$1"
  local output="$2"

  if printf '%s\n' "$output" | rg -q '^  - '; then
    printf '%s\n' "$output" >&2
    fail "$name produced lint findings"
  fi

  if ! printf '%s\n' "$output" | rg -q '^=== Lint Complete ===$'; then
    printf '%s\n' "$output" >&2
    fail "$name did not complete lint"
  fi
}

assert_contains() {
  local name="$1"
  local output="$2"
  local pattern="$3"

  if ! printf '%s\n' "$output" | rg -q "$pattern"; then
    printf '%s\n' "$output" >&2
    fail "$name did not contain expected pattern: $pattern"
  fi
}

write_file() {
  local path="$1"
  shift
  mkdir -p "$(dirname "$path")"
  printf '%s\n' "$@" > "$path"
}

make_default_wiki() {
  local wiki="$1"

  mkdir -p \
    "$wiki/.loreforge" \
    "$wiki/00_System/Views" \
    "$wiki/10_Inbox/capture" \
    "$wiki/10_Inbox/ingest" \
    "$wiki/10_Inbox/writeback" \
    "$wiki/Cards" \
    "$wiki/Sources" \
    "$wiki/MOCs" \
    "$wiki/Archive"

  write_file "$wiki/.loreforge/wiki.toml" \
    'schema_version = "0.1"' \
    'name = "fixture"' \
    'description = "Lint fixture"' \
    'agents_file = "AGENTS.md"' \
    'vault_map = "00_System/Vault Map.md"' \
    'schema_file = "00_System/Schema.md"' \
    'index_file = "00_System/+Wiki Index.md"' \
    'log_file = "00_System/Wiki Log.md"' \
    'views_dir = "00_System/Views"' \
    'default_view = "query"' \
    '' \
    '[views]' \
    'default = "00_System/Views/default.md"' \
    'query = "00_System/Views/query.md"' \
    'ingest = "00_System/Views/ingest.md"' \
    'writeback = "00_System/Views/writeback.md"' \
    'promote = "00_System/Views/promote.md"' \
    'maintenance = "00_System/Views/maintenance.md"' \
    '' \
    '[paths]' \
    'inbox = "10_Inbox"' \
    'capture = "10_Inbox/capture"' \
    'ingest = "10_Inbox/ingest"' \
    'writeback = "10_Inbox/writeback"' \
    'cards = "Cards"' \
    'sources = "Sources"' \
    'mocs = "MOCs"' \
    'archive = "Archive"'

  write_file "$wiki/AGENTS.md" '# Fixture Rules'
  write_file "$wiki/00_System/Vault Map.md" '# Vault Map'
  write_file "$wiki/00_System/Schema.md" '# Schema'
  write_file "$wiki/00_System/+Wiki Index.md" '# Wiki Index' '' '## Cards'
  write_file "$wiki/00_System/Wiki Log.md" '# Wiki Log'
  for view in default query ingest writeback promote maintenance; do
    write_file "$wiki/00_System/Views/$view.md" "# $view"
  done
}

make_custom_path_wiki() {
  local wiki="$1"

  mkdir -p \
    "$wiki/.loreforge" \
    "$wiki/System/Views" \
    "$wiki/Work/Inbox/capture" \
    "$wiki/Work/Inbox/ingest" \
    "$wiki/Work/Inbox/writeback" \
    "$wiki/Knowledge/Cards" \
    "$wiki/Knowledge/Sources" \
    "$wiki/Knowledge/MOCs" \
    "$wiki/Closed"

  write_file "$wiki/.loreforge/wiki.toml" \
    'schema_version = "0.1"' \
    'name = "custom-path-fixture"' \
    'description = "Custom path lint fixture"' \
    'agents_file = "ROOT_AGENTS.md"' \
    'vault_map = "System/Vault Map.md"' \
    'schema_file = "System/Schema.md"' \
    'index_file = "System/Card Index.md"' \
    'log_file = "System/Wiki Log.md"' \
    'views_dir = "System/Views"' \
    'default_view = "query"' \
    '' \
    '[views]' \
    'default = "System/Views/default.md"' \
    'query = "System/Views/query.md"' \
    'ingest = "System/Views/ingest.md"' \
    'writeback = "System/Views/writeback.md"' \
    'promote = "System/Views/promote.md"' \
    'maintenance = "System/Views/maintenance.md"' \
    '' \
    '[paths]' \
    'inbox = "Work/Inbox"' \
    'capture = "Work/Inbox/capture"' \
    'ingest = "Work/Inbox/ingest"' \
    'writeback = "Work/Inbox/writeback"' \
    'cards = "Knowledge/Cards"' \
    'sources = "Knowledge/Sources"' \
    'mocs = "Knowledge/MOCs"' \
    'archive = "Closed"'

  write_file "$wiki/ROOT_AGENTS.md" '# Fixture Rules'
  write_file "$wiki/System/Vault Map.md" '# Vault Map'
  write_file "$wiki/System/Schema.md" '# Schema'
  write_file "$wiki/System/Card Index.md" '# Card Index' '' '## Cards'
  write_file "$wiki/System/Wiki Log.md" '# Wiki Log'
  for view in default query ingest writeback promote maintenance; do
    write_file "$wiki/System/Views/$view.md" "# $view"
  done
}

bash -n "$LINT"
pass "lint script syntax"

template_output="$(bash "$LINT" "$ROOT/templates/wiki")"
assert_no_findings "templates/wiki" "$template_output"
pass "templates/wiki is clean"

default_wiki="$TMP_DIR/default-wiki"
make_default_wiki "$default_wiki"
default_output="$(bash "$LINT" "$default_wiki")"
assert_no_findings "default generated fixture" "$default_output"
pass "default generated fixture is clean"

custom_wiki="$TMP_DIR/custom-path-wiki"
make_custom_path_wiki "$custom_wiki"
custom_output="$(bash "$LINT" "$custom_wiki")"
assert_no_findings "custom path fixture" "$custom_output"
assert_contains "custom path fixture" "$custom_output" '^  index: System/Card Index.md$'
assert_contains "custom path fixture" "$custom_output" '^  cards: Knowledge/Cards$'
pass "custom path fixture is clean"

bad_manifest_wiki="$TMP_DIR/bad-manifest-wiki"
make_default_wiki "$bad_manifest_wiki"
mkdir -p "$bad_manifest_wiki/10_Inbox/ingest/2026-04-28-bad"
write_file "$bad_manifest_wiki/10_Inbox/ingest/2026-04-28-bad/manifest.md" \
  '---' \
  'type: ingest' \
  'source_type: docs' \
  'status: staged' \
  'created: 2026-04-28' \
  'provenance:' \
  '  - fixture-source' \
  'candidate_notes:' \
  '  - Cards/Bad Card.md' \
  'updates:' \
  '  - 00_System/Wrong Index.md' \
  'promotion_reason: Exercise manifest validation.' \
  '---' \
  '# Bad Package'
bad_manifest_output="$(bash "$LINT" "$bad_manifest_wiki")"
assert_contains "bad manifest fixture" "$bad_manifest_output" 'card candidates require 00_System/\+Wiki Index.md in updates'
assert_contains "bad manifest fixture" "$bad_manifest_output" '^  Package issues: 1$'
pass "bad manifest fixture reports expected issue"

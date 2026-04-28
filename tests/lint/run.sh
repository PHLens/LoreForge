#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LINT_PROTOCOL="$ROOT/skills/lint/scripts/lint-protocol.sh"
LINT_NATIVE="$ROOT/skills/lint/scripts/lint-native.sh"

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

  if ! printf '%s\n' "$output" | rg -q '^=== Native Lint Complete ===$'; then
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

make_protocol_binding() {
  local root="$1"
  local registry="$root/registry.toml"
  local repo="$root/repo"
  local state="$root/state/notes"

  mkdir -p "$repo/docs" "$repo/references" "$state/packages/ingest/2026-04-28-example/candidates"
  mkdir -p "$state/packages/writeback" "$state/packages/archive" "$state/reports" "$state/cache" "$state/locks" "$state/tmp"
  printf '# Existing\n' > "$repo/docs/existing.md"
  write_file "$state/state.toml" \
    'schema_version = "0.1"' \
    'binding = "notes"' \
    "target_repo = \"$repo\""
  write_file "$state/packages/ingest/2026-04-28-example/manifest.toml" \
    'type = "ingest"' \
    'status = "staged"' \
    'binding = "notes"' \
    'created_at = "2026-04-28T12:00:00+08:00"' \
    '' \
    '[[sources]]' \
    'type = "url"' \
    'ref = "https://example.com/article"' \
    'snapshot = "extract"' \
    '' \
    '[[outputs]]' \
    'kind = "file"' \
    'target = "notes"' \
    'path = "topic/example.md"' \
    'candidate = "candidates/example.md"' \
    'mode = "create"'
  write_file "$state/packages/ingest/2026-04-28-example/candidates/example.md" '# Candidate'
  write_file "$registry" \
    'default = "notes"' \
    '' \
    '[[bindings]]' \
    'name = "notes"' \
    "target_repo = \"$repo\"" \
    "state_dir = \"$state\"" \
    'mode = "generic"' \
    'remote = ""' \
    'description = "Protocol fixture"' \
    'default_target = "notes"' \
    'read_roots = ["."]' \
    '' \
    '[bindings.targets.notes]' \
    'path = "docs"' \
    'description = "General notes"' \
    '' \
    '[bindings.targets.sources]' \
    'path = "references"' \
    'description = "References"'
  printf '%s\n' "$registry"
}

make_default_wiki() {
  local wiki="$1"

  mkdir -p \
    "$wiki/.loreforge" \
    "$wiki/00_System/Views" \
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

bash -n "$LINT_NATIVE"
pass "native lint script syntax"

bash -n "$LINT_PROTOCOL"
pass "protocol lint script syntax"

protocol_root="$TMP_DIR/protocol"
protocol_registry="$(make_protocol_binding "$protocol_root")"
protocol_output="$(bash "$LINT_PROTOCOL" --registry "$protocol_registry" notes)"
assert_contains "protocol lint fixture" "$protocol_output" '^=== LoreForge Protocol Lint Report: notes ===$'
assert_contains "protocol lint fixture" "$protocol_output" '^  Binding issues: 0$'
assert_contains "protocol lint fixture" "$protocol_output" '^  Runtime issues: 0$'
assert_contains "protocol lint fixture" "$protocol_output" '^  Package issues: 0$'
pass "protocol lint fixture is clean"

bad_root="$TMP_DIR/protocol-bad"
bad_registry="$(make_protocol_binding "$bad_root")"
bad_manifest="$bad_root/state/notes/packages/ingest/2026-04-28-example/manifest.toml"
sed -i 's|path = "topic/example.md"|path = "../escape.md"|' "$bad_manifest"
bad_output="$(bash "$LINT_PROTOCOL" --registry "$bad_registry" notes)"
assert_contains "protocol lint traversal fixture" "$bad_output" 'output path escapes target'
assert_contains "protocol lint traversal fixture" "$bad_output" '^  Package issues: 1$'
pass "protocol lint detects path traversal"

missing_read_root="$TMP_DIR/protocol-missing-read-root"
missing_read_root_registry="$(make_protocol_binding "$missing_read_root")"
sed -i 's|read_roots = \["\."\]|read_roots = ["missing"]|' "$missing_read_root_registry"
missing_read_root_output="$(bash "$LINT_PROTOCOL" --registry "$missing_read_root_registry" notes)"
assert_contains "protocol lint missing read root fixture" "$missing_read_root_output" 'read_root is not a directory'
assert_contains "protocol lint missing read root fixture" "$missing_read_root_output" '^  Binding issues: 1$'
pass "protocol lint detects missing read roots"

file_target_root="$TMP_DIR/protocol-file-target"
file_target_registry="$(make_protocol_binding "$file_target_root")"
rm -rf "$file_target_root/repo/docs"
printf 'not a directory\n' > "$file_target_root/repo/docs"
file_target_output="$(bash "$LINT_PROTOCOL" --registry "$file_target_registry" notes)"
assert_contains "protocol lint file target fixture" "$file_target_output" 'target path exists but is not a directory'
assert_contains "protocol lint file target fixture" "$file_target_output" '^  Binding issues: 1$'
pass "protocol lint detects unusable target paths"

bad_registry_fields_root="$TMP_DIR/protocol-bad-registry-fields"
bad_registry_fields_registry="$(make_protocol_binding "$bad_registry_fields_root")"
sed -i 's|mode = "generic"|mode = "surprise"|' "$bad_registry_fields_registry"
sed -i 's|default_target = "notes"|default_target = "missing"|' "$bad_registry_fields_registry"
bad_registry_fields_output="$(bash "$LINT_PROTOCOL" --registry "$bad_registry_fields_registry" notes)"
assert_contains "protocol lint bad registry fields fixture" "$bad_registry_fields_output" 'mode must be generic or native'
assert_contains "protocol lint bad registry fields fixture" "$bad_registry_fields_output" 'default_target is not configured'
assert_contains "protocol lint bad registry fields fixture" "$bad_registry_fields_output" '^  Binding issues: 2$'
pass "protocol lint validates mode and default target"

native_stable_target_root="$TMP_DIR/protocol-native-stable-target"
native_stable_target_registry="$(make_protocol_binding "$native_stable_target_root")"
sed -i 's|mode = "generic"|mode = "native"|' "$native_stable_target_registry"
sed -i 's|path = "docs"|path = "Cards"|' "$native_stable_target_registry"
native_stable_target_output="$(bash "$LINT_PROTOCOL" --registry "$native_stable_target_registry" notes)"
assert_contains "protocol lint native stable target fixture" "$native_stable_target_output" 'native target path points at stable knowledge'
assert_contains "protocol lint native stable target fixture" "$native_stable_target_output" '^  Binding issues: 1$'
pass "protocol lint rejects native stable targets"

missing_manifest_root="$TMP_DIR/protocol-missing-manifest"
missing_manifest_registry="$(make_protocol_binding "$missing_manifest_root")"
mkdir -p "$missing_manifest_root/state/notes/packages/ingest/2026-04-28-missing"
missing_manifest_output="$(bash "$LINT_PROTOCOL" --registry "$missing_manifest_registry" notes)"
assert_contains "protocol lint missing manifest fixture" "$missing_manifest_output" 'staged package missing manifest.toml'
assert_contains "protocol lint missing manifest fixture" "$missing_manifest_output" '^  Package issues: 1$'
pass "protocol lint detects missing package manifests"

bad_output_fields_root="$TMP_DIR/protocol-bad-output-fields"
bad_output_fields_registry="$(make_protocol_binding "$bad_output_fields_root")"
bad_output_fields_manifest="$bad_output_fields_root/state/notes/packages/ingest/2026-04-28-example/manifest.toml"
sed -i 's|kind = "file"|kind = "unknown"|' "$bad_output_fields_manifest"
sed -i 's|mode = "create"|mode = "overwrite"|' "$bad_output_fields_manifest"
bad_output_fields_output="$(bash "$LINT_PROTOCOL" --registry "$bad_output_fields_registry" notes)"
assert_contains "protocol lint bad output fields fixture" "$bad_output_fields_output" 'kind must be file or patch'
assert_contains "protocol lint bad output fields fixture" "$bad_output_fields_output" 'mode must be create or update'
assert_contains "protocol lint bad output fields fixture" "$bad_output_fields_output" '^  Package issues: 2$'
pass "protocol lint validates output kind and mode"

bad_patch_root="$TMP_DIR/protocol-bad-patch"
bad_patch_registry="$(make_protocol_binding "$bad_patch_root")"
bad_patch_package="$bad_patch_root/state/notes/packages/writeback/2026-04-28-bad-patch"
mkdir -p "$bad_patch_package/patches"
write_file "$bad_patch_package/manifest.toml" \
  'type = "writeback"' \
  'status = "staged"' \
  'binding = "notes"' \
  'created_at = "2026-04-28T12:15:00+08:00"' \
  '' \
  '[[outputs]]' \
  'kind = "patch"' \
  'target = "notes"' \
  'path = "existing.md"' \
  'patch = "patches/bad.patch"' \
  'mode = "update"'
write_file "$bad_patch_package/patches/bad.patch" 'this is not a patch'
bad_patch_output="$(bash "$LINT_PROTOCOL" --registry "$bad_patch_registry" notes)"
assert_contains "protocol lint bad patch fixture" "$bad_patch_output" 'update patch does not apply cleanly'
assert_contains "protocol lint bad patch fixture" "$bad_patch_output" '^  Package issues: 1$'
pass "protocol lint validates update patches"

template_output="$(bash "$LINT_NATIVE" "$ROOT/templates/wiki")"
assert_no_findings "templates/wiki" "$template_output"
pass "templates/wiki is clean"

default_wiki="$TMP_DIR/default-wiki"
make_default_wiki "$default_wiki"
default_output="$(bash "$LINT_NATIVE" "$default_wiki")"
assert_no_findings "default generated fixture" "$default_output"
pass "default generated fixture is clean"

custom_wiki="$TMP_DIR/custom-path-wiki"
make_custom_path_wiki "$custom_wiki"
custom_output="$(bash "$LINT_NATIVE" "$custom_wiki")"
assert_no_findings "custom path fixture" "$custom_output"
assert_contains "custom path fixture" "$custom_output" '^  index: System/Card Index.md$'
assert_contains "custom path fixture" "$custom_output" '^  cards: Knowledge/Cards$'
pass "custom path fixture is clean"

bad_manifest_wiki="$TMP_DIR/bad-manifest-wiki"
make_default_wiki "$bad_manifest_wiki"
mkdir -p "$bad_manifest_wiki/10_Inbox/ingest/2026-04-28-bad"
write_file "$bad_manifest_wiki/10_Inbox/ingest/2026-04-28-bad/Cards/Bad Card.md" '# Bad Card'
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
bad_manifest_output="$(bash "$LINT_NATIVE" "$bad_manifest_wiki")"
assert_contains "bad manifest fixture" "$bad_manifest_output" 'card candidates require 00_System/\+Wiki Index.md in updates'
assert_contains "bad manifest fixture" "$bad_manifest_output" '^  Package issues: 1$'
pass "bad manifest fixture reports expected issue"

bad_candidate_wiki="$TMP_DIR/bad-candidate-wiki"
make_default_wiki "$bad_candidate_wiki"
mkdir -p "$bad_candidate_wiki/10_Inbox/ingest/2026-04-28-bad-candidate"
write_file "$bad_candidate_wiki/10_Inbox/ingest/2026-04-28-bad-candidate/manifest.md" \
  '---' \
  'type: ingest' \
  'source_type: docs' \
  'status: staged' \
  'created: 2026-04-28' \
  'provenance:' \
  '  - fixture-source' \
  'candidate_notes:' \
  '  - ../../Cards/Escape.md' \
  'updates:' \
  '  - 00_System/+Wiki Index.md' \
  'promotion_reason: Exercise candidate validation.' \
  '---' \
  '# Bad Candidate Package'
bad_candidate_output="$(bash "$LINT_NATIVE" "$bad_candidate_wiki")"
assert_contains "bad candidate fixture" "$bad_candidate_output" 'candidate path escapes package'
pass "native lint rejects escaping candidate paths"

missing_candidate_wiki="$TMP_DIR/missing-candidate-wiki"
make_default_wiki "$missing_candidate_wiki"
mkdir -p "$missing_candidate_wiki/10_Inbox/writeback/2026-04-28-missing-candidate"
write_file "$missing_candidate_wiki/10_Inbox/writeback/2026-04-28-missing-candidate/manifest.md" \
  '---' \
  'type: writeback' \
  'source_type: conversation_synthesis' \
  'status: staged' \
  'created: 2026-04-28' \
  'provenance:' \
  '  - conversation: fixture' \
  'candidate_notes:' \
  '  - Cards/Missing.md' \
  'updates:' \
  '  - 00_System/+Wiki Index.md' \
  'promotion_reason: Exercise missing candidate validation.' \
  '---' \
  '# Missing Candidate Package'
missing_candidate_output="$(bash "$LINT_NATIVE" "$missing_candidate_wiki")"
assert_contains "missing candidate fixture" "$missing_candidate_output" 'candidate file missing'
assert_contains "missing candidate fixture" "$missing_candidate_output" '^  Package issues: 1$'
pass "native lint detects missing candidate files"

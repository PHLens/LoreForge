#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SETUP="$ROOT/scripts/setup-binding.sh"
LINT_PROTOCOL="$ROOT/skills/lint/scripts/lint-protocol.sh"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

fail() {
  printf 'FAIL: %s\n' "$*" >&2
  exit 1
}

pass() {
  printf 'PASS: %s\n' "$*"
}

assert_file_contains() {
  local file="$1"
  local pattern="$2"

  if ! grep -Eq "$pattern" "$file"; then
    printf '%s\n' "File did not match: $file" >&2
    printf '%s\n' "Pattern: $pattern" >&2
    sed -n '1,220p' "$file" >&2
    fail "missing expected file content"
  fi
}

bash -n "$SETUP"
pass "setup-binding script syntax"

generic_repo="$TMP_DIR/generic-repo"
mkdir -p "$generic_repo/docs" "$generic_repo/references"
printf '# Existing Note\n' > "$generic_repo/docs/existing.md"

registry="$TMP_DIR/registry.toml"
state="$TMP_DIR/state/notes"

bash "$SETUP" notes "$generic_repo" \
  --registry "$registry" \
  --state-dir "$state" \
  --description "General notes binding" \
  --remote "git@example.com:demo/notes.git" \
  --read-root "." \
  --target "notes=docs:General notes" \
  --target "sources=references:Source-grounded notes" \
  --default-target "notes" >/dev/null

[ -f "$registry" ] || fail "registry missing"
[ -d "$state/packages/ingest" ] || fail "ingest package state missing"
[ -d "$state/packages/writeback" ] || fail "writeback package state missing"
[ -d "$state/packages/archive" ] || fail "archive package state missing"
[ -d "$state/reports" ] || fail "reports state missing"
[ -d "$state/cache" ] || fail "cache state missing"
[ -d "$state/locks" ] || fail "locks state missing"
[ -d "$state/tmp" ] || fail "tmp state missing"
[ -f "$state/state.toml" ] || fail "state.toml missing"
[ ! -e "$generic_repo/.loreforge" ] || fail "generic setup wrote repo-local .loreforge"

assert_file_contains "$registry" '^default = "notes"$'
assert_file_contains "$registry" '^\[\[bindings\]\]$'
assert_file_contains "$registry" '^name = "notes"$'
assert_file_contains "$registry" "^target_repo = \"$generic_repo\"$"
assert_file_contains "$registry" "^state_dir = \"$state\"$"
assert_file_contains "$registry" '^mode = "generic"$'
assert_file_contains "$registry" '^remote = "git@example.com:demo/notes.git"$'
assert_file_contains "$registry" '^description = "General notes binding"$'
assert_file_contains "$registry" '^default_target = "notes"$'
assert_file_contains "$registry" '^read_roots = \["\."\]$'
assert_file_contains "$registry" '^\[bindings.targets.notes\]$'
assert_file_contains "$registry" '^path = "docs"$'
assert_file_contains "$registry" '^\[bindings.targets.sources\]$'
assert_file_contains "$registry" '^path = "references"$'

bash "$LINT_PROTOCOL" --registry "$registry" notes >/dev/null
pass "generic binding creates runtime state and passes protocol lint"

bash "$SETUP" notes "$generic_repo" \
  --registry "$registry" >/dev/null

assert_file_contains "$registry" "^state_dir = \"$state\"$"
assert_file_contains "$registry" '^remote = "git@example.com:demo/notes.git"$'
assert_file_contains "$registry" '^description = "General notes binding"$'
assert_file_contains "$registry" '^default_target = "notes"$'
assert_file_contains "$registry" '^\[bindings.targets.sources\]$'
assert_file_contains "$registry" '^path = "references"$'

bash "$LINT_PROTOCOL" --registry "$registry" notes >/dev/null
pass "repeat setup preserves existing binding fields"

default_repo="$TMP_DIR/default-generic-repo"
default_registry="$TMP_DIR/default-registry.toml"
default_state="$TMP_DIR/state/default"
bash "$SETUP" default "$default_repo" \
  --registry "$default_registry" \
  --state-dir "$default_state" >/dev/null

[ -d "$default_repo/notes" ] || fail "default generic target dir missing"
assert_file_contains "$default_registry" '^default_target = "notes"$'
assert_file_contains "$default_registry" '^\[bindings.targets.notes\]$'
assert_file_contains "$default_registry" '^path = "notes"$'
bash "$LINT_PROTOCOL" --registry "$default_registry" default >/dev/null
pass "default generic setup avoids repository root target"

native_repo="$TMP_DIR/native-repo"
native_state="$TMP_DIR/state/cs"
bash "$SETUP" cs "$native_repo" \
  --registry "$registry" \
  --state-dir "$native_state" \
  --mode native \
  --init-native-template \
  --description "Native knowledge repo" \
  --read-root "." \
  --target "writeback_staging=10_Inbox/writeback:Native staged writeback packages" \
  --target "ingest_staging=10_Inbox/ingest:Native staged ingest packages" \
  --default-target "writeback_staging" >/dev/null

[ -f "$native_repo/.loreforge/wiki.toml" ] || fail "native wiki config missing"
[ -f "$native_repo/00_System/+Wiki Index.md" ] || fail "native index missing"
[ -d "$native_state/packages/ingest" ] || fail "native runtime state missing"
assert_file_contains "$registry" '^name = "cs"$'
assert_file_contains "$registry" '^mode = "native"$'
assert_file_contains "$registry" '^default_target = "writeback_staging"$'
assert_file_contains "$registry" '^\[bindings.targets.writeback_staging\]$'
assert_file_contains "$registry" '^path = "10_Inbox/writeback"$'
assert_file_contains "$registry" '^\[bindings.targets.ingest_staging\]$'
assert_file_contains "$registry" '^path = "10_Inbox/ingest"$'
assert_file_contains "$registry" '^\[bindings.native\]$'
assert_file_contains "$registry" '^index_file = "00_System/\+Wiki Index.md"$'

bash "$LINT_PROTOCOL" --registry "$registry" cs >/dev/null
pass "native binding creates starter repo and passes protocol lint"

bad_native_target="$TMP_DIR/bad-native-target"
bash "$SETUP" badnative "$bad_native_target" \
  --registry "$registry" \
  --mode native \
  --init-native-template \
  --target "cards=Cards:Native cards" \
  --default-target "cards" >/tmp/loreforge-native-stable-target.out 2>&1 && {
  cat /tmp/loreforge-native-stable-target.out >&2
  fail "native setup allowed stable writeback target"
}
pass "native setup rejects stable writeback targets"

non_empty_native="$TMP_DIR/non-empty-native"
mkdir -p "$non_empty_native"
printf '# User file\n' > "$non_empty_native/README.md"
bash "$SETUP" blocked "$non_empty_native" \
  --registry "$registry" \
  --mode native \
  --init-native-template >/tmp/loreforge-native-nonempty.out 2>&1 && {
  cat /tmp/loreforge-native-nonempty.out >&2
  fail "native template setup allowed non-empty target"
}
pass "native template setup rejects non-empty target"

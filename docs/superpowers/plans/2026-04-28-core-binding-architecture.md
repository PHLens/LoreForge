# Core Binding Architecture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace LoreForge's wiki-first core with a binding-centric core that stages workflow state in runtime storage and treats native wiki repos as an optional profile.

**Architecture:** Add a generic binding setup script, protocol lint, and search workflow that operate on `target_repo + state_dir + targets`. Keep `templates/wiki` and the existing structural lint as the native profile for query and promote. Rewrite docs and routing so generic repositories are first-class without requiring `00_System`, `10_Inbox`, `Cards`, `Sources`, or `MOCs`.

**Tech Stack:** Bash scripts, Markdown skills/docs, TOML-like config templates parsed with shell/awk, existing shell test runners under `tests/`.

---

## File Structure

- Create `scripts/setup-binding.sh`: deterministic helper for generic and native bindings.
- Modify `templates/config/registry.toml`: example registry uses `[[bindings]]`, `target_repo`, `state_dir`, `mode`, `read_roots`, and named targets.
- Create `skills/lint/scripts/lint-protocol.sh`: read-only protocol health check for bindings, runtime state, packages, and writeback targets.
- Create `skills/lint/scripts/lint-native.sh`: native structural lint entry copied from the existing `lint-wiki.sh` behavior.
- Modify `skills/lint/scripts/lint-wiki.sh`: compatibility wrapper that calls `lint-native.sh`.
- Create `tests/setup/run.sh`: setup-binding regression tests for generic and native bindings.
- Modify `tests/lint/run.sh`: run protocol lint fixtures and native lint fixtures.
- Do not add `tests/install/run.sh`: wiki-first setup tests are obsolete.
- Create `skills/search/SKILL.md`: lightweight read-root search workflow for generic and native bindings.
- Delete `skills/capture/SKILL.md`: capture is no longer a core workflow.
- Create `skills/setup/SKILL.md`: user-facing binding setup workflow.
- Modify `skills/ingest/SKILL.md`: source ingestion now stages runtime packages directly.
- Modify `skills/writeback/SKILL.md`: generic writeback validates package outputs against configured targets.
- Modify `skills/query/SKILL.md`: native-only query contract.
- Modify `skills/promote/SKILL.md`: native-only promotion contract.
- Modify `skills/lint/SKILL.md`: protocol lint default and native lint profile.
- Modify `skills/register/SKILL.md`: low-level binding registry maintenance.
- Modify `skills/sync/SKILL.md`: sync target repos, not runtime state.
- Modify `skills/loreforge-router/SKILL.md`, `.claude/CLAUDE.md`, `.codex-plugin/plugin.json`, `skills/README.md`: routing and plugin metadata.
- Modify `README.md`, `docs/install.md`, `docs/config.md`, `docs/schema.md`, `docs/philosophy.md`, `tests/README.md`: binding-centric documentation.

## Task 0: Workspace Checkpoint

**Files:**
- Inspect only: repository status and recent commits

- [ ] **Step 1: Confirm the implementation worktree is clean**

Run:

```bash
git status --short --branch
```

Expected: a clean implementation branch with no modified or untracked implementation files:

```text
## core-binding-architecture
```

- [ ] **Step 2: Confirm the architecture spec is present**

Run:

```bash
test -f docs/superpowers/specs/2026-04-28-loreforge-core-binding-design.md
```

Expected: command exits `0`.

- [ ] **Step 3: Keep the plan commit separate**

Run:

```bash
git diff --cached --name-status
```

Expected: no staged files before implementation starts.

## Task 1: Binding Setup Tests

**Files:**
- Create: `tests/setup/run.sh`
- Modify: `tests/README.md`

- [ ] **Step 1: Add the failing setup test**

Create `tests/setup/run.sh` with this content:

```bash
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
assert_file_contains "$registry" '^default_target = "notes"$'
assert_file_contains "$registry" '^read_roots = \["\."\]$'
assert_file_contains "$registry" '^\[bindings.targets.notes\]$'
assert_file_contains "$registry" '^path = "docs"$'
assert_file_contains "$registry" '^\[bindings.targets.sources\]$'
assert_file_contains "$registry" '^path = "references"$'

bash "$LINT_PROTOCOL" --registry "$registry" notes >/dev/null
pass "generic binding creates runtime state and passes protocol lint"

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
assert_file_contains "$registry" '^\[bindings.native\]$'
assert_file_contains "$registry" '^index_file = "00_System/\+Wiki Index.md"$'

bash "$LINT_PROTOCOL" --registry "$registry" cs >/dev/null
pass "native binding creates starter repo and passes protocol lint"

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
```

- [ ] **Step 2: Update test documentation**

In `tests/README.md`, replace the install/lint section with:

~~~markdown
# Tests

Run focused shell regressions from the repository root:

```bash
bash tests/setup/run.sh
bash tests/lint/run.sh
```

`tests/setup/run.sh` verifies binding setup, runtime state creation, registry output, and native starter creation.

`tests/lint/run.sh` verifies protocol lint for generic bindings and native lint for the native starter template.
~~~

- [ ] **Step 3: Run the failing test**

Run:

```bash
bash tests/setup/run.sh
```

Expected: FAIL because `scripts/setup-binding.sh` and `skills/lint/scripts/lint-protocol.sh` do not exist yet.

- [ ] **Step 4: Commit the failing tests**

Run:

```bash
git add tests/setup/run.sh tests/README.md
git commit -m "test: add binding setup regression"
```

Expected: commit succeeds with the new setup test and test documentation.

## Task 2: Binding Setup Script

**Files:**
- Create: `scripts/setup-binding.sh`
- Modify: `templates/config/registry.toml`

- [ ] **Step 1: Create the setup-binding implementation**

Create `scripts/setup-binding.sh` as an executable Bash script. It must implement this interface:

```text
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
  --default-target NAME    Default writeback or staging target
  --no-default             Do not make this binding the registry default
  --no-git                 Do not run git init for native starter creation
  -h, --help               Show help
```

Required behavior:

```bash
NAME_REGEX='^[A-Za-z0-9._-]+$'
DEFAULT_REGISTRY="${LOREFORGE_REGISTRY:-$HOME/.config/loreforge/registry.toml}"
DEFAULT_STATE_DIR="$HOME/.local/state/loreforge/$NAME"
DEFAULT_MODE="generic"
DEFAULT_READ_ROOT="."
DEFAULT_GENERIC_TARGET="notes"
DEFAULT_GENERIC_TARGET_SPEC="notes=notes:Default durable notes target"
DEFAULT_NATIVE_TARGET="writeback_staging"
```

Use these runtime directories:

```bash
packages/ingest
packages/writeback
packages/archive
reports
cache
locks
tmp
```

Write `state.toml` with:

```toml
schema_version = "0.1"
binding = "<name>"
target_repo = "<absolute target repo>"
```

For generic mode:

- create `target_repo` if missing
- do not create `<target_repo>/.loreforge`
- do not copy `templates/wiki`
- create configured target directories only when the user supplied a target path that does not exist

For native mode with `--init-native-template`:

- require missing or empty `target_repo`
- copy `templates/wiki/.` into `target_repo`
- initialize git unless `--no-git` is supplied
- write a registry binding with `[bindings.native]` fields:

```toml
index_file = "00_System/+Wiki Index.md"
log_file = "00_System/Wiki Log.md"
views_dir = "00_System/Views"
```

Registry output must use `[[bindings]]` blocks. The script must replace any existing binding block with the same `name`, then append the new block.

- [ ] **Step 2: Use exact registry block formatting**

The script must append generic bindings in this shape:

```toml
[[bindings]]
name = "notes"
target_repo = "/absolute/path"
state_dir = "/absolute/state"
mode = "generic"
remote = ""
description = "General notes binding"
default_target = "notes"
read_roots = ["."]

[bindings.targets.notes]
path = "docs"
description = "General notes"
```

Native bindings use the same block plus:

```toml
[bindings.native]
index_file = "00_System/+Wiki Index.md"
log_file = "00_System/Wiki Log.md"
views_dir = "00_System/Views"
```

- [ ] **Step 3: Replace the registry template**

Replace `templates/config/registry.toml` with:

```toml
# LoreForge local binding registry
#
# Copy this file to:
#   ~/.config/loreforge/registry.toml
#
# The registry is machine-local. It binds user-owned target repositories
# to LoreForge runtime state and writeback targets.

default = "notes"

[[bindings]]
name = "notes"
target_repo = "/path/to/notes"
state_dir = "~/.local/state/loreforge/notes"
mode = "generic"
remote = "git@github.com:OWNER/notes.git"
description = "Example generic Markdown repository"
default_target = "notes"
read_roots = ["."]

[bindings.targets.notes]
path = "notes"
description = "General notes"

[bindings.targets.sources]
path = "references"
description = "Source-grounded notes"

[[bindings]]
name = "cs"
target_repo = "/path/to/cs-native"
state_dir = "~/.local/state/loreforge/cs"
mode = "native"
remote = "git@github.com:OWNER/cs-native.git"
description = "Example native LoreForge repository"
default_target = "writeback_staging"
read_roots = ["."]

[bindings.targets.writeback_staging]
path = "10_Inbox/writeback"
description = "Native staged writeback packages"

[bindings.targets.ingest_staging]
path = "10_Inbox/ingest"
description = "Native staged ingest packages"

[bindings.native]
index_file = "00_System/+Wiki Index.md"
log_file = "00_System/Wiki Log.md"
views_dir = "00_System/Views"
```

- [ ] **Step 4: Run setup tests**

Run:

```bash
bash tests/setup/run.sh
```

Expected: FAIL only because protocol lint is not implemented yet. The failure should mention missing `skills/lint/scripts/lint-protocol.sh`.

- [ ] **Step 5: Commit setup script**

Run:

```bash
git add scripts/setup-binding.sh templates/config/registry.toml
git commit -m "feat: add binding setup helper"
```

Expected: commit succeeds.

## Task 3: Protocol Lint

**Files:**
- Create: `skills/lint/scripts/lint-protocol.sh`
- Modify: `tests/lint/run.sh`

- [ ] **Step 1: Add protocol lint fixtures to the lint runner**

At the top of `tests/lint/run.sh`, set:

```bash
LINT_PROTOCOL="$ROOT/skills/lint/scripts/lint-protocol.sh"
LINT_NATIVE="$ROOT/skills/lint/scripts/lint-native.sh"
```

Add this fixture function before native fixtures:

```bash
make_protocol_binding() {
  local root="$1"
  local registry="$root/registry.toml"
  local repo="$root/repo"
  local state="$root/state/notes"

  mkdir -p "$repo/docs" "$repo/references" "$state/packages/ingest/2026-04-28-example/candidates"
  mkdir -p "$state/packages/writeback" "$state/packages/archive" "$state/reports" "$state/cache" "$state/locks" "$state/tmp"
  printf '# Existing\n' > "$repo/docs/existing.md"
  cat > "$state/state.toml" <<EOF
schema_version = "0.1"
binding = "notes"
target_repo = "$repo"
EOF
  cat > "$state/packages/ingest/2026-04-28-example/manifest.toml" <<'EOF'
type = "ingest"
status = "staged"
binding = "notes"
created_at = "2026-04-28T12:00:00+08:00"

[[sources]]
type = "url"
ref = "https://example.com/article"
snapshot = "extract"

[[outputs]]
kind = "file"
target = "notes"
path = "topic/example.md"
candidate = "candidates/example.md"
mode = "create"
EOF
  printf '# Candidate\n' > "$state/packages/ingest/2026-04-28-example/candidates/example.md"
  cat > "$registry" <<EOF
default = "notes"

[[bindings]]
name = "notes"
target_repo = "$repo"
state_dir = "$state"
mode = "generic"
remote = ""
description = "Protocol fixture"
default_target = "notes"
read_roots = ["."]

[bindings.targets.notes]
path = "docs"
description = "General notes"

[bindings.targets.sources]
path = "references"
description = "References"
EOF
  printf '%s\n' "$registry"
}
```

Add this assertion after `bash -n "$LINT_PROTOCOL"`:

```bash
protocol_root="$TMP_DIR/protocol"
protocol_registry="$(make_protocol_binding "$protocol_root")"
protocol_output="$(bash "$LINT_PROTOCOL" --registry "$protocol_registry" notes)"
assert_contains "protocol lint fixture" "$protocol_output" '^=== LoreForge Protocol Lint Report: notes ===$'
assert_contains "protocol lint fixture" "$protocol_output" '^  Binding issues: 0$'
assert_contains "protocol lint fixture" "$protocol_output" '^  Runtime issues: 0$'
assert_contains "protocol lint fixture" "$protocol_output" '^  Package issues: 0$'
pass "protocol lint fixture is clean"
```

Add a path traversal fixture:

```bash
bad_root="$TMP_DIR/protocol-bad"
bad_registry="$(make_protocol_binding "$bad_root")"
bad_manifest="$bad_root/state/notes/packages/ingest/2026-04-28-example/manifest.toml"
perl -0pi -e 's/path = "topic\/example.md"/path = "..\/escape.md"/' "$bad_manifest"
bad_output="$(bash "$LINT_PROTOCOL" --registry "$bad_registry" notes)"
assert_contains "protocol lint traversal fixture" "$bad_output" 'output path escapes target'
assert_contains "protocol lint traversal fixture" "$bad_output" '^  Package issues: 1$'
pass "protocol lint detects path traversal"
```

- [ ] **Step 2: Create the protocol lint script**

Create `skills/lint/scripts/lint-protocol.sh` with these behaviors:

```text
Usage:
  lint-protocol.sh [--registry PATH] [binding-name]
```

Required checks:

- registry file exists
- binding exists by `name`
- `target_repo` exists as a directory
- `state_dir` exists as a directory
- `state_dir` contains `packages/ingest`, `packages/writeback`, `packages/archive`, `reports`, `cache`, `locks`, and `tmp`
- every `read_roots` entry stays inside `target_repo`
- every configured target path stays inside `target_repo`
- every staged package `manifest.toml` has `type`, `status`, `binding`, and `created_at`
- package `binding` matches the selected binding
- every `[[outputs]]` block has `kind`, `target`, `path`, `mode`, and either `candidate` or `patch`
- output `target` is configured
- output `path` does not escape the configured target path
- `mode = "create"` does not target an existing file
- `candidate` files exist for file outputs
- `patch` files exist for patch outputs

Required report headings:

```text
=== LoreForge Protocol Lint Report: <binding> ===

## Binding
  Binding issues: <n>

## Runtime State
  Runtime issues: <n>

## Packages
  Package issues: <n>

=== Protocol Lint Complete ===
```

Use `awk`, `sed`, `find`, and shell functions. Do not require Python, jq, or a TOML package.

- [ ] **Step 3: Run protocol lint tests**

Run:

```bash
bash tests/lint/run.sh
bash tests/setup/run.sh
```

Expected: protocol lint tests pass. Native lint tests may fail until Task 4 creates `lint-native.sh`.

- [ ] **Step 4: Commit protocol lint**

Run:

```bash
git add skills/lint/scripts/lint-protocol.sh tests/lint/run.sh
git commit -m "feat: add protocol lint"
```

Expected: commit succeeds.

## Task 4: Native Lint Profile

**Files:**
- Create: `skills/lint/scripts/lint-native.sh`
- Modify: `skills/lint/scripts/lint-wiki.sh`
- Modify: `tests/lint/run.sh`

- [ ] **Step 1: Move existing structural lint into native lint**

Copy the current body of `skills/lint/scripts/lint-wiki.sh` into `skills/lint/scripts/lint-native.sh`.

Change the first comment and report title in `lint-native.sh` to:

```bash
# Read-only native structure health check for a LoreForge native repo.
```

```bash
echo "=== LoreForge Native Lint Report: $(basename "$(pwd)") ==="
```

Change the completion line to:

```bash
echo "=== Native Lint Complete ==="
```

- [ ] **Step 2: Replace lint-wiki with a compatibility wrapper**

Replace `skills/lint/scripts/lint-wiki.sh` with:

```bash
#!/usr/bin/env bash
# Compatibility wrapper for the legacy wiki lint command.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
exec "$ROOT/skills/lint/scripts/lint-native.sh" "$@"
```

- [ ] **Step 3: Update native lint assertions**

In `tests/lint/run.sh`, update native assertions so clean native output checks:

```bash
assert_contains "templates/wiki" "$template_output" '^=== Native Lint Complete ===$'
```

The existing bad manifest native fixture should remain a native-only fixture. It must still assert:

```bash
assert_contains "bad manifest fixture" "$bad_manifest_output" 'card candidates require 00_System/\+Wiki Index.md in updates'
assert_contains "bad manifest fixture" "$bad_manifest_output" '^  Package issues: 1$'
```

- [ ] **Step 4: Run lint regression**

Run:

```bash
bash tests/lint/run.sh
```

Expected: all lint checks pass, including protocol fixtures and native fixtures.

- [ ] **Step 5: Commit native lint split**

Run:

```bash
git add skills/lint/scripts/lint-native.sh skills/lint/scripts/lint-wiki.sh tests/lint/run.sh
git commit -m "refactor: split protocol and native lint"
```

Expected: commit succeeds.

## Task 5: Core Skill Routing

**Files:**
- Create: `skills/search/SKILL.md`
- Modify: `skills/loreforge-router/SKILL.md`
- Modify: `skills/README.md`
- Modify: `.claude/CLAUDE.md`
- Modify: `.codex-plugin/plugin.json`

- [ ] **Step 1: Add search skill**

Create `skills/search/SKILL.md`:

~~~markdown
---
name: search
description: Use for lightweight filesystem and Markdown search over configured LoreForge binding read roots.
user-invocable: true
---

# Search Binding

Search is available for generic and native bindings.

## Trigger

Use for:

- `search binding`
- `search repo`
- `find in notes`
- lightweight lookup before ingest or writeback

## Discovery

1. Read `~/.config/loreforge/registry.toml`.
2. Resolve the named binding or the registry `default`.
3. Read `target_repo` and `read_roots`.
4. Search only inside configured read roots.

## Execution

Use `rg` first:

```bash
rg -n "<query>" <target_repo>/<read_root>
```

If `rg` is unavailable, use the fastest available local search command.

## Boundary

Search does not promise native query semantics. It does not require indexes, MOCs, source provenance, or native views.

For structured native retrieval, use `query` on a binding with `mode = "native"`.
~~~

- [ ] **Step 2: Rewrite router table**

In `skills/loreforge-router/SKILL.md`, replace the route table with:

```markdown
| Intent | Skill |
|---|---|
| Create, install, adopt, or register a binding | `setup` |
| Ingest a URL, file, article, paper, docs page, repo note, or user-provided source | `ingest` |
| Search a configured target repo read root | `search` |
| Write staged package outputs into configured target paths | `writeback` |
| Answer from native LoreForge knowledge using indexes, views, cards, sources, and MOCs | `query` |
| Promote native staged material into native cards, sources, MOCs, indexes, logs, and archive | `promote` |
| Check binding runtime state and package health | `lint protocol` |
| Check native repo structure and index/provenance health | `lint native` |
| Low-level binding registry update | `register` |
| Pull, inspect, commit, or push a target repo | `sync` |
```

Replace the boundary bullets with:

```markdown
- Shared professional knowledge belongs in user-owned target repositories.
- Runtime packages, extracts, reports, caches, and locks belong in LoreForge runtime state.
- Agent-local experience, preferences, task state, and workflow memories belong in `pamem`.
- Locate bindings through `~/.config/loreforge/registry.toml`.
- Generic bindings support setup, ingest, writeback, search, and protocol lint.
- Native bindings additionally support query, promote, and native lint.
- Recover after compaction from the selected binding, runtime package manifests, and target repo context.
```

- [ ] **Step 3: Update skill index**

In `skills/README.md`, make the core table:

```markdown
| Skill | Purpose |
|---|---|
| `setup` | Create or update LoreForge bindings and runtime state |
| `ingest` | Process source material into staged runtime packages |
| `writeback` | Write staged package outputs into configured target paths |
| `search` | Search configured read roots in generic or native bindings |
| `lint` | Run protocol lint by default and native lint for native bindings |
| `register` | Low-level binding registry maintenance |
| `sync` | Sync target repositories with Git remotes |
| `query` | Native-only structured retrieval |
| `promote` | Native-only stable promotion |
```

- [ ] **Step 4: Update always-on and plugin routing**

Update `.claude/CLAUDE.md` with the same route table as Step 3.

Update `.codex-plugin/plugin.json` so the long description contains:

```text
LoreForge provides binding-centric workflows for setup, ingest, writeback, search, lint, and native query/promote profiles.
```

Remove capture from default prompts or routing text.

- [ ] **Step 5: Run routing grep**

Run:

```bash
rg -n "capture|wiki instance|\\.loreforge/wiki|10_Inbox|Cards|Sources|MOCs" skills .claude .codex-plugin
```

Expected: remaining matches are only in native-only skills (`query`, `promote`, native lint docs), native template references, or migration wording that explicitly says capture was removed.

- [ ] **Step 6: Commit routing changes**

Run:

```bash
git add skills/search/SKILL.md skills/loreforge-router/SKILL.md skills/README.md .claude/CLAUDE.md .codex-plugin/plugin.json
git commit -m "refactor: route core workflows through bindings"
```

Expected: commit succeeds.

## Task 6: Setup, Ingest, Writeback, Query, Promote, Lint, Register, Sync Skills

**Files:**
- Create: `skills/setup/SKILL.md`
- Modify: `skills/ingest/SKILL.md`
- Modify: `skills/writeback/SKILL.md`
- Modify: `skills/query/SKILL.md`
- Modify: `skills/promote/SKILL.md`
- Modify: `skills/lint/SKILL.md`
- Modify: `skills/register/SKILL.md`
- Modify: `skills/sync/SKILL.md`

- [ ] **Step 1: Create setup skill with binding modes**

Create `skills/setup/SKILL.md` with:

```markdown
---
name: setup
description: Use when creating or updating a LoreForge binding, configuring runtime state, binding an existing repo, or creating a native starter repo.
user-invocable: true
---

# Setup LoreForge Binding

Set up a LoreForge binding between a user-owned target repository and LoreForge runtime state.
```

Replace modes with:

```markdown
| Request | Mode | Default action |
|---|---|---|
| Existing repo or directory | Generic binding | Create registry binding and runtime state only |
| Missing target path | Generic binding | Create target directory and runtime state |
| New native starter | Native binding | Copy `templates/wiki`, initialize git, create runtime state |
| Existing native repo | Native binding | Register native paths and run protocol plus native lint |
```

Add this deterministic helper call:

```bash
bash <loreforge-root>/scripts/setup-binding.sh <name> <target_repo> \
  --target "notes=notes:General notes" \
  --default-target notes
```

State explicitly:

```markdown
Generic setup must not create `.loreforge/`, `00_System/`, `10_Inbox/`, `Cards/`, `Sources/`, or `MOCs/` in the target repo.
```

- [ ] **Step 2: Rewrite ingest skill around runtime packages**

In `skills/ingest/SKILL.md`, replace capture/process modes with:

```markdown
# Ingest Source

Ingest reads source material and creates a staged runtime package. It does not write the target repo by default.

## Workflow

1. Resolve the binding from `~/.config/loreforge/registry.toml`.
2. Read `target_repo`, `state_dir`, `read_roots`, `targets`, and `default_target`.
3. Fetch or read the source.
4. Store source reference and extracted text under `<state_dir>/packages/ingest/<id>/source/`.
5. Generate candidate files under `<state_dir>/packages/ingest/<id>/candidates/`.
6. Write `manifest.toml` with `[[sources]]` and `[[outputs]]`.
7. Leave the package with `status = "staged"`.
8. Hand off to `writeback` for target repo writes.
```

Use this generic package contract:

```toml
type = "ingest"
status = "staged"
binding = "<binding>"
created_at = "<ISO-8601 timestamp>"

[[sources]]
type = "url"
ref = "<source ref>"
snapshot = "extract"

[[outputs]]
kind = "file"
target = "<configured target>"
path = "<relative output path>"
candidate = "candidates/<file>.md"
mode = "create"
```

- [ ] **Step 3: Rewrite writeback skill around output validation**

In `skills/writeback/SKILL.md`, replace wiki staging language with:

```markdown
# Writeback Package

Writeback is the only generic workflow that writes to the target repository.

## Validation

Before writing, verify:

- package `binding` matches the selected binding
- every `target` exists in the binding config
- every output path remains inside the configured target path
- `mode = "create"` does not overwrite an existing file
- `mode = "update"` has a patch file and applies cleanly
- diffs are shown before any write

## Boundary

Writeback must not modify paths outside configured targets. It must not update native indexes or logs unless the binding is native and the user explicitly routes through `promote`.
```

- [ ] **Step 4: Mark query and promote native-only**

At the top of `skills/query/SKILL.md`, add:

```markdown
Query is native-only by default. Generic bindings should use `search`.
```

At the top of `skills/promote/SKILL.md`, add:

```markdown
Promote is native-only. Generic bindings use `writeback` as their stable write operation.
```

Ensure generic registry examples are not used in these native-only skills.

- [ ] **Step 5: Rewrite lint skill profiles**

In `skills/lint/SKILL.md`, replace execution with:

~~~markdown
## Execution

Protocol lint is the default:

```bash
bash <skill-path>/lint/scripts/lint-protocol.sh [--registry <path>] [binding]
```

Native lint is explicit:

```bash
bash <skill-path>/lint/scripts/lint-native.sh <target_repo>
```
~~~

List protocol checks and native checks exactly as described in the architecture spec.

- [ ] **Step 6: Rewrite register and sync scope**

In `skills/register/SKILL.md`, replace wiki registry wording with binding registry wording:

```markdown
Use `register` only for low-level edits to `~/.config/loreforge/registry.toml`. User-facing setup should use `setup`.
```

In `skills/sync/SKILL.md`, state:

```markdown
Sync operates on `target_repo` Git repositories. Runtime state under `state_dir` is local workflow state and is not synced by this skill.
```

- [ ] **Step 7: Run skill consistency grep**

Run:

```bash
rg -n "capture|10_Inbox/capture|ingest mode=capture|wiki instance" skills
```

Expected: no active core workflow text recommends capture or wiki-first setup. Remaining `wiki instance` matches must be native-template context or old migration context.

- [ ] **Step 8: Commit skill rewrites**

Run:

```bash
git add skills/setup/SKILL.md skills/ingest/SKILL.md skills/writeback/SKILL.md skills/query/SKILL.md skills/promote/SKILL.md skills/lint/SKILL.md skills/register/SKILL.md skills/sync/SKILL.md
git commit -m "docs: define binding-based skills"
```

Expected: commit succeeds.

## Task 7: User Documentation

**Files:**
- Modify: `README.md`
- Modify: `docs/install.md`
- Modify: `docs/config.md`
- Modify: `docs/schema.md`
- Modify: `docs/philosophy.md`
- Modify: `tests/README.md`

- [ ] **Step 1: Rewrite README core boundary**

In `README.md`, replace the core boundary diagram with:

```text
pamem
  agent-local memory
  preferences
  task state
  agent-local experience

LoreForge runtime state
  staged packages
  source extracts
  reports
  caches
  locks

User target repositories
  durable professional knowledge
  documentation
  notes
  source-grounded writeback results

LoreForge framework repo
  plugin metadata
  native starter template
  workflow specs
  skills
  deterministic helper scripts
```

Replace "Wiki Instance Shape" with "Native Repo Profile" and state:

```markdown
The native repo profile is optional. It enables query, promote, native lint, indexes, views, cards, sources, and MOCs. Generic bindings do not need to follow this structure.
```

- [ ] **Step 2: Rewrite first operations**

In `README.md`, use this operations table:

```markdown
| Operation | Scope | Purpose |
|---|---|---|
| Setup | Core | Create or update a binding and runtime state |
| Ingest | Core | Turn source material into a staged runtime package |
| Writeback | Core | Apply staged outputs to configured target paths |
| Search | Core | Search configured read roots |
| Lint protocol | Core | Check bindings, runtime state, and package safety |
| Query | Native | Use native indexes, views, cards, sources, and MOCs |
| Promote | Native | Promote native staged material into native stable structure |
| Lint native | Native | Check native repo structure and provenance/index health |
| Register | Core | Low-level registry maintenance |
| Sync | Core | Sync target repos with Git remotes |
```

- [ ] **Step 3: Rewrite install guide**

In `docs/install.md`, make the recommended flow:

~~~markdown
## Bind An Existing Repo

```text
setup binding name=notes path=~/notes target=notes:notes target=sources:references
```

Equivalent helper:

```bash
cd /home/cambricon/LoreForge
bash scripts/setup-binding.sh notes ~/notes \
  --target "notes=notes:General notes" \
  --target "sources=references:Source-grounded notes" \
  --default-target notes
```

Generic setup creates runtime state and a registry binding. It does not create LoreForge protocol directories inside the target repo.
~~~

Add native starter flow:

~~~markdown
## Create A Native Starter Repo

```bash
bash scripts/setup-binding.sh cs ~/wikis/cs \
  --mode native \
  --init-native-template \
  --target "writeback_staging=10_Inbox/writeback:Native staged writeback packages" \
  --target "ingest_staging=10_Inbox/ingest:Native staged ingest packages" \
  --default-target writeback_staging
```
~~~

- [ ] **Step 4: Rewrite config guide**

In `docs/config.md`, replace `[[wikis]]` examples with `[[bindings]]` examples from the architecture spec.

Include these required field definitions:

```markdown
- `name`: stable binding name
- `target_repo`: user-owned repository or directory
- `state_dir`: LoreForge runtime state directory
- `mode`: `generic` or `native`
- `read_roots`: paths searched inside `target_repo`
- `default_target`: fallback writeback target
- `[bindings.targets.<name>]`: allowed writeback target path and description
- `[bindings.native]`: native-only index, log, and view paths
```

- [ ] **Step 5: Update schema and philosophy**

In `docs/schema.md`, add this opening:

```markdown
This schema describes the optional native repo profile. It is not required for generic bindings.
```

In `docs/philosophy.md`, add:

```markdown
LoreForge core is a workflow layer over user-owned repositories. Native repos are an optional high-structure profile for query and promotion.
```

- [ ] **Step 6: Run documentation grep**

Run:

```bash
rg -n "capture|create-wiki|wiki instance|\\.loreforge/wiki|10_Inbox" README.md docs skills .claude .codex-plugin tests
```

Expected: remaining matches are native-profile descriptions, compatibility wrapper text, or migration history. No install path should instruct users to run `scripts/create-wiki.sh`.

- [ ] **Step 7: Commit docs**

Run:

```bash
git add README.md docs/install.md docs/config.md docs/schema.md docs/philosophy.md tests/README.md
git commit -m "docs: document binding-centric workflow"
```

Expected: commit succeeds.

## Task 8: Full Regression And Cleanup

**Files:**
- Inspect: all modified files

- [ ] **Step 1: Run all shell tests**

Run:

```bash
bash tests/setup/run.sh
bash tests/lint/run.sh
```

Expected output includes:

```text
PASS: setup-binding script syntax
PASS: generic binding creates runtime state and passes protocol lint
PASS: native binding creates starter repo and passes protocol lint
PASS: native template setup rejects non-empty target
PASS: protocol lint fixture is clean
PASS: protocol lint detects path traversal
PASS: templates/wiki is clean
PASS: bad manifest fixture reports expected issue
```

- [ ] **Step 2: Run syntax and whitespace checks**

Run:

```bash
bash -n scripts/setup-binding.sh
bash -n skills/lint/scripts/lint-protocol.sh
bash -n skills/lint/scripts/lint-native.sh
bash -n skills/lint/scripts/lint-wiki.sh
git diff --check
```

Expected: all commands exit `0`.

- [ ] **Step 3: Check no obsolete files remain**

Run:

```bash
test ! -e scripts/create-wiki.sh
test ! -e tests/install/run.sh
```

Expected: all commands exit `0`.

- [ ] **Step 4: Inspect final status**

Run:

```bash
git status --short --branch
```

Expected: only intentional changes are present. No temporary files under `/tmp`, `~/.local/state/loreforge`, or generated test directories are tracked.

- [ ] **Step 5: Commit final cleanup if needed**

If Step 4 shows only intentional uncommitted cleanup, run:

```bash
git add -A
git commit -m "chore: finish binding architecture migration"
```

Expected: commit succeeds or there is nothing left to commit.

## Self-Review Checklist

- Spec coverage: setup, ingest, writeback, search, protocol lint, native query/promote, runtime state, package format, source snapshot policy, and migration implications all map to tasks.
- File coverage: every old wiki-first surface found in README, docs, skills, setup script, lint, tests, router, and plugin metadata has a task.
- Safety coverage: tests include non-mutating generic setup, path traversal detection, native non-empty target rejection, and obsolete file removal checks.
- Commit coverage: each task has a commit boundary so failures can be isolated.

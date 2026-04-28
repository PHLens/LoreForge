# LoreForge Core Binding Architecture

Date: 2026-04-28

## Summary

LoreForge will pivot from a repo-centric wiki model to a binding-centric workflow model.

The core abstraction is a local binding between a user-owned target repository and LoreForge-managed runtime state. The target repository is not required to follow LoreForge's native wiki structure. LoreForge core provides setup, ingest, writeback, search, and protocol lint for any configured binding. LoreForge native repos remain supported as an optional profile that adds query, promote, native lint, indexes, views, and provenance conventions.

## Goals

- Allow users to bind existing Markdown or documentation repositories without reshaping them.
- Keep ingest and staging artifacts out of the user's repository by default.
- Make writeback explicit, configurable, and path-safe.
- Reduce lint burden for generic repositories.
- Preserve the native LoreForge repo template as the high-capability mode for structured query and promotion.
- Keep stable professional knowledge in the user's target repository, not in LoreForge runtime state.

## Non-Goals

- Do not require generic repositories to create `00_System/`, `10_Inbox/`, `Cards/`, `Sources/`, or `MOCs/`.
- Do not make repo-local `.loreforge/` configuration mandatory for generic bindings.
- Do not treat runtime packages, extracts, reports, or caches as durable knowledge.
- Do not keep `capture` as a core workflow step.
- Do not make query semantics available for arbitrary repositories without a native retrieval contract.

## Architecture

LoreForge has two layers.

### Core Layer

The core layer is available for generic and native bindings:

- `setup`: create or update a binding, configure runtime state, and configure read/write targets.
- `ingest`: read a source, extract useful material, and stage a package in runtime state.
- `writeback`: apply a staged package to configured target paths after validation and confirmation.
- `search`: perform lightweight search over configured read roots.
- `lint(protocol)`: validate bindings, runtime state, staged packages, and writeback safety.

The core layer knows nothing about `Cards`, `Sources`, `MOCs`, native indexes, or native views.

### Native Layer

The native layer is enabled only for bindings with `mode = "native"`:

- `query`: answer from native retrieval contracts such as indexes, views, provenance, cards, sources, and MOCs.
- `promote`: perform native stable-write transactions over cards, sources, MOCs, indexes, logs, and archives.
- `lint(native)`: validate native structure, index health, provenance health, and promotion rules.
- native starter template: keep `templates/wiki` as a native repo starter unless a later migration renames it.

Native repos remain the strongest LoreForge experience, but they are no longer the required shape for all LoreForge usage.

## Configuration Model

The local registry should move from `wikis` terminology to `bindings` terminology.

Example generic binding:

```toml
default = "notes"

[[bindings]]
name = "notes"
target_repo = "/home/me/notes"
state_dir = "~/.local/state/loreforge/notes"
mode = "generic"
default_target = "notes"
read_roots = ["."]

[bindings.targets.notes]
path = "notes"
description = "General durable notes"

[bindings.targets.sources]
path = "references"
description = "Source-grounded notes"
```

Example native binding:

```toml
[[bindings]]
name = "cs"
target_repo = "/home/me/cs-wiki"
state_dir = "~/.local/state/loreforge/cs"
mode = "native"
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

Rules:

- `target_repo` is the user-owned repository or directory.
- `state_dir` defaults to `~/.local/state/loreforge/<binding>`, but users may override it.
- Generic `targets` are the only durable paths that writeback may modify; native `targets` are review staging paths under `10_Inbox/`.
- `read_roots` define the search and context boundary.
- `mode = "generic"` enables core workflows only.
- `mode = "native"` enables core workflows plus native query, promote, and native lint.
- Generic setup does not write repo-local `.loreforge/` files unless the user explicitly asks for portable config.

## Runtime State

Runtime state defaults to:

```text
~/.local/state/loreforge/<binding>/
```

It contains workflow artifacts only:

```text
packages/
  ingest/
  writeback/
  archive/
reports/
cache/
locks/
tmp/
state.toml
```

Runtime state may store:

- staged packages
- extracted source text
- optional source snapshots
- generated candidates
- patch files
- lint and writeback reports
- rebuildable caches
- locks and temporary files
- run metadata such as recent package IDs

Runtime state must not store:

- stable professional knowledge
- user preferences
- agent long-term memory
- the user's repository structure as a required schema
- a second authoritative copy of target repository content

## Workflow

### Setup

`setup` creates or updates a binding. For generic repositories it should:

1. Resolve `name`, `target_repo`, `state_dir`, `read_roots`, and configured writeback targets.
2. Create runtime state.
3. Update the local registry after showing diffs for existing entries.
4. Run protocol lint.
5. Avoid modifying the target repository unless the user explicitly requests repo-local portable config.

For native starter creation, `setup` may create a new repo from the native template and register it as `mode = "native"`.

### Ingest

`ingest source` replaces the old `capture` flow.

It should:

1. Fetch or read the source.
2. Extract useful text and metadata.
3. Create an ingest package in runtime state.
4. Generate candidates and output plans.
5. Leave the package staged by default.
6. Avoid writing to the target repository.

`capture` should be removed from core docs and routing. A deferred ingestion case can be represented as a low-priority staged ingest package, but it should not restore `capture` as an independent abstraction.

### Writeback

`writeback` is the only generic operation that writes to the target repository.

It should:

1. Read a staged package.
2. Validate every output against configured targets.
3. Prevent path traversal outside the target repo and target path.
4. Detect create/update conflicts.
5. Show the write plan and diff.
6. Ask for confirmation before writing.
7. Mark the package as written or archive it after success.

### Search

`search` is available for generic and native bindings. It performs lightweight filesystem and Markdown search over configured `read_roots`. It does not promise native query semantics.

### Query

`query` is native-only by default. It requires a native retrieval contract such as an index, views, provenance conventions, cards, sources, and MOCs.

Generic repositories can still be searched, but they should not be presented as full LoreForge query targets unless the user explicitly upgrades them to native mode.

### Promote

`promote` is native-only. Generic repositories use `writeback` as their stable write operation.

## Package Format

Generic packages express source material, candidate files, patches, and writeback outputs. They do not use `Cards`, `Sources`, or `MOCs` as core package structure.

Example layout:

```text
~/.local/state/loreforge/<binding>/packages/ingest/<id>/
  manifest.toml
  source/
    ref.toml
    extract.md
    original.*
  candidates/
    example.md
  patches/
    0001-example.patch
```

Example manifest:

```toml
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

[[outputs]]
kind = "patch"
target = "sources"
path = "article-index.md"
patch = "patches/0001.patch"
mode = "update"
```

Required writeback validation:

- package `binding` matches the selected binding
- every `target` exists in the binding config
- every output path stays inside the configured target path
- `mode = "create"` does not overwrite existing files
- `mode = "update"` can apply cleanly
- diffs are shown before writing

Native packages may add native-specific conventions for index, log, provenance, and promotion, but core writeback must not depend on them.

## Source Snapshot Policy

Source snapshots are workflow evidence, not stable knowledge.

Default policy:

```toml
source_ref_policy = "always"
extract_policy = "on_ingest"
snapshot_policy = "explicit"
archive_policy = "explicit"
```

Meaning:

- Ingest stores source references and extracted text needed for staged processing.
- Full source snapshots are stored only when the user asks or a binding policy requires them.
- Durable source notes are written to the target repo only through writeback.
- Source snapshots are never written into generic target repos by default.

## Lint

Lint is split into protocol lint and native lint.

### Protocol Lint

Protocol lint is available for all bindings. It checks:

- registry syntax and binding resolution
- target repository existence
- runtime state readability and writability
- configured target path existence or creatability
- read root validity
- staged package manifest validity
- output target validity
- path traversal prevention
- writeback conflict detectability
- lock, cache, and report directory health

Protocol lint does not require native wiki structure.

### Native Lint

Native lint runs only for native bindings. It checks:

- native index, log, and views
- native template structure
- card, source, and MOC conventions
- provenance and index drift
- native package promotion rules

Existing lint fixtures for `templates/wiki` should become native lint fixtures, not the definition of all LoreForge health checks.

## Testing Strategy

Tests should cover:

- setup binding fixture
- runtime state creation fixture
- ingest package fixture
- writeback path safety fixture
- protocol lint fixture
- generic repo fixture with arbitrary target paths
- native template fixture
- native lint fixture
- compatibility fixture for any temporarily supported legacy wiki registry format

The most important safety tests are path traversal, accidental overwrite, package binding mismatch, and target-name mismatch.

## Migration Implications

The current repository still contains wiki-centric language and files. Implementation should migrate in stages:

1. Update docs and routing to describe binding-centric core and native profile.
2. Replace create-wiki-first installation with setup binding as the default.
3. Convert the setup script into a binding/runtime initializer.
4. Remove `capture` from primary docs and skill routing.
5. Split lint into protocol and native profiles.
6. Move query and promote language under native profile.
7. Keep `templates/wiki` as native starter until a separate rename decision is approved.

Existing uncommitted setup work should be reviewed against this design before being kept, rewritten, or discarded.

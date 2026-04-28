---
name: ingest
description: Use when reading source material, extracting useful content, and staging a LoreForge package without writing stable knowledge.
user-invocable: true
---

# Ingest Source

Ingest reads source material and creates a staged package. It does not write stable knowledge by default.

Use `ingest` for URLs, local files, articles, papers, docs pages, repository notes, transcripts, datasets, or user-provided source material that may become durable knowledge after review.

## Workflow

1. Resolve the binding from `~/.config/loreforge/registry.toml`.
2. Read `target_repo`, `state_dir`, `read_roots`, `targets`, and `default_target`.
3. Confirm the source is allowed to be read and fits inside configured repository boundaries when it is local target-repo content.
4. Fetch or read the source.
5. Extract useful text, source metadata, title, author, URL or path, access time, and any relevant provenance.
6. If `mode = "generic"`, create a runtime package under `<state_dir>/packages/ingest/<id>/`.
7. If `mode = "native"`, create a review package under `<target_repo>/10_Inbox/ingest/<id>/` or the configured native ingest path.
8. Store heavy extracts, snapshots, reports, and temporary evidence under `state_dir` when useful.
9. Generate candidate files in the selected package.
10. Write the package manifest for the selected backend.
11. Leave the package with `status = "staged"`.
12. Hand off to `writeback` for generic target writes, or `promote` for native stable promotion after review.

## Package Layout

Generic runtime layout:

```text
<state_dir>/packages/ingest/<id>/
  manifest.toml
  source/
    ref.toml
    extract.md
    original.*
  candidates/
    <candidate>.md
  patches/
    0001-<change>.patch
```

`source/original.*` is optional. Store full source snapshots only when the user asks or the binding policy requires them. Source references and extracts are workflow evidence, not durable repository content.

Native review layout:

```text
<target_repo>/10_Inbox/ingest/<id>/
  manifest.md
  Sources/<Type>/<source>.md
  Cards/<candidate>.md
  MOCs/<candidate>.md
  Deltas/
```

Native packages are repo-local review artifacts. They are not stable knowledge until `promote` moves approved material into stable native paths and updates the index, log, and archive.

## Manifest Contract

Every generic ingest package must include `manifest.toml`.

Minimum generic manifest:

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

`[[sources]]` entries describe where the material came from. Use `type` values such as `url`, `file`, `repo`, `paper`, `docs`, `dataset`, `conversation`, or `user_material`.

`[[outputs]]` entries describe proposed writes. Each output must use a configured target name. `path` is relative to that target path, not to the repository root. `candidate` and `patch` paths are package-relative.

Use `mode = "create"` for new files and `mode = "update"` for patch-based updates. Writeback validates conflicts and path safety before anything reaches the target repository.

Native ingest packages use Markdown frontmatter:

```markdown
---
type: ingest
source_type: <source type>
status: staged
created: YYYY-MM-DD
provenance:
  - <source path/url>
candidate_notes:
  - Sources/<Type>/<source>.md
  - Cards/<candidate-card>.md
updates:
  - 00_System/+Wiki Index.md
promotion_reason: <why this should become stable native knowledge>
---
```

`candidate_notes` are package-relative paths. `updates` are target-repo-relative paths changed during promotion.

## Candidate Guidance

Candidates should be small, source-grounded, and ready for review. Prefer one durable concept, summary, or update per candidate file. Keep source attribution in the candidate when it will matter after writeback.

For generic bindings, do not assume native directories such as `Cards`, `Sources`, or `MOCs`. Choose output targets from the binding configuration.

For native bindings, ingest stages candidates in `10_Inbox/ingest/` using native conventions. It must not write stable `Cards/`, `Sources/`, `MOCs/`, indexes, logs, or archive entries directly.

## Boundary

This skill must not:

- write stable knowledge into `target_repo` by default
- create repository structure for generic bindings
- silently update native indexes, logs, or views
- store agent-local experience, preferences, or task state
- save full chat transcripts
- commit or push git changes

It may store generic packages under `state_dir`, native review packages under the configured native ingest staging path, and runtime extracts, snapshots, reports, or temporary evidence under `state_dir`.

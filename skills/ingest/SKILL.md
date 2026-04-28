---
name: ingest
description: Use when reading source material, extracting useful content, and staging a LoreForge runtime package without writing the target repository by default.
user-invocable: true
---

# Ingest Source

Ingest reads source material and creates a staged runtime package. It does not write the target repo by default.

Use `ingest` for URLs, local files, articles, papers, docs pages, repository notes, transcripts, datasets, or user-provided source material that may become durable knowledge after review.

## Workflow

1. Resolve the binding from `~/.config/loreforge/registry.toml`.
2. Read `target_repo`, `state_dir`, `read_roots`, `targets`, and `default_target`.
3. Confirm the source is allowed to be read and fits inside configured repository boundaries when it is local target-repo content.
4. Fetch or read the source.
5. Extract useful text, source metadata, title, author, URL or path, access time, and any relevant provenance.
6. Create a package under `<state_dir>/packages/ingest/<id>/`.
7. Store source references and extracted text under `<state_dir>/packages/ingest/<id>/source/`.
8. Generate candidate files under `<state_dir>/packages/ingest/<id>/candidates/`.
9. Generate patch files under `<state_dir>/packages/ingest/<id>/patches/` when an update is more appropriate than a new file.
10. Write `manifest.toml` with `[[sources]]` and `[[outputs]]`.
11. Leave the package with `status = "staged"`.
12. Hand off to `writeback` for target repo writes.

## Package Layout

Recommended generic layout:

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

## Manifest Contract

Every ingest package must include `manifest.toml`.

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

## Candidate Guidance

Candidates should be small, source-grounded, and ready for review. Prefer one durable concept, summary, or update per candidate file. Keep source attribution in the candidate when it will matter after writeback.

For generic bindings, do not assume native directories such as `Cards`, `Sources`, or `MOCs`. Choose output targets from the binding configuration.

For native bindings, ingest may generate candidates that match native conventions, but the package is still staged in runtime state and remains unwritten until a write workflow is explicitly chosen.

## Boundary

This skill must not:

- write files into `target_repo` by default
- create repository structure for generic bindings
- silently update native indexes, logs, or views
- store agent-local experience, preferences, or task state
- save full chat transcripts
- commit or push git changes

It may store source references, extracts, candidates, patches, reports, and package metadata under `state_dir`.

---
name: writeback
description: Use when applying staged LoreForge package outputs to configured target repository paths after validation and user approval.
user-invocable: true
---

# Writeback Package

Writeback is the only generic workflow that writes to the target repository.

Writeback consumes staged runtime packages, validates their declared outputs, previews the diff, and applies approved creates or updates inside configured targets only.

## Inputs

Acceptable inputs:

- staged ingest package under `<state_dir>/packages/ingest/<id>/`
- staged writeback package under `<state_dir>/packages/writeback/<id>/`
- explicit `manifest.toml` path
- user-approved output subset from a staged package

Packages must declare outputs in `manifest.toml` with `[[outputs]]` entries.

## Validation

Before writing, verify:

- package `binding` matches the selected binding
- every `target` exists in the binding config
- every output path remains inside the configured target path
- `mode = "create"` does not overwrite an existing file
- `mode = "update"` has a patch file and applies cleanly
- diffs are shown before any write

Also verify that candidate and patch paths remain inside the package directory and that the selected binding resolves to the expected `target_repo` and `state_dir`.

## Workflow

1. Resolve the selected binding from `~/.config/loreforge/registry.toml`.
2. Read `target_repo`, `state_dir`, configured `targets`, and `default_target`.
3. Read the staged package `manifest.toml`.
4. Validate the package binding, status, sources, outputs, candidate files, and patch files.
5. Resolve each output target as `<target_repo>/<configured target path>/<output path>`.
6. Reject any path that escapes the configured target path or target repository.
7. Detect create conflicts and update applicability.
8. Build a write plan listing creates, updates, skips, and package status changes.
9. Show the write plan and diff preview.
10. Ask for explicit user approval before writing.
11. Apply only the approved outputs.
12. Mark the package as written or move it under `<state_dir>/packages/archive/` after success.
13. Report written, updated, skipped, archived, and any follow-up lint recommendation.

## Output Contract

Generic output examples:

```toml
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
patch = "patches/0001-article-index.patch"
mode = "update"
```

`target` must name a configured binding target. `path` is relative to that target. `candidate` and `patch` are relative to the package directory.

## Boundary

Writeback must not modify paths outside configured targets. It must not update native indexes or logs unless the binding is native and the user explicitly routes through `promote`.

This skill must not:

- write unvalidated package outputs
- invent target paths that are not configured in the binding
- write runtime extracts or package metadata into the target repository
- store agent-local memory or task state
- commit or push git changes

It may update runtime package status after successful writes.

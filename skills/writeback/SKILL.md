---
name: writeback
description: Use when applying generic staged outputs to configured target paths, or staging native conversation/query synthesis under 10_Inbox/writeback.
user-invocable: true
---

# Writeback Package

Writeback has mode-specific semantics.

For generic bindings, writeback consumes staged runtime packages, validates their declared outputs, previews the diff, and applies approved creates or updates inside configured targets only.

For native bindings, writeback creates a review package under `10_Inbox/writeback/` or the configured native writeback staging path. It must not write stable native `Cards/`, `Sources/`, `MOCs/`, indexes, logs, or archive entries directly.

## Inputs

Acceptable inputs:

- staged ingest package under `<state_dir>/packages/ingest/<id>/`
- staged writeback package under `<state_dir>/packages/writeback/<id>/`
- explicit `manifest.toml` path
- user-approved output subset from a staged package
- native conversation or query synthesis that may become durable knowledge

Generic packages must declare outputs in `manifest.toml` with `[[outputs]]` entries. Native writeback creates `manifest.md` plus candidate notes under the native writeback staging package.

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
3. If the binding is native, create a staged package under the configured native writeback path and stop before stable writes.
4. Read the staged generic package `manifest.toml`.
5. Validate the package binding, status, sources, outputs, candidate files, and patch files.
6. Resolve each output target as `<target_repo>/<configured target path>/<output path>`.
7. Reject any path that escapes the configured target path or target repository.
8. Detect create conflicts and update applicability.
9. Build a write plan listing creates, updates, skips, and package status changes.
10. Show the write plan and diff preview.
11. Ask for explicit user approval before writing.
12. Apply only the approved outputs.
13. Mark the package as written or move it under `<state_dir>/packages/archive/` after success.
14. Report written, updated, skipped, archived, and any follow-up lint recommendation.

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

Native staged writeback packages use Markdown frontmatter:

```markdown
---
type: writeback
source_type: conversation_synthesis
status: staged
created: YYYY-MM-DD
provenance:
  - conversation: <short description>
candidate_notes:
  - Cards/<candidate-card>.md
updates:
  - 00_System/+Wiki Index.md
promotion_reason: <why this should become stable native knowledge>
---
```

Candidate files live inside the same package. `candidate_notes` are package-relative paths; `updates` are target-repo-relative paths changed by promotion.

## Boundary

Writeback must not modify paths outside configured targets. In native mode, configured targets are staging targets only. Stable native writes require `promote`.

This skill must not:

- write unvalidated package outputs
- invent target paths that are not configured in the binding
- write generic runtime extracts or package metadata into stable target paths
- write native stable `Cards/`, `Sources/`, `MOCs/`, indexes, logs, or archive entries directly
- store agent-local memory or task state
- commit or push git changes

It may update generic runtime package status after successful writes, or create native review packages under the configured writeback staging path.

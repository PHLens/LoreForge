---
name: setup
description: Use when creating or updating a LoreForge binding, configuring runtime state, binding an existing repo, or creating a native starter repo.
user-invocable: true
---

# Setup LoreForge Binding

Set up a LoreForge binding between a user-owned target repository and LoreForge runtime state.

`setup` is the user-facing entry point for creating, adopting, or updating bindings. A binding records where durable content lives (`target_repo`), where workflow state lives (`state_dir`), what paths may be searched (`read_roots`), and which configured targets may receive writeback.

Adopting an existing repository is binding setup, not wiki creation. Do not reshape a user's existing repository just to make it usable by LoreForge core workflows.

## Modes

| Request | Mode | Default action |
|---|---|---|
| Existing repo or directory | Generic binding | Create registry binding and runtime state only |
| Missing target path | Generic binding | Create target directory and runtime state |
| New native starter | Native binding | Copy `templates/wiki`, initialize git, create runtime state, register staging targets |
| Existing native repo | Native binding | Register native paths and run protocol plus native lint |

Generic mode supports setup, ingest, writeback, search, and protocol lint over configured repository paths. It does not require native LoreForge structure.

Native mode is an optional profile for repositories that use LoreForge's native template and retrieval contract. It adds query, promote, native lint, native indexes, views, cards, sources, MOCs, and native logs. Native writeback targets are staging paths under `10_Inbox/`, not stable `Cards/`, `Sources/`, or `MOCs/`.

Generic setup must not create `.loreforge/`, `00_System/`, `10_Inbox/`, `Cards/`, `Sources/`, or `MOCs/` in the target repo.

## Helper

For empty or new generic targets, call the deterministic helper:

```bash
bash <loreforge-root>/scripts/setup-binding.sh <name> <target_repo> \
  --target "notes=notes:General notes" \
  --default-target notes
```

Use repeatable `--read-root` and `--target "name=path:description"` options to match the target repository's existing layout. The helper creates runtime state and writes the binding registry entry.

For native starter creation, call the same helper with native mode:

```bash
bash <loreforge-root>/scripts/setup-binding.sh <name> <target_repo> \
  --mode native \
  --init-native-template \
  --target "writeback_staging=10_Inbox/writeback:Native staged writeback packages" \
  --target "ingest_staging=10_Inbox/ingest:Native staged ingest packages" \
  --default-target writeback_staging
```

## Workflow

1. Collect the binding name, `target_repo`, mode, `state_dir`, `read_roots`, configured targets, and `default_target`.
2. Decide whether the binding is generic or native.
3. For generic setup, preserve the target repository layout and create only the target directory if it is missing.
4. For native starter setup, require a missing or empty target path before copying `templates/wiki`.
5. Run `scripts/setup-binding.sh` with explicit targets and default target.
   - Generic targets may point at durable user-chosen writeback directories.
   - Native targets must point at staging directories such as `10_Inbox/writeback` and `10_Inbox/ingest`.
6. If updating an existing binding, report the old and new registry values before relying on the updated entry.
7. Run protocol lint on the binding.
8. For native bindings, also run native lint against `target_repo`.
9. Report the binding name, mode, target repository, runtime state directory, read roots, configured targets, and default target.

## Registry

Bindings are stored in:

```text
~/.config/loreforge/registry.toml
```

Each binding should use `[[bindings]]` with:

- `name`
- `target_repo`
- `state_dir`
- `mode`
- `default_target`
- `read_roots`
- `[bindings.targets.<name>]` tables for allowed writeback targets
- optional `[bindings.native]` for native-only index, log, and view paths

Use `register` only for low-level manual registry maintenance. Use `setup` for user-facing binding creation and adoption.

## Boundary

This skill must not:

- put runtime packages or extracts in the target repository
- create native directories for a generic binding
- store agent-local memory or task state
- commit or push git changes
- overwrite an existing non-empty native target when creating a starter

It may create or update the local registry and runtime state. It may create a missing generic target directory without adding LoreForge structure inside it.

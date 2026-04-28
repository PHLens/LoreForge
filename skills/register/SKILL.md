---
name: register
description: Use only for low-level LoreForge binding registry edits in ~/.config/loreforge/registry.toml.
user-invocable: true
---

# Register Binding

Use `register` only for low-level edits to `~/.config/loreforge/registry.toml`. User-facing setup should use `setup`.

`register` exists for direct registry maintenance when the user already knows the desired binding fields. It does not replace setup, runtime state initialization, or lint.

For native bindings, registry targets must be staging targets such as `10_Inbox/writeback` or `10_Inbox/ingest`. Do not register stable native `Cards/`, `Sources/`, or `MOCs/` as writeback targets.

## Purpose

Agents should not guess binding paths. They should discover bindings through:

```text
~/.config/loreforge/registry.toml
```

This skill defines the procedure for adding, updating, or verifying `[[bindings]]` entries in that registry.

## Hard Boundary

This skill must not:

- modify target repository content
- initialize runtime state
- modify `pamem`
- push to Git remotes
- overwrite an existing registry entry without reporting the diff

It may:

- create `~/.config/loreforge/`
- create `registry.toml` from template
- add or update a binding entry
- verify the local `target_repo` path
- verify `state_dir` when it already exists
- recommend `setup` when runtime state or target initialization is needed

## Input

Required:

- `name`
- `target_repo`
- `state_dir`
- `mode`
- `default_target`
- at least one target

Optional:

- `remote`
- `description`
- `read_roots`
- native index, log, and views paths

Example:

```text
register binding name=notes target_repo=/path/to/notes state_dir=~/.local/state/loreforge/notes mode=generic target=notes:notes default_target=notes
```

## Registry Entry

```toml
[[bindings]]
name = "notes"
target_repo = "/path/to/notes"
state_dir = "~/.local/state/loreforge/notes"
mode = "generic"
description = "General notes binding"
default_target = "notes"
read_roots = ["."]

[bindings.targets.notes]
path = "notes"
description = "General durable notes"
```

Native bindings may also include:

```toml
[bindings.native]
index_file = "00_System/+Wiki Index.md"
log_file = "00_System/Wiki Log.md"
views_dir = "00_System/Views"
```

Native target example:

```toml
[bindings.targets.writeback_staging]
path = "10_Inbox/writeback"
description = "Native staged writeback packages"
```

## Workflow

1. Locate registry at `~/.config/loreforge/registry.toml`.
2. If missing, create the parent directory and copy from `templates/config/registry.toml`.
3. Check whether an entry with the same `name` already exists.
4. If it exists, show old and new values before updating.
5. If it does not exist, append a new `[[bindings]]` entry.
6. Verify `target_repo` is an absolute path or can be resolved safely.
7. Verify `state_dir` is an absolute path or can be resolved safely.
8. Verify every `read_roots` entry and target path stays inside `target_repo`.
9. Verify `default_target` names a configured target.
10. Report the registered binding and recommend protocol lint.

## Validation

A registry entry is valid when:

- `name` is non-empty
- `target_repo` is absolute
- `state_dir` is absolute or uses `~`
- `mode` is `generic` or `native`
- `read_roots` entries do not escape `target_repo`
- `default_target` is non-empty and configured
- every `[bindings.targets.<name>]` has a safe relative `path`
- native targets do not point at stable native `Cards/`, `Sources/`, or `MOCs/`
- `remote` is either empty or a valid Git remote string

Use `setup` instead when the user wants to create target directories, initialize runtime state, create a native starter, or adopt an existing repository through the normal flow.

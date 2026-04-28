---
name: register
description: Use when registering, updating, or verifying a LoreForge wiki path, name, default view, or Git remote in ~/.config/loreforge/registry.toml.
user-invocable: true
---

# Register LoreForge Wiki

Register a wiki instance in the local LoreForge registry.

## Purpose

Agents should not guess wiki paths. They should discover wiki instances through:

```text
~/.config/loreforge/registry.toml
```

This skill defines the procedure for adding or updating entries in that registry.

## Hard Boundary

This skill must not:

- modify wiki knowledge content
- modify `pamem`
- push to Git remotes
- overwrite an existing registry entry without reporting the diff

It may:

- create `~/.config/loreforge/`
- create `registry.toml` from template
- add or update a wiki entry
- verify the local wiki path
- verify `.loreforge/wiki.toml`
- recommend cloning when only a remote exists

## Input

Required:

- `name`
- `path`

Optional:

- `remote`
- `description`
- `default_view`

Example:

```text
register wiki name=cs path=/path/to/cs-wiki remote=git@github.com:OWNER/cs-wiki.git default_view=query
```

## Registry Entry

```toml
[[wikis]]
name = "cs"
path = "/path/to/cs-wiki"
remote = "git@github.com:OWNER/cs-wiki.git"
description = "Computer science, GPU, ML systems, PyTorch"
default_view = "query"
```

## Workflow

1. Locate registry at `~/.config/loreforge/registry.toml`.
2. If missing, create parent directory and copy from `templates/config/registry.toml`.
3. Check whether an entry with the same `name` already exists.
4. If it exists, show old and new values before updating.
5. If it does not exist, append a new `[[wikis]]` entry.
6. Verify `path`:
   - if path exists, check for `.loreforge/wiki.toml`
   - if path does not exist but `remote` exists, ask before cloning
   - if neither path nor remote works, stop and ask for correction
7. Report the registered wiki and default view.

## First-Time Setup

Recommended manual setup:

```bash
mkdir -p ~/.config/loreforge
cp templates/config/registry.toml ~/.config/loreforge/registry.toml
```

Then edit the registry entry.

## Validation

A registry entry is valid when:

- `name` is non-empty
- `path` is absolute
- `default_view` is non-empty
- `remote` is either empty or a valid Git remote string

If the wiki path exists, it should contain:

```text
.loreforge/wiki.toml
AGENTS.md
00_System/Vault Map.md
```

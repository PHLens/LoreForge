# Configuration

LoreForge uses a machine-local binding registry. Native targets may also carry optional target-local metadata for the native profile.

## Local Registry

Path:

```text
~/.config/loreforge/registry.toml
```

Purpose:

- machine-local discovery
- maps binding names to user-owned target repositories
- records LoreForge runtime state locations
- defines search roots and writeback targets
- records optional Git remotes and native profile paths

Template:

```text
templates/config/registry.toml
```

Generic binding example:

```toml
default = "notes"

[[bindings]]
name = "notes"
target_repo = "/home/me/notes"
state_dir = "~/.local/state/loreforge/notes"
mode = "generic"
remote = "git@github.com:OWNER/notes.git"
description = "General notes repository"
default_target = "notes"
read_roots = ["."]

[bindings.targets.notes]
path = "docs"
description = "General durable notes"

[bindings.targets.sources]
path = "references"
description = "Source-grounded notes"
```

Native binding example:

```toml
[[bindings]]
name = "cs"
target_repo = "/home/me/cs-native"
state_dir = "~/.local/state/loreforge/cs"
mode = "native"
remote = "git@github.com:OWNER/cs-native.git"
description = "Native LoreForge knowledge repository"
default_target = "cards"
read_roots = ["."]

[bindings.targets.cards]
path = "Cards"
description = "Native cards"

[bindings.targets.sources]
path = "Sources"
description = "Native source notes"

[bindings.native]
index_file = "00_System/+Wiki Index.md"
log_file = "00_System/Wiki Log.md"
views_dir = "00_System/Views"
```

The registry is not a knowledge store. Do not put notes, findings, summaries, source text, or agent memory in it.

## Binding Fields

| Field | Purpose |
|---|---|
| `name` | Stable local binding name used by LoreForge operations |
| `target_repo` | User-owned repository or directory that holds durable content |
| `state_dir` | LoreForge-managed runtime directory for packages, reports, caches, locks, and temporary files |
| `mode` | `generic` for core workflows only, or `native` for core workflows plus native query/promote/native lint |
| `default_target` | Writeback target used when a package does not select another configured target |
| `read_roots` | Relative paths inside `target_repo` that search and context gathering may read |
| `[bindings.targets.*]` | Named writeback target tables; each target defines a safe relative `path` and optional `description` |
| `[bindings.native]` | Native-only paths such as `index_file`, `log_file`, and `views_dir` |

`targets` are the only target-repo paths that writeback may modify. `read_roots` are the search boundary. Both are relative to `target_repo` and must stay inside it.

## Setup And Register

Use `setup` as the user-facing entry point for binding creation and adoption:

```text
setup binding name=notes path=/home/me/notes
```

`setup` creates runtime state, updates the registry, and can create an optional native starter when requested.

Use `register` only for low-level registry maintenance, such as adding or correcting a `[[bindings]]` block when runtime state and target paths already exist. `register` does not replace setup, runtime initialization, or lint.

## Native Target Metadata

Generic bindings do not require target-local LoreForge metadata.

Native targets may include:

```text
<target_repo>/.loreforge/wiki.toml
```

Purpose:

- describes the native profile inside that target repo
- declares entry files, views, indexes, logs, and path conventions
- supports native query, promote, and native lint

The file name is historical. It belongs to the optional native profile, not to generic binding setup.

Template:

```text
templates/wiki/.loreforge/wiki.toml
```

Example:

```toml
schema_version = "0.1"
name = "cs"
description = "Computer science native target"
agents_file = "AGENTS.md"
vault_map = "00_System/Vault Map.md"
schema_file = "00_System/Schema.md"
index_file = "00_System/+Wiki Index.md"
log_file = "00_System/Wiki Log.md"
views_dir = "00_System/Views"
default_view = "query"

[views]
default = "00_System/Views/default.md"
query = "00_System/Views/query.md"
ingest = "00_System/Views/ingest.md"
writeback = "00_System/Views/writeback.md"
promote = "00_System/Views/promote.md"
maintenance = "00_System/Views/maintenance.md"

[paths]
inbox = "10_Inbox"
ingest = "10_Inbox/ingest"
writeback = "10_Inbox/writeback"
cards = "Cards"
sources = "Sources"
mocs = "MOCs"
archive = "Archive"
```

## Discovery Flow

1. Agent reads `~/.config/loreforge/registry.toml`.
2. Agent resolves the requested binding name, or the registry `default`.
3. Agent loads `target_repo`, `state_dir`, `mode`, `read_roots`, targets, and native fields.
4. Core operations use the target repo plus runtime state.
5. Native operations additionally read native target metadata and views when present.
6. The selected operation reports the binding it used.

Agents should not guess target paths when the registry is available.

## Git Support

Git remotes are supported as persistence and synchronization backends for target repositories.

Preferred mode:

```text
Git remote -> local clone -> local read/search/write -> git sync
```

Agents should not query the remote directly for every answer.

Use the `sync` skill for conservative pull/status/commit/push workflows.

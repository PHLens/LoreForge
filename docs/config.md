# Configuration

LoreForge uses two configuration layers.

## Local Registry

Path:

```text
~/.config/loreforge/registry.toml
```

Purpose:

- machine-local discovery
- maps wiki names to local paths
- records optional Git remotes
- defines default wiki and default views

Template:

```text
templates/config/registry.toml
```

Example:

```toml
default = "cs"

[[wikis]]
name = "cs"
path = "/path/to/cs-wiki"
remote = "git@github.com:OWNER/cs-wiki.git"
description = "Computer science, GPU, ML systems, PyTorch"
default_view = "query"
```

The registry is not a knowledge store. Do not put notes, findings, summaries, or agent memory in it.

## Wiki-Local Metadata

Path:

```text
<wiki>/.loreforge/wiki.toml
```

Purpose:

- describes the wiki instance
- declares entry files and task views
- records path conventions
- optionally records Git defaults

Template:

```text
templates/wiki/.loreforge/wiki.toml
```

Example:

```toml
schema_version = "0.1"
name = "cs"
description = "Computer science wiki"
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
capture = "10_Inbox/capture"
ingest = "10_Inbox/ingest"
writeback = "10_Inbox/writeback"
cards = "Cards"
sources = "Sources"
mocs = "MOCs"
archive = "Archive"
```

## Discovery Flow

1. Agent reads `~/.config/loreforge/registry.toml`.
2. Agent resolves the requested wiki name or registry default.
3. Agent enters the local `path`.
4. Agent reads `<wiki>/.loreforge/wiki.toml`.
5. Agent reads the wiki `AGENTS.md`.
6. Agent follows the selected task view.

## GitHub Support

GitHub remotes are supported as persistence and sync backends.

Preferred mode:

```text
GitHub remote -> local clone -> local read/search/write -> git sync
```

Agents should not query GitHub directly for every answer.

Use the `sync` skill for conservative pull/status/commit/push workflows.

## Registration

Use the `register` skill to create or update registry entries.

First-time manual setup:

```bash
mkdir -p ~/.config/loreforge
cp templates/config/registry.toml ~/.config/loreforge/registry.toml
```

# Configuration

LoreForge can use explicit paths, environment variables, or local config files.
The core `loreforge-wiki` skill should prefer a user-provided domain path, then
`WIKI_PATH`, then `~/wiki`.

## Local Registry

Path:

```text
~/.config/loreforge/registry.toml
```

Purpose:

- machine-local discovery
- maps wiki names to local paths
- records optional Git remotes
- defines a default wiki

Template:

```text
templates/config/registry.toml
```

Example:

```toml
default = "cs"

[[wikis]]
name = "cs"
path = "/home/phlens/wiki"
remote = "git@github.com:PHLens/cs-wiki.git"
description = "Computer science, GPU, ML systems, PyTorch"
```

The registry is not a knowledge store. Do not put notes, findings, summaries, or agent memory in it.

## Wiki-Local Metadata

Path:

```text
<wiki>/.loreforge/wiki.toml
```

Purpose:

- describes the wiki instance
- declares entry files
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
system_dir = "00_System"
domains_dir = "Domains"

[paths]
domains = "Domains"
```

## Discovery Flow

1. Use the user-provided wiki/domain path, if given.
2. Otherwise use `WIKI_PATH` and the requested domain name.
3. Otherwise read `~/.config/loreforge/registry.toml`, if available.
4. Otherwise fall back to `~/wiki`.
5. Enter `Domains/<domain>/`.
6. Orient on `SCHEMA.md`, `index.md`, recent `log.md`, and relevant pages.

## GitHub Support

GitHub remotes are supported as persistence and sync backends.

Preferred mode:

```text
GitHub remote -> local clone -> local read/search/write -> git synchronization
```

Agents should not query GitHub directly for every answer.

Use normal git workflows for pull/status/commit/push until a smaller sync helper
is justified.

## Registration

Create or update registry entries manually until a smaller domain-management
helper is justified.

First-time manual setup:

```bash
mkdir -p ~/.config/loreforge
cp templates/config/registry.toml ~/.config/loreforge/registry.toml
```

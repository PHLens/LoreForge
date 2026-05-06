# Configuration

LoreForge can use explicit paths, environment variables, or local config files.
The core `loreforge-wiki` skill should prefer a user-provided domain path, then
`WIKI_PATH`, then `~/wiki`.

For LoreForge instances that use `~/wiki` as the local working copy and sync
through Nutstore/WebDAV, keep the local checkout in that default directory and
follow the repo's documented sync command. The first sync on a fresh machine
may require a different bootstrap or resync command than the normal steady-state
sync.

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

## Discovery Flow

1. Use the user-provided wiki/domain path, if given.
2. Otherwise use `WIKI_PATH` and the requested domain name.
3. Otherwise read `~/.config/loreforge/registry.toml`, if available.
4. Otherwise fall back to `~/wiki`.
5. Enter `Domains/<domain>/`.
6. Orient on `SCHEMA.md`, `index.md`, recent `log.md`, and relevant pages.

Wiki-local metadata files are optional. The active core workflow is defined by
the selected domain's files, not by a copied template.

## Remote Sync Support

GitHub remotes are supported as persistence and sync backends. Nutstore/WebDAV
sync backends are also supported where the repo documents them.

Preferred mode:

```text
Remote backend -> local clone -> local read/search/write -> documented sync
```

Agents should not query GitHub directly for every answer.

Use normal git workflows for GitHub-backed wikis until a smaller sync helper is
justified. Use the repo's recorded sync command for Nutstore/WebDAV-backed
wikis; the first sync command may differ from the normal repeat-sync command.

## Registration

Create or update registry entries manually until a smaller domain-management
helper is justified.

First-time manual setup:

```bash
mkdir -p ~/.config/loreforge
cp templates/config/registry.toml ~/.config/loreforge/registry.toml
```

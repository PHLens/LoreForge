# Install

LoreForge has two parts:

1. Framework repo: this repository.
2. Wiki instance: a separate repository or vault created from `templates/wiki/`.

The wiki instance is the product. It is a plain Markdown git repo, so it can be opened in Obsidian, VS Code, or any other Markdown client without a separate compatibility layer.

## Create A Wiki Repo

Create a new repo from the generic template:

```bash
mkdir -p /path/to/my-wiki
cp -R templates/wiki/. /path/to/my-wiki/
cd /path/to/my-wiki
git init
```

Then edit:

- `AGENTS.md`
- `00_System/Vault Map.md`
- `00_System/+Wiki Index.md`
- `00_System/Views/`
- `Cards/`
- `Sources/`
- `MOCs/`

If the repo needs local path or workflow choices, record them in `.loreforge/wiki.toml` and `AGENTS.md` inside that wiki repo.

## Use With pamem

Store the wiki instance path in the agent workspace memory if useful.

Do not store wiki knowledge in pamem.

## Configure Local Discovery

See `docs/config.md` for the full configuration model.

Copy the registry template:

```bash
mkdir -p ~/.config/loreforge
cp templates/config/registry.toml ~/.config/loreforge/registry.toml
```

Edit the registry so each wiki has:

- `name`
- `path`
- `remote`
- `description`
- `default_view`

Agents should use this registry to find local wiki clones instead of guessing paths.

## Install Core Skills

Core operation skills live in:

```text
skills/
```

Current core skills:

- `loreforge-router`
- `query`
- `capture`
- `ingest`
- `writeback`
- `promote`
- `lint`
- `register`
- `sync`

Install them into the target agent environment using that environment's skill installation mechanism.

## Install As Plugin

LoreForge can also be installed as a plugin.

Codex plugin metadata:

```text
.codex-plugin/plugin.json
```

Claude plugin metadata:

```text
.claude-plugin/plugin.json
.claude-plugin/marketplace.json
.claude/CLAUDE.md
```

The plugin contains routing rules and skills only. Actual wiki knowledge stays in separate wiki instances registered through `~/.config/loreforge/registry.toml`.

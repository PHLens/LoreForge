# Install

LoreForge has two parts:

1. Framework repo: this repository.
2. Wiki instance: a separate repository or vault maintained by the `loreforge-wiki` skill.

## Create A Wiki Instance

Create a wiki root:

```bash
mkdir -p /path/to/my-wiki/00_System \
  /path/to/my-wiki/Calendar/dailynotes \
  /path/to/my-wiki/Shared/Raw \
  /path/to/my-wiki/Shared/Templates
```

Then ask an agent with the `loreforge-wiki` skill to initialize the target
domain. It should create:

- `00_System/index.md`, `00_System/domains.md`, and `00_System/wiki-layout.md`
- shared `Calendar/dailynotes/`, `Shared/Raw/`, and `Shared/Templates/`
- domain `SCHEMA.md`, `index.md`, `log.md`, `Atlas/`, `Cards/`, and `Spaces/`
  under `Domains/<domain>/`

Existing repos or vaults should be ingested as sources into the shared
`Shared/Raw/<source-id>/` area plus native domain synthesis under
`Domains/<domain>/`. Do not keep alternate layouts as long-term LoreForge
structure.

Create `Domains/<domain>/Extras/` only if the domain needs its own non-source
attachments.

## Use With pamem

Store the wiki instance path in the agent workspace memory if useful.

Do not store wiki knowledge in pamem.

## Configure Location

Set `WIKI_PATH` when you want agents to find the wiki without guessing:

```bash
export WIKI_PATH=/path/to/my-wiki
```

If unset, `loreforge-wiki` falls back to `~/wiki`.

## Install Core Skills

Core and helper skills live in:

```text
skills/
```

Router and core skill:

- `loreforge-router`
- `loreforge-wiki`

Bundled helper skills:

- `topic-research`
- `convert-to-markdown`
- `defuddle`
- `obsidian-markdown`
- `obsidian-cli`
- `json-canvas`
- `obsidian-bases`

Install them into the target agent environment using that environment's skill installation mechanism.

### Helper Runtime Setup

`topic-research` and `convert-to-markdown` use `uv` inside their `scripts/`
directories:

```bash
cd skills/topic-research/scripts
uv sync
./.venv/bin/python -m playwright install chromium

cd ../../convert-to-markdown/scripts
uv sync
```

`topic-research` may use local browser state files such as
`skills/topic-research/scripts/auth/zhihu.json`. These files can contain cookies
or tokens and are ignored by git. Copy or create them on each machine that needs
authenticated access.

`defuddle` requires the external CLI when used:

```bash
npm install -g defuddle
```

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
```

The plugin contains framework guidance and skills only. Actual wiki knowledge
stays in separate wiki instances.

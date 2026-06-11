# Install

LoreForge has two parts:

1. Framework repo: this repository.
2. Wiki instance: a separate repository or vault managed by the LoreForge
   main entrypoint, `loreforge-config`, `loreforge-card`, `loreforge-moc`, and
   `loreforge-domain`.

## Create A Wiki Instance

Create a wiki root:

```bash
mkdir -p /path/to/my-wiki/00_System \
  /path/to/my-wiki/Calendar/dailynotes \
  /path/to/my-wiki/Calendar/weeklynotes \
  /path/to/my-wiki/Shared/Raw \
  /path/to/my-wiki/Shared/Templates
```

Then ask LoreForge to initialize the target domain. The main entrypoint should
resolve config and the `loreforge-domain` expert should create:

- `00_System/index.md`, `00_System/domains.md`, and `00_System/wiki-layout.md`
- shared `Calendar/dailynotes/`, `Calendar/weeklynotes/`, `Shared/Raw/`, and
  `Shared/Templates/`
- shared templates: `Shared/Templates/weekly.md` for weekly planning,
  `card.md` for reusable concepts, `moc.md` for broader Atlas/MOC structure
  notes, and `relationship.md` for focused relationship views; diary templates
  may be added by the wiki's Obsidian profile
- domain `SCHEMA.md`, `index.md`, `log.md`, `Atlas/`, `Cards/`, and `Spaces/`
  under `Domains/<domain>/`
- optional `Sources/` under `Domains/<domain>/` when a source excerpt or
  source-specific lens is useful

Existing repos or vaults should be ingested as sources by first capturing raw
source packages under the shared `Shared/Raw/<source-id>/` area, then compiling
native domain synthesis under `Domains/<domain>/`. Capture should derive a
stable source ID, write `origin.md` plus `manifest.md`, and stop before domain
synthesis. Ingest should update that same package and compile durable notes from
it. Use `Domains/<domain>/Sources/` only when a source is too large or
source-specific excerpts are useful. Do not keep alternate layouts as long-term
LoreForge structure.

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

If unset, the main entrypoint and `loreforge-config` fall back to `~/wiki`.

## Install Core Skills

Core and helper skills live in:

```text
skills/
```

Main entrypoint and expert workflows:

- `loreforge`
- `loreforge-config`
- `loreforge-capture`
- `loreforge-paper`
- `plan-docomposer`
- `loreforge-work-item`
- `loreforge-card`
- `loreforge-moc`
- `loreforge-check`
- `loreforge-import`
- `loreforge-domain`

Bundled helper skills:

- `topic-research`
- `convert-to-markdown`
- `defuddle`
- `obsidian-markdown`
- `obsidian-cli`
- `json-canvas`
- `obsidian-bases`

Install them into the target agent environment using that environment's skill installation mechanism.
Keep `loreforge` as the user-facing entrypoint; the other LoreForge skills are
internal workflows that the entrypoint delegates to when the request needs
config, capture, paper-specific ingest, Calendar planning, work-item records,
checks, import, or domain writes.

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

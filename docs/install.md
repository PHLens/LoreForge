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
  /path/to/my-wiki/Atlas \
  /path/to/my-wiki/Calendar/dailynotes \
  /path/to/my-wiki/Calendar/weeklynotes \
  /path/to/my-wiki/Cards \
  /path/to/my-wiki/Sources/Raw \
  /path/to/my-wiki/Sources/Papers \
  /path/to/my-wiki/Sources/Clippings \
  /path/to/my-wiki/Spaces \
  /path/to/my-wiki/Extras/Templates \
  /path/to/my-wiki/Extras/Img \
  /path/to/my-wiki/Extras/Excalidraw \
  /path/to/my-wiki/z-Legacy
```

Then ask LoreForge to initialize the target domain. The main entrypoint should
resolve config and the `loreforge-domain` expert should create:

- `00_System/index.md`, `00_System/domains.md`, `00_System/wiki-layout.md`,
  `00_System/card-policy.md`, `00_System/card-domains.md`, and
  `00_System/agent-policy.md`
- root `Atlas/`, `Cards/<domain>/`, `Sources/Raw/`, `Sources/Papers/`,
  `Sources/Clippings/`, `Spaces/`, `Extras/`, and `z-Legacy/`
- shared templates: `Extras/Templates/weekly.md` for weekly planning and
  review; diary templates may be added by the wiki's Obsidian profile

Existing repos or vaults should be ingested as sources by first capturing raw
source packages under the shared `Sources/Raw/<source-id>/` area, then
compiling native root-layout synthesis. Capture should derive a
stable source ID, write `origin.md` plus `manifest.md`, and stop before domain
synthesis. Ingest should update that same package and compile durable notes from
it. Use root `Sources/` only when a source is too large or source-specific
excerpts are useful. Do not keep alternate layouts as long-term LoreForge
structure.

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

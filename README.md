# LoreForge

LoreForge is a framework for building LLM-wiki style professional knowledge bases.

It is inspired by [Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), but its scope is narrower and more practical:

- compile reusable professional knowledge from questions, sources, and queries
- make that knowledge readable by humans and agents
- reduce repeated raw search and re-summarization
- keep agent-local experience out of the shared wiki

## Core Boundary

```text
pamem
  agent-local memory
  preferences
  task state
  agent-local experience

LoreForge wiki instance
  professional knowledge
  concepts
  raw source packages
  maps and indexes

LoreForge framework repo
  plugin metadata
  schema
  skills
  config examples
```

LoreForge is not an agent memory store. It is a framework and plugin distribution used to create and operate separate wiki instances.

## Repository Form

This repository contains the framework:

```text
LoreForge/
├── .codex-plugin/plugin.json  # Codex plugin metadata
├── .claude-plugin/            # Claude plugin metadata
├── README.md
├── docs/                     # Philosophy, schema, install guidance
├── templates/config/          # Optional local registry example
└── skills/                   # LoreForge entrypoint, domain skill, and helper skills
```

Actual knowledge should live in a separate wiki repository or vault.

Agents should use an explicit wiki path when available, or `WIKI_PATH` plus a
domain name. If unset, the main entrypoint and `loreforge-config` fall back to
`~/wiki`.

## Wiki Instance Shape

The domain skill expects this shape:

```text
wiki/
  00_System/
    ...
  Calendar/
    dailynotes/
  Shared/
    Raw/
      <source-id>/
        manifest.md
        origin.md
        original/
        extracted/
        assets/
    Templates/
  Domains/
    <domain>/
      SCHEMA.md
      index.md
      log.md
      Atlas/
      Cards/
      Sources/  # optional compiled source excerpts
      Spaces/
```

Each domain is a self-contained LLM Wiki owned by one expert agent. The agent
orients on `SCHEMA.md`, `index.md`, recent `log.md`, and relevant pages before
querying, ingesting, updating, reviewing, or running a Check.

`Extras/` is optional for a domain and only used when the domain truly needs
its own non-source attachments.

`Shared/Raw/<source-id>/` stores the canonical raw source package:
`origin.md` keeps the agent-readable source text, and `manifest.md` keeps
metadata, source hash, compiled page pointers, and links to original/extracted
artifacts. `Shared/Templates/` stores reusable wiki
templates. `Domains/<domain>/Sources/` is optional and can hold source excerpts
or source-specific lenses when the raw package is large. `Cards/`, `Atlas/`,
and `Spaces/` hold the durable synthesis and cite raw manifests or domain
source notes through body footnotes, not YAML source links.

## Skills

LoreForge exposes one user entrypoint, focused internal workflows, one domain
expert skill, and helper skills used during source capture and Obsidian-facing
editing:

| Skill | Purpose |
|---|---|
| `loreforge` | Default main entrypoint for config, capture, ingest, lint, init, import, query, and cross-domain coordination |
| `loreforge-config` | Resolve wiki location, registry, sync backend, and post-write sync |
| `loreforge-capture` | Preserve raw source packages under `Shared/Raw/<source-id>/` without compiling domain pages |
| `loreforge-check` | Lint, audit, and structural checks for raw packages and native domains |
| `loreforge-import` | Treat existing repos, vaults, folders, and exports as source material |
| `loreforge-domain` | Query, ingest synthesis, update durable pages, and initialize expert-owned domains |
| `topic-research` | Browser-backed web research, URL extraction, Zhihu detail expansion, WeChat probing, and source research packs |
| `convert-to-markdown` | Convert local documents and exported pages to Markdown |
| `defuddle` | Extract clean Markdown from standard web pages with the Defuddle CLI |
| `obsidian-markdown` | Work with Obsidian-flavored Markdown syntax |
| `obsidian-cli` | Optional automation against a running Obsidian app |
| `json-canvas` | Create and edit JSON Canvas files |
| `obsidian-bases` | Create and edit Obsidian Bases files |

The main entrypoint owns domain selection, config, capture handoff, and cross-domain
coordination. `loreforge-domain` owns durable domain writes. Helper skills
produce capture input or Obsidian-specific artifacts; they should not replace
routing, domain orientation, index, log, and check workflow.

The previous Obsidian `wiki` adapter layout is not bundled. Existing Obsidian
vaults can still be used as sources, and LoreForge wiki instances can still be
opened in Obsidian as plain Markdown vaults.

## Plugin Distribution

LoreForge can be installed as a Codex or Claude plugin.

The plugin layer is intentionally thin:

- expose the `loreforge` main entrypoint
- expose `loreforge-config`, `loreforge-capture`, `loreforge-check`,
  `loreforge-import`, and `loreforge-domain`
- provide boundary instructions for when to use LoreForge
- keep actual knowledge in separate wiki instances
- recover after context compaction from domain `SCHEMA.md`, `index.md`,
  `log.md`, and relevant pages

Plugin metadata lives in:

```text
.codex-plugin/plugin.json
.claude-plugin/plugin.json
.claude-plugin/marketplace.json
```

## GitHub-Backed Wikis

LoreForge supports wiki instances backed by GitHub repositories.

The intended mode is local-first:

```text
GitHub remote -> local clone -> local query/search/edit -> git synchronization
```

Agents should use the local clone for search and editing. GitHub is for persistence and cross-machine synchronization, not per-query retrieval.

## Sync Backends

LoreForge wiki instances are local-first and can be configured for `webdav`,
`git`, or explicit `local` mode. New wiki initialization should confirm the
backend before the first durable write, and existing wikis can add sync behavior
by updating the machine-local registry entry for that machine.

After every agent-owned wiki edit, WebDAV-backed wikis should run
`skills/loreforge-domain/scripts/sync_webdav.sh`, git-backed wikis should commit
and push, and local-only wikis should report that no remote sync ran and warn
about data-loss risk. The WebDAV helper owns the exact `rclone bisync` command
and supports both steady-state sync and first-machine bootstrap/resync.

## Existing Repos And Vaults

Existing repos or vaults should be treated as sources. Use `loreforge-import`
and `loreforge-capture` to preserve raw material under `Shared/Raw/`, then
route selected material to `loreforge-domain` domain experts for native
`Domains/<domain>/` synthesis instead of keeping long-term alternate layouts or
source mirrors.

## License

MIT

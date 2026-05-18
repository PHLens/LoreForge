# Skills

Core LoreForge operations and bundled helper skills live here.

LoreForge exposes one user entrypoint plus focused internal workflows. Agents
should start from `loreforge`; the entrypoint delegates to paper, capture,
config, work-item, check, import, and domain workflows only when needed.

| Skill | Purpose |
|---|---|
| `loreforge` | Default user entrypoint for config, capture, ingest, lint, init, import, query, and cross-domain coordination |
| `loreforge-config` | Resolve wiki location, registry, sync backend, and post-write sync |
| `loreforge-capture` | Preserve raw clips under `Shared/Raw/` without compiling domain pages |
| `loreforge-paper` | Route paper-specific capture/ingest for arXiv, DOI, PDF, preprints, conference papers, and paper-like technical reports |
| `loreforge-work-item` | Turn project, Jira, issue, MR/PR, bugfix, CI failure, and implementation context into durable `Spaces/projects/` records |
| `loreforge-check` | Lint, audit, and structural checks for raw packages and native domains |
| `loreforge-import` | Treat existing repos, vaults, folders, and exports as source material |
| `loreforge-domain` | Query, ingest synthesis, update durable pages, and initialize expert-owned domains |

It also bundles reusable helper skills that a wiki agent can call during
capture or Obsidian-facing work:

| Skill | Purpose |
|---|---|
| `topic-research` | Browser-backed web research, URL extraction, Zhihu detail expansion, WeChat probing, and research packs |
| `convert-to-markdown` | Convert Word, Confluence MIME exports, HTML, and text files to Markdown, extracting images when supported |
| `defuddle` | Lightweight clean Markdown extraction for standard web pages via the Defuddle CLI |
| `obsidian-markdown` | Obsidian-flavored Markdown syntax: wikilinks, embeds, callouts, properties, and related references |
| `obsidian-cli` | Optional interaction with a running Obsidian app through the Obsidian CLI |
| `json-canvas` | Create and edit Obsidian JSON Canvas files |
| `obsidian-bases` | Create and edit Obsidian Bases files |

The `loreforge` skill owns intent classification, config/sync resolution,
source capture handoff, domain routing, write gates, and subagent fan-out.
`loreforge-paper` owns paper-specific page shape and related-work linking
before bounded domain handoff. `loreforge-work-item` owns durable project
record shape before bounded domain handoff. The domain skill follows the LLM
Wiki pattern: one expert agent maintains one domain by orienting on
`SCHEMA.md`, `index.md`, recent `log.md`, and relevant pages before writing.
Raw clips are preserved separately, and compiled domain pages cite raw
manifests or domain source notes with body footnotes, not YAML source links.

## Core Workflow

Use `loreforge` as the default user-facing entry point.
Use `loreforge-config` when location or sync needs to be resolved.
Use `loreforge-capture` when a source should be preserved without synthesis.
Use `loreforge-paper` when the source is a paper or paper-like technical report.
Use `loreforge-work-item` when current project, Jira, issue, MR/PR, bugfix, CI
failure, or implementation context should become a durable project record.
Use `loreforge-check` when the user asks for linting, audit, validation, or checks.
Use `loreforge-import` when an existing repo, vault, folder, or export should
be treated as source material.
Use `loreforge-domain` for one expert-owned domain's durable synthesis and
updates.

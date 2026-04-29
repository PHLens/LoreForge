# Skills

Core LoreForge operations and bundled helper skills live here.

LoreForge exposes one core wiki skill:

| Skill | Purpose |
|---|---|
| `loreforge-wiki` | Query, ingest sources, update durable pages, review, initialize domains, and run Health Checks for expert-owned LoreForge domains |

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

The core skill follows the LLM Wiki pattern: one expert agent maintains one
domain by orienting on `SCHEMA.md`, `index.md`, recent `log.md`, and relevant
pages before writing.

Legacy staged workflow skills such as `capture`, `ingest`, `writeback`,
`promote`, `query`, `lint`, `register`, and `sync` are intentionally removed
from the active skill surface. Their responsibilities are either covered by
`loreforge-wiki` or deferred until a smaller router, migration, domain-management,
or sync workflow is justified.

The old Obsidian `wiki` adapter skill is not bundled here. LoreForge's durable
layout is the native `Domains/<domain>/` structure operated by
`loreforge-wiki`; helper skills may feed capture material into that workflow but
do not reintroduce the previous staged adapter layout.

## Core Workflow

Use `loreforge-wiki` when a user or agent needs to:

- answer from an existing LoreForge domain
- ingest a source into `Sources/` and update related pages
- create or revise durable Cards, Atlas MOCs, or Spaces
- initialize a new expert-owned domain
- review or run a Health Check on a domain

The skill writes directly after orientation and keeps the domain `index.md` and
`log.md` current. Human review happens through logs, confidence fields,
contradiction metadata, Health Checks, and git diffs.

## Deferred Work

Router, migration, domain-management, and sync helpers should be added as small
skills only after the single-domain expert workflow is stable.

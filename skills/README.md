# Skills

Core LoreForge operations and bundled helper skills live here.

LoreForge exposes an optional router skill and one core domain wiki skill:

| Skill | Purpose |
|---|---|
| `loreforge-router` | Optional dispatch layer for unknown-domain, batch, or cross-domain query/ingest requests |
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
pages before writing. Capture writes flat raw clips under wiki-root
`Shared/Raw/`; ingest normalizes them into `Shared/Raw/<source-id>/` packages,
with `manifest.md` carrying metadata, source hash, and compiled page pointers.
Optional domain `Sources/` pages can hold excerpts or source-specific lenses
when a raw package is large. Compiled domain pages cite raw manifests or domain
source notes with body footnotes, not YAML source links.

Legacy staged workflow skills such as `capture`, `ingest`, `writeback`,
`promote`, `query`, `lint`, `register`, and `sync` are intentionally removed
from the active skill surface. Their responsibilities are either covered by
`loreforge-router`, `loreforge-wiki`, or deferred until a smaller migration,
domain-management, or sync workflow is justified.

The old Obsidian `wiki` adapter skill is not bundled here. LoreForge's durable
layout is the native `Domains/<domain>/` structure operated by
`loreforge-wiki`; helper skills may feed capture material into that workflow but
do not reintroduce the previous staged adapter layout.

## Core Workflow

Use `loreforge-router` when a user or agent needs to:

- decide which domain should handle a request
- query across domains
- plan ingest for captured source batches or a source that may belong to
  multiple domains
- coordinate bounded domain expert work through `loreforge-wiki`

Use `loreforge-wiki` when a user or agent needs to:

- answer from an existing LoreForge domain
- capture a raw source into `Shared/Raw/` as a flat clip, then let ingest
  normalize it into `Shared/Raw/<source-id>/manifest.md` and the relevant
  compiled pages
- create or revise durable Cards, Atlas MOCs, or Spaces
- create an optional domain `Sources/` page when a source-specific excerpt or
  stable lens is useful
- initialize a new expert-owned domain
- review or run a Health Check on a domain

For clear single-domain work, bypass the router and call `loreforge-wiki`
directly. The router should not capture raw content, normalize raw packages, or
write domain pages itself.

The skill writes directly after orientation and keeps the domain `index.md` and
`log.md` current. Human review happens through logs, confidence fields,
contradiction metadata, Health Checks, and git diffs.

## Deferred Work

Migration, domain-management, and sync helpers should be added as small skills
only after repeated use proves they are needed.

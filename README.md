# LoreForge

LoreForge is a framework for building LLM-wiki style professional knowledge bases.

It is inspired by [Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), but its scope is narrower and more practical:

- compile reusable professional knowledge from sources and queries
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
  source notes
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
└── skills/                   # LoreForge wiki skill
```

Actual knowledge should live in a separate wiki repository or vault.

Agents should use an explicit wiki path when available, or `WIKI_PATH` plus a
domain name. If unset, the core skill falls back to `~/wiki`.

## Wiki Instance Shape

The core wiki skill expects this shape:

```text
wiki/
00_System/
  ...
Domains/
  <domain>/
    SCHEMA.md
    index.md
    log.md
    Atlas/
    Cards/
    Sources/
    Spaces/
    Extras/
```

Each domain is a self-contained LLM Wiki owned by one expert agent. The agent
orients on `SCHEMA.md`, `index.md`, recent `log.md`, and relevant pages before
querying, ingesting, updating, reviewing, or running a Health Check.

## Core Skill

LoreForge currently exposes one core skill:

| Skill | Purpose |
|---|---|
| `loreforge-wiki` | Query, ingest sources, update durable pages, initialize domains, review, and run Health Checks for expert-owned domains |

Automation should grow from repeated usage pain, not be designed up front.

The old staged workflow skills (`capture`, `ingest`, `writeback`, `promote`,
`query`, `lint`, `register`, and `sync`) are no longer part of the active skill
surface. Routine expert maintenance happens directly inside the selected domain
after orientation, with human review through logs, confidence markers,
contradiction records, Health Checks, and git diffs.

## Plugin Distribution

LoreForge can be installed as a Codex or Claude plugin.

The plugin layer is intentionally thin:

- expose the `loreforge-wiki` skill
- provide boundary instructions for when to use LoreForge
- keep actual knowledge in separate wiki instances
- recover after context compaction from domain `SCHEMA.md`, `index.md`, `log.md`,
  and relevant pages

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

## Existing Repos And Vaults

Existing repos or vaults should be treated as sources. Use `loreforge-wiki` to
ingest useful material into a native `Domains/<domain>/` wiki instead of keeping
long-term alternate layouts.

## License

MIT

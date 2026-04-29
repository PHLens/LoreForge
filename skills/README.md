# Skills

Core LoreForge operations live here.

LoreForge now exposes one core wiki skill:

| Skill | Purpose |
|---|---|
| `loreforge-wiki` | Query, ingest sources, update durable pages, review, initialize domains, and run Health Checks for expert-owned LoreForge domains |

The core skill follows the LLM Wiki pattern: one expert agent maintains one
domain by orienting on `SCHEMA.md`, `index.md`, recent `log.md`, and relevant
pages before writing.

Legacy staged workflow skills such as `capture`, `ingest`, `writeback`,
`promote`, `query`, `lint`, `register`, and `sync` are intentionally removed
from the active skill surface. Their responsibilities are either covered by
`loreforge-wiki` or deferred until a smaller router, migration, domain-management,
or sync workflow is justified.

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

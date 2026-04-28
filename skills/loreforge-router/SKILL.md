---
name: loreforge-router
description: Route setup, ingest, search, writeback, lint, query, promote, register, or sync requests to the correct LoreForge skill for binding-centric workflows.
user-invocable: true
---

# LoreForge Router

Use this lightweight router before choosing a LoreForge operation.

## Route

| Intent | Skill |
|---|---|
| Create, install, adopt, or register a binding | `setup` |
| Ingest a URL, file, article, paper, docs page, repo note, or user-provided source | `ingest` |
| Search a configured target repo read root | `search` |
| Generic stable writeback or native review staging | `writeback` |
| Answer from native LoreForge knowledge using indexes, views, cards, sources, and MOCs | `query` |
| Promote native staged material into native cards, sources, MOCs, indexes, logs, and archive | `promote` |
| Check binding runtime state and package health | `lint protocol` |
| Check native repo structure and index/provenance health | `lint native` |
| Low-level binding registry update | `register` |
| Pull, inspect, commit, or push a target repo | `sync` |

## Boundaries

- Shared professional knowledge belongs in user-owned target repositories.
- Generic runtime packages, extracts, reports, caches, and locks belong in LoreForge runtime state.
- Native review packages belong in the target repo `10_Inbox/`.
- Agent-local experience, preferences, task state, and workflow memories belong in `pamem`.
- Locate bindings through `~/.config/loreforge/registry.toml`.
- Generic bindings support setup, ingest, stable writeback, search, and protocol lint.
- Native bindings support setup, ingest, writeback staging, search, query, promote, and native lint.
- Recover after compaction from the selected binding, runtime package manifests, and target repo context.

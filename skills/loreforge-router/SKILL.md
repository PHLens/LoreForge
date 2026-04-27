---
name: loreforge-router
description: Route LoreForge, llm-wiki, wiki knowledge base, shared professional knowledge, query, capture, ingest, writeback, promote, lint, register, or sync requests to the correct LoreForge skill.
user-invocable: true
---

# LoreForge Router

Use this lightweight router before choosing a LoreForge operation.

## Route

| Intent | Skill |
|---|---|
| Answer from existing wiki knowledge | `query` |
| Save a source, URL, or note quickly | `ingest mode=capture` or `capture` |
| Process an article, paper, docs, file, or captured note | `ingest mode=process` |
| Research and then stage source-derived knowledge | `ingest mode=research` |
| Save reusable conversation or query synthesis | `writeback` |
| Move staged package content into stable wiki notes | `promote` |
| Check wiki structure and package health | `lint` |
| Register or update a local wiki path | `register` |
| Pull, inspect, commit, or push a wiki clone | `sync` |

## Boundaries

- Shared professional knowledge belongs in a LoreForge wiki.
- Agent-local experience, preferences, task state, and workflow memories belong in `pamem`.
- Locate wikis through `~/.config/loreforge/registry.toml` and `.loreforge/wiki.toml`.
- `ingest` and `writeback` create staged packages.
- `promote` is the stable-write transaction.
- Recover after compaction from staged package `manifest.md`, `00_System/Wiki Log.md`, domain `+Wiki Index.md`, and the registry.

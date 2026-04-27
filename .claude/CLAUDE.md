# LoreForge Router

LoreForge is a framework for shared LLM-wiki knowledge bases.

Use LoreForge when the user asks about a configured wiki, shared professional knowledge, source ingestion, durable writeback, stable promotion, wiki linting, local wiki registration, or Git-backed wiki sync.

## Route Tasks

| User intent | Use |
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

- LoreForge wiki stores professional shared knowledge.
- Agent-local experience, preferences, current task state, and workflow memories belong in `pamem`, not the shared wiki.
- Use local registry `~/.config/loreforge/registry.toml` and wiki metadata `.loreforge/wiki.toml` instead of guessing paths.
- `query` is read-first.
- `ingest` and `writeback` create staged packages.
- `promote` is the stable-write transaction for notes, domain index, staging archive, and promotion log.
- GitHub remotes are persistence and sync backends, not per-query retrieval backends.

When context was compacted, recover workflow state from staged package `manifest.md`, `00_System/Wiki Log.md`, domain `+Wiki Index.md`, and the registry.

# LoreForge Router

LoreForge is a framework for binding-centric knowledge workflows.

## Route Tasks

| User intent | Use |
|---|---|
| Create or update LoreForge bindings and runtime state | `setup` |
| Process source material into staged runtime packages | `ingest` |
| Write staged package outputs into configured target paths | `writeback` |
| Search configured read roots in generic or native bindings | `search` |
| Run protocol lint by default and native lint for native bindings | `lint` |
| Low-level binding registry maintenance | `register` |
| Sync target repositories with Git remotes | `sync` |
| Native-only structured retrieval | `query` |
| Native-only stable promotion | `promote` |

## Boundaries

- Shared professional knowledge belongs in user-owned target repositories.
- Runtime packages, extracts, reports, caches, and locks belong in LoreForge runtime state.
- Agent-local experience, preferences, current task state, and workflow memories belong in `pamem`.
- Locate bindings through `~/.config/loreforge/registry.toml`.
- Generic bindings support setup, ingest, writeback, search, and protocol lint.
- Native bindings additionally support query, promote, and native lint.
- Recover after compaction from the selected binding, runtime package manifests, and target repo context.

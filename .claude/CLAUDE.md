# LoreForge Router

LoreForge is a framework for binding-centric knowledge workflows.

## Route Tasks

| User intent | Use |
|---|---|
| Create or update LoreForge bindings and runtime state | `setup` |
| Process source material into staged generic or native review packages | `ingest` |
| Generic stable writeback or native review staging | `writeback` |
| Search configured read roots in generic or native bindings | `search` |
| Run protocol lint by default and native lint for native bindings | `lint` |
| Low-level binding registry maintenance | `register` |
| Sync target repositories with Git remotes | `sync` |
| Native-only structured retrieval | `query` |
| Native-only stable promotion | `promote` |

## Boundaries

- Shared professional knowledge belongs in user-owned target repositories.
- Generic runtime packages, extracts, reports, caches, and locks belong in LoreForge runtime state.
- Native review packages belong in the target repo `10_Inbox/`.
- Agent-local experience, preferences, current task state, and workflow memories belong in `pamem`.
- Locate bindings through `~/.config/loreforge/registry.toml`.
- Generic bindings support setup, ingest, stable writeback, search, and protocol lint.
- Native bindings support setup, ingest, writeback staging, search, query, promote, and native lint.
- Recover after compaction from the selected binding, runtime package manifests, and target repo context.

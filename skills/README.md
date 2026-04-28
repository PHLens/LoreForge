# Skills

Core LoreForge operations live here.

These skills define framework-level workflows that any LoreForge wiki instance should support:

| Skill | Purpose |
|---|---|
| `loreforge-router` | Route LoreForge tasks to the correct operation skill |
| `query` | Locate a configured wiki and answer using views, maps, and indexes before broad search |
| `capture` | Thin alias for `ingest mode=capture` |
| `ingest` | Capture or process external sources into staged packages |
| `writeback` | Stage conversation/query synthesis as one or more candidate wiki notes |
| `promote` | Batch-promote staged packages into stable notes, update indexes, archive staging, and append the wiki log |
| `lint` | Run structural health checks |
| `register` | Register wiki instances in local machine config |
| `sync` | Synchronize a local wiki clone with its Git remote |

Core skills should resolve paths from the local registry and wiki-local `.loreforge/wiki.toml` whenever possible. Obsidian-specific conventions belong under `adapters/obsidian-vault/`.

`loreforge-router` is intentionally small. It exists so installed plugin sessions can recover the correct operation after context compaction.

## Ingest Modes

`capture` is a low-friction command alias for `ingest mode=capture`. It saves potentially durable material to `<capture>/` without deciding final structure.

`ingest mode=process` or `ingest mode=research` processes an inbox note, source note, file, or URL into a staged package after checking existing maps and indexes.

Processed packages use `manifest.md` and can contain multiple candidate notes.

## Stable Promotion

Only `promote` should make reviewed material part of stable wiki knowledge.

Pipeline:

```text
query -> answer
ingest mode=capture -> inbox capture
ingest/writeback -> staged package + package log
promote -> stable notes + card index + optional MOC updates + archive staging + promotion log
sync -> git persistence
```

This keeps index updates tied to the stable-write transaction while still letting the wiki log record meaningful staging events.

---
name: query
description: Use for native-only LoreForge structured retrieval from indexes, views, cards, sources, MOCs, and provenance conventions.
user-invocable: true
---

# Query Native LoreForge

Query is native-only by default. Generic bindings should use `search`.

Use `query` only when the selected binding has `mode = "native"` and a native retrieval contract. Native query answers from configured indexes, views, cards, sources, MOCs, and provenance conventions before considering broader search.

## Purpose

Use native repository structure first:

1. Resolve a native binding.
2. Load the configured native query view.
3. Read the native vault map or equivalent map file.
4. Read the configured card index.
5. Use Atlas and MOCs to select semantic context when present.
6. Search cards by title, aliases, and content.
7. Search sources when evidence, freshness, or provenance matters.
8. Answer with native repository grounding.

## Discovery

Default registry path:

```text
~/.config/loreforge/registry.toml
```

1. Read the binding registry.
2. Resolve the named binding, or the registry `default` if no binding is named.
3. Require `mode = "native"` or a `[bindings.native]` section.
4. Read `target_repo`.
5. Read native config from `[bindings.native]` and, when present, `<target_repo>/.loreforge/wiki.toml`.
6. If the target repo is missing but a remote is configured, ask before cloning or route to `sync`.

Generic bindings do not have structured query semantics. Use `search` over configured `read_roots` for generic repositories.

## Query Workflow

1. Enter `target_repo`.
2. Read the target repo `AGENTS.md` when present.
3. Read the native vault map, falling back to `00_System/Vault Map.md`.
4. Select the query view from native config, falling back to `00_System/Views/query.md`.
5. Read the configured index, falling back to `00_System/+Wiki Index.md`.
6. Read `MOCs/Scope/+Atlas.md` if present.
7. Use Atlas and MOCs to preselect likely semantic views when helpful.
8. Search `Cards/` by title, aliases, and content.
9. Read relevant `MOCs/` for synthesis and context.
10. Search `Sources/` only when evidence, freshness, or provenance matters.
11. Answer with native-grounded synthesis.
12. If durable knowledge is missing, recommend `ingest` or `writeback`; do not write by default.

## Native Search Order

Use configured native paths when present. Default order:

```text
00_System/Vault Map.md
00_System/Views/query.md
00_System/+Wiki Index.md
MOCs/Scope/+Atlas.md
MOCs/
Cards/
Sources/
```

## Hard Boundary

This skill is read-first.

It must not:

- operate as structured query on generic bindings
- write new notes by default
- save full transcripts
- store agent-local experience in the repository
- modify `pamem`
- commit or push git changes

It may:

- recommend `search` for generic bindings
- recommend `ingest` or `writeback` when durable gaps are found
- report that native indexes or source provenance appear stale

## Output

When answering, include:

- which native binding was used
- which native view was used
- important cards, MOCs, or source notes consulted
- any detected gap that should be ingested or written back later

Keep the answer concise unless the user asks for detailed synthesis.

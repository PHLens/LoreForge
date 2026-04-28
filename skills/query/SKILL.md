---
name: query
description: Use when answering from a configured LoreForge or llm-wiki knowledge base; query the card index, Atlas/MOCs, cards, and sources before broad web search.
user-invocable: true
---

# Query LoreForge Wiki

Answer questions from a LoreForge wiki instance without starting from raw web search.

## Purpose

Use compiled wiki knowledge first:

1. Locate the wiki instance.
2. Load the correct task view.
3. Read the vault map.
4. Read `00_System/+Wiki Index.md`.
5. Use Atlas and MOCs to preselect semantic views when helpful.
6. Search Cards by title, aliases, and content.
7. Search Sources only when provenance matters.
8. Use raw web search only when the wiki is missing or stale.

## Hard Boundary

This skill is read-first.

It must not:

- write new notes by default
- save full transcripts
- store agent-local experience in the wiki
- modify `pamem`
- commit or push git changes

It may:

- propose captures or staged notes when durable gaps are found
- recommend running `capture`, `ingest`, or `writeback`
- report that the wiki appears stale or missing

## Discovery

Default registry path:

```text
~/.config/loreforge/registry.toml
```

Registry template:

```text
templates/config/registry.toml
```

Wiki instance metadata:

```text
<wiki>/.loreforge/wiki.toml
```

If the user names a wiki, use that registry entry.

If no wiki is named, use the registry `default`.

If the local path does not exist but `remote` is configured, ask before cloning.

If the path exists, operate on the local clone.

## Query Workflow

1. Read `~/.config/loreforge/registry.toml`.
2. Resolve the target wiki by name or default.
3. Enter the wiki local path.
4. Read `.loreforge/wiki.toml` if present.
5. Read the wiki `AGENTS.md`.
6. Read `00_System/Vault Map.md`.
7. Select the query view from config, falling back to `00_System/Views/query.md`.
8. Read `00_System/+Wiki Index.md` or configured `index_file`.
9. Read `MOCs/Scope/+Atlas.md` if present.
10. Use Atlas and MOCs to preselect likely semantic views when helpful.
11. Search `Cards/` by title, aliases, and content.
12. Read relevant `MOCs/` for synthesis and context.
13. Search `Sources/` only when evidence, freshness, or provenance matters.
14. Answer with wiki-grounded synthesis.
15. If the wiki lacks durable knowledge, propose a capture or staged note; do not write by default.

## Search Order

Use this order inside a generic wiki instance:

```text
00_System/Vault Map.md
00_System/Views/query.md
00_System/+Wiki Index.md
MOCs/Scope/+Atlas.md, if present
MOCs/
Cards/
Sources/
```

For any wiki with custom paths, follow the wiki's `.loreforge/wiki.toml`.

## GitHub Remote Support

GitHub is a persistence and sync backend, not the query backend.

Preferred mode:

```text
remote GitHub repo -> local clone -> local query/search
```

Do not query GitHub for every answer.

If a wiki has a `remote` but no local clone, ask before cloning.

If a local clone exists, use local files. Report dirty git state when relevant, but do not commit or push from this skill.

## Output

When answering, include:

- which wiki was used
- which view was used
- important cards, MOCs, or source notes consulted
- any detected gap that should be captured or ingested later

Keep the answer concise unless the user asks for detailed synthesis.

---
name: query
description: Use when answering from a configured LoreForge or llm-wiki knowledge base; query wiki maps, domain indexes, cards, MOCs, and sources before broad web search.
user-invocable: true
---

# Query LoreForge Wiki

Answer questions from a LoreForge wiki instance without starting from raw web search.

## Purpose

Use compiled wiki knowledge first:

1. Locate the wiki instance.
2. Load the correct task view.
3. Read the vault map and domain map.
4. Use compact indexes.
5. Search cards and MOCs.
6. Search sources only when provenance matters.
7. Use raw web search only when the wiki is missing or stale.

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
7. Select the task view:
   - default query: `domain-query`
   - source investigation: `source-ingest`
   - structure/cleanup: `wiki-maintenance`
8. Identify target domain from the question or ask the user if ambiguous.
9. Read the target domain map.
10. Read relevant sections of the target domain `+Wiki Index.md`.
11. Search `Cards/` and `MOCs/`.
12. Search `Sources/` only when evidence or provenance matters.
13. Answer with wiki-grounded synthesis.
14. If the wiki lacks durable knowledge, propose a capture or staged note; do not write by default.

## Search Order

Use this order inside a wiki instance:

```text
00_System/Vault Map.md
00_System/Views/<view>.md
20_Domains/<Domain>/<Domain> Map.md
20_Domains/<Domain>/+Wiki Index.md
20_Domains/<Domain>/Cards/
20_Domains/<Domain>/MOCs/
20_Domains/<Domain>/Sources/
30_Shared/
```

For Obsidian adapter vaults that still use `MOCs/Scope/+Wiki Index.md`, follow the adapter conventions in `adapters/obsidian-vault/`.

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
- which view/domain was used
- important source notes or cards consulted
- any detected gap that should be captured or ingested later

Keep the answer concise unless the user asks for detailed synthesis.

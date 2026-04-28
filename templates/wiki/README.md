# LoreForge Wiki Template

This is the native LoreForge wiki starter template.

The template is type-first: directories describe what a note is, not which domain owns it. Domain and topic structure should emerge through MOCs, links, tags, and the card index.

## Layout

```text
AGENTS.md
.loreforge/
  wiki.toml
00_System/
  +Wiki Index.md
  Vault Map.md
  Schema.md
  Wiki Log.md
  Views/
10_Inbox/
  ingest/
  writeback/
Cards/
Sources/
MOCs/
Archive/
```

## Core Areas

| Area | Purpose |
|---|---|
| `00_System/` | Agent-facing protocol, schema, task views, card index, and wiki log |
| `10_Inbox/` | Staged ingest/writeback packages |
| `Cards/` | Flat stable atomic knowledge |
| `Sources/` | Source-grounded notes organized by source type |
| `MOCs/` | Emergent semantic views over cards and sources |
| `Archive/` | Closed staged packages and exceptional retired material |

## Retrieval Model

`00_System/+Wiki Index.md` is the minimum retrieval contract for stable Cards.

- Stable Cards should appear in the index.
- MOCs are semantic views and do not need to appear in the index.
- Sources are discovered through Card/MOC references, package provenance, and source metadata.
- Staged packages and archived packages should not appear in the index.

Query should generally read:

```text
00_System/Vault Map.md
00_System/Views/query.md
00_System/+Wiki Index.md
MOCs/Scope/+Atlas.md, if present
MOCs/
Cards/
Sources/, only when provenance matters
```

## Stable Writes

Stable wiki changes go through promotion:

```text
ingest/writeback package -> promote -> stable notes + card index + wiki log + archive
```

`ingest` and `writeback` work should create staged packages under `10_Inbox/ingest/` or `10_Inbox/writeback/`. A promoted package moves to `Archive/promoted/`; a rejected package moves to `Archive/rejected/`.

## Manifest Shape

Staged packages use `manifest.md` with package-relative candidate paths and target-repo-relative update paths:

```yaml
---
type: ingest
source_type: docs
status: staged
created: YYYY-MM-DD
provenance:
  - https://example.com/source-doc
candidate_notes:
  - Sources/Docs/example-source.md
  - Cards/example-concept.md
updates:
  - 00_System/+Wiki Index.md
promotion_reason: The source defines reusable knowledge.
---
```

Do not use a `domain` field. Do not use `path:` and `kind:` objects under `candidate_notes`; note kind is structural metadata inside the candidate file and can also be inferred from the path.

## Human Workspace Extensions

Concrete Obsidian vaults may add folders such as `Spaces/`, `Calendar/`, or `Extras/`. Those folders are outside the generic LoreForge stable promotion contract.

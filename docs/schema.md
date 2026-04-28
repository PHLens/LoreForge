# Schema

LoreForge wiki instances use a type-first structure.

## Layers

| Layer | Purpose |
|---|---|
| `cards` | Compiled atomic knowledge |
| `sources` | Source-grounded notes and provenance |
| `mocs` | Navigation and synthesis views |
| `system` | Schema, task views, card index, promotion log, policies |
| `inbox` | Captures and staged packages |
| `archive` | Closed packages and exceptional retired material |

## Default Template

Use `templates/wiki/` as the generic starting point for a new wiki instance.

Concrete wiki repos may customize this template in their own repository through `AGENTS.md` and `.loreforge/wiki.toml`.

## Default Layout

```text
00_System/
  +Wiki Index.md
  Vault Map.md
  Schema.md
  Wiki Log.md
  Views/
10_Inbox/
  capture/
  ingest/
  writeback/
Cards/
Sources/
MOCs/
Archive/
```

Directories describe note kind, not domain ownership. MOCs are emergent semantic views over cards and sources.

## Discovery Files

LoreForge uses two discovery layers:

| File | Scope | Purpose |
|---|---|---|
| `~/.config/loreforge/registry.toml` | machine-local | Lists wiki instances, local paths, remotes, and defaults |
| `<wiki>/.loreforge/wiki.toml` | wiki-local | Describes the wiki schema, entry files, task views, and path conventions |

Agents should never guess wiki paths when a registry is available.

## Wiki Index

`00_System/+Wiki Index.md` is the operational card index.

- stable Cards must appear in the index
- MOCs may be listed as convenience pointers, but are not required
- Sources are discovered through references and provenance, not the card index
- captures, staged packages, and archived packages are never indexed

## Stable Promotion

Stable wiki writes should go through the `promote` skill.

Promotion is the transaction that:

1. creates or moves reviewed staged notes into stable locations
2. updates `00_System/+Wiki Index.md` for promoted cards
3. optionally updates MOCs
4. moves consumed staging material to `Archive/promoted/` or `Archive/rejected/`
5. appends one entry to `00_System/Wiki Log.md`

Processed `ingest` and `writeback` outputs should use a staged package with `manifest.md`. A package can contain multiple candidate notes when they came from the same source or conversation.

## Manifest Contract

Minimum manifest:

```yaml
---
type: <ingest|writeback>
source_type: <source type>
status: staged
created: YYYY-MM-DD
provenance:
  - <source path/url/conversation>
candidate_notes:
  - Cards/<candidate-card>.md
updates:
  - 00_System/+Wiki Index.md
promotion_reason: <why this should become stable wiki knowledge>
---
```

`candidate_notes` and `updates` are simple package-relative path lists. Do not use a `domain` field or `path`/`kind` objects in the manifest.

## Note Metadata

Cards use:

```yaml
---
status: stable
created: YYYY-MM-DD
kind: card
aliases: []
tags: []
up: ""
---
```

Sources use:

```yaml
---
status: stable
created: YYYY-MM-DD
kind: source
source_type: paper
source_system: zotero
url: ""
accessed: YYYY-MM-DD
---
```

MOCs use:

```yaml
---
status: stable
created: YYYY-MM-DD
kind: moc
aliases: []
tags:
  - map
up: ""
---
```

`kind` is structural for agents and tooling. Tags remain freeform.

## Wiki Log

The wiki log is broader than promotion history: it may record substantive staged package creation and lint passes with meaningful findings, but should not record ordinary queries, ordinary captures, read-only lint with no meaningful findings, or sync operations.

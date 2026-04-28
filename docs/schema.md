# Native Profile Schema

This document describes LoreForge's optional native repository profile and native retrieval contract.

Generic bindings do not need this structure. A generic binding only needs a registry entry, runtime state, configured read roots, and configured writeback targets. Use `search` for generic retrieval and `writeback` for generic stable writes.

Native bindings add a high-structure profile for `query`, `promote`, and `lint native`. The native profile gives agents predictable indexes, views, note kinds, provenance conventions, and promotion logs.

Native staging is repo-local by design. Native ingest and writeback create review packages under `10_Inbox/` so humans and other agents can inspect them before `promote` writes stable knowledge. `state_dir` remains available for extracts, snapshots, reports, cache, locks, and temporary runtime evidence.

## Native Layers

| Layer | Purpose |
|---|---|
| `cards` | Compiled atomic knowledge |
| `sources` | Source-grounded notes and provenance |
| `mocs` | Navigation and synthesis views |
| `system` | Schema, task views, card index, promotion log, and policies |
| `inbox` | Native staging area for reviewed package material |
| `archive` | Closed packages and exceptional retired material |

These layers are native-profile conventions, not requirements for all bindings.

## Native Starter Template

Use `templates/wiki/` only when creating a native starter repository.

The template name is historical. It remains the current native starter until a separate migration renames it.

Existing repositories can be bound in generic mode without copying this template. Repositories should adopt the native profile only when they need structured native query, promotion, and lint behavior.

## Native Layout

The native starter uses:

```text
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

Directories describe note kind, not domain ownership. MOCs are emergent semantic views over cards and sources. Generic bindings may use any repository layout configured through registry targets and read roots.

## Discovery Files

LoreForge uses a machine-local registry for all bindings and optional native metadata for native targets:

| File | Scope | Purpose |
|---|---|---|
| `~/.config/loreforge/registry.toml` | machine-local | Lists bindings, target repos, runtime state dirs, read roots, targets, modes, remotes, and defaults |
| `<target_repo>/.loreforge/wiki.toml` | native target only | Describes native entry files, task views, indexes, logs, and path conventions |

Agents should never guess target paths when a registry is available.

## Native Retrieval Contract

Native `query` relies on:

- registry binding resolution with `mode = "native"`
- native metadata when present
- `00_System/Views/query.md` or an equivalent configured query view
- `00_System/Vault Map.md` or an equivalent map file
- `00_System/+Wiki Index.md` for stable cards
- `Cards/`, `Sources/`, and `MOCs/`
- source provenance and stable note metadata

This contract is why generic bindings use `search` instead of `query`.

## Native Index

`00_System/+Wiki Index.md` is the native operational card index.

- stable native cards should appear in the index
- MOCs may be listed as convenience pointers, but are not required
- sources are discovered through references and provenance, not the card index
- staged and archived package material is not indexed as stable knowledge

This index convention applies to native repos only.

## Native Promotion

Stable native writes should go through the `promote` skill.

Promotion is the native transaction that:

1. creates or moves reviewed staged notes into stable native locations
2. updates `00_System/+Wiki Index.md` for promoted cards
3. optionally updates MOCs
4. moves consumed staging material to `Archive/promoted/` or `Archive/rejected/`
5. appends one entry to `00_System/Wiki Log.md`

Generic bindings use `writeback` as their stable write operation. Generic writeback validates configured targets and paths but does not require native indexes, logs, MOCs, or promotion semantics. Native bindings use `writeback` only to create staged packages under `10_Inbox/writeback/`; stable native writes go through `promote`.

## Native Manifest Convention

Generic runtime packages use `manifest.toml` in `state_dir` and are checked by protocol lint. Native review packages use `manifest.md` under `10_Inbox/ingest/` or `10_Inbox/writeback/` and are checked by native lint.

Minimum native manifest:

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
promotion_reason: <why this should become stable native knowledge>
---
```

`candidate_notes` are simple package-relative path lists. `updates` are target-repo-relative paths that will be changed during promotion, such as `00_System/+Wiki Index.md`. Do not use a `domain` field or `path`/`kind` objects in the native manifest.

## Native Note Metadata

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

`kind` is structural for agents and native tooling. Tags remain freeform.

## Native Log

`00_System/Wiki Log.md` is broader than promotion history, but staged package creation is already represented by the package manifest. The log may record promotions and lint passes with meaningful findings, but should not record ordinary queries, ordinary staged package creation, read-only lint with no meaningful findings, or sync operations.

This log convention applies to native repos only.

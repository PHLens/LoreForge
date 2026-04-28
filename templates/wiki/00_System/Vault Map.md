# Vault Map

Global entry point for this LoreForge wiki instance.

This file lists stable knowledge areas, activity areas, system files, and retrieval strategy. It does not enumerate every note.

## Stable Knowledge Areas

| Area | Path | Description |
|---|---|---|
| Cards | `Cards/` | Flat stable atomic knowledge |
| Sources | `Sources/` | Source-grounded notes by source type |
| MOCs | `MOCs/` | Emergent semantic views |
| Scope Views | `MOCs/Scope/` | Vault-level entry views |

## Activity Areas

| Area | Path | Description |
|---|---|---|
| Inbox | `10_Inbox/` | Staged ingest and writeback packages |
| Staged Ingest | `10_Inbox/ingest/` | Packages from external source processing |
| Staged Writeback | `10_Inbox/writeback/` | Packages from conversation or query synthesis |
| Archive | `Archive/` | Closed packages and exceptional retired material |

## System Files

| File | Path | Description |
|---|---|---|
| Schema | `00_System/Schema.md` | Wiki structure and note conventions |
| Wiki Index | `00_System/+Wiki Index.md` | Compact stable card inventory |
| Wiki Log | `00_System/Wiki Log.md` | Human-readable timeline of meaningful wiki evolution |

## Task Views

- Default -> `00_System/Views/default.md`
- Query -> `00_System/Views/query.md`
- Ingest -> `00_System/Views/ingest.md`
- Writeback -> `00_System/Views/writeback.md`
- Promote -> `00_System/Views/promote.md`
- Maintenance -> `00_System/Views/maintenance.md`

## Retrieval Strategy

1. Read the task view.
2. Read `00_System/+Wiki Index.md` for stable card candidates.
3. Read `MOCs/Scope/+Atlas.md` if present to preselect semantic views.
4. Search relevant MOCs and Cards.
5. Search Sources only when evidence or provenance matters.

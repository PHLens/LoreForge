# Wiki Instance Agent Rules

This file is copied into a concrete LoreForge wiki instance.

## Purpose

This wiki stores professional, reusable knowledge for humans and agents.

It is not agent-local memory. Agent-local experience, preferences, and current task state belong in `pamem`.

## Startup Flow

1. Read this file.
2. Read `00_System/Vault Map.md`.
3. Choose the relevant task view from `00_System/Views/`.
4. Read `00_System/+Wiki Index.md` before broad full-text search.
5. Use `MOCs/Scope/+Atlas.md` and relevant MOCs as optional semantic views.

## Write Policy

Allowed without confirmation:

- New captures under `10_Inbox/capture/`
- New staged packages under `10_Inbox/ingest/` or `10_Inbox/writeback/`
- Wiki log entries for substantive staged package creation
- Read-only reports

Requires confirmation:

- Promotion from staging to stable knowledge areas
- Index updates
- Semantic edits to existing stable notes
- Deletions, moves, or large restructures
- Changes to `00_System/` rules or views

Stable promotion should update stable notes, update `00_System/+Wiki Index.md` for promoted cards, move consumed staging material to `Archive/`, and append `00_System/Wiki Log.md` in the same transaction.

## Storage Boundary

| Content | Destination |
|---|---|
| Professional concept or method | `Cards/` |
| Source summary | `Sources/<Type>/` |
| Topic map or semantic view | `MOCs/` |
| Vault-level view | `MOCs/Scope/` |
| Uncertain capture | `10_Inbox/capture/` |
| Staged package | `10_Inbox/ingest/` or `10_Inbox/writeback/` |
| Closed package | `Archive/promoted/` or `Archive/rejected/` |
| Agent local experience | `pamem`, not this wiki |

## Do Not Store

- Full chat transcripts
- One-off debug output
- Current task state
- Agent-local preferences
- Raw memory logs

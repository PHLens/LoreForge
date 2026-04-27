# Wiki Instance Agent Rules

This file is copied into a concrete LoreForge wiki instance.

## Purpose

This wiki stores professional, reusable knowledge for humans and agents.

It is not agent-local memory. Agent-local experience, preferences, and current task state belong in `pamem`.

## Startup Flow

1. Read this file.
2. Read `00_System/Vault Map.md`.
3. Choose the relevant task view from `00_System/Views/`.
4. Read the relevant domain map before searching raw notes.
5. Search the compact indexes before broad full-text search.

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

Stable promotion should update notes and the target domain `+Wiki Index.md`, archive consumed staging material, and append `00_System/Wiki Log.md` in the same transaction.

## Storage Boundary

| Content | Destination |
|---|---|
| Professional concept | `20_Domains/<Domain>/Cards/` |
| Source summary | `20_Domains/<Domain>/Sources/` |
| Topic map | `20_Domains/<Domain>/MOCs/` |
| Cross-domain method | `30_Shared/Methods/` |
| Uncertain capture | `10_Inbox/capture/` |
| Staged package | `10_Inbox/ingest/` or `10_Inbox/writeback/` |
| Agent local experience | `pamem`, not this wiki |

## Do Not Store

- Full chat transcripts
- One-off debug output
- Current task state
- Agent-local preferences
- Raw memory logs

# Ingest View

Use this view when processing a new article, paper, document, repository, local file, or source note.

## Load First

- `AGENTS.md`
- `00_System/Vault Map.md`
- `00_System/+Wiki Index.md`
- Relevant MOCs if they already exist
- Source material

## Workflow

1. Preserve source provenance.
2. Identify reusable concepts.
3. Check existing Cards before creating new ones.
4. Create a staged package with `manifest.md`.
5. Use type-first candidate paths such as `Sources/Docs/<source>.md` and `Cards/<concept>.md`.
6. Include `00_System/+Wiki Index.md` in `updates` when the package contains card candidates.
7. Use `promote` for stable notes, index updates, archive moves, and promotion log entries.

## Boundary

New source-derived knowledge starts staged. Do not promote without confirmation.

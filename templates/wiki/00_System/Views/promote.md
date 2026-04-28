# Promote View

Use this view when approved staged packages should become stable wiki knowledge.

## Load First

- `AGENTS.md`
- `00_System/Vault Map.md`
- `00_System/Schema.md`
- The staged package `manifest.md`
- `00_System/+Wiki Index.md`
- Relevant target Cards, Sources, or MOCs

## Workflow

1. Read the package manifest.
2. Validate `status: staged`.
3. Resolve package-relative `candidate_notes`.
4. Check stable target path conflicts.
5. Move or create approved candidates in stable paths.
6. Update `00_System/+Wiki Index.md` for promoted Cards.
7. Apply optional MOC deltas.
8. Append one `00_System/Wiki Log.md` entry.
9. Move the package to `Archive/promoted/` or `Archive/rejected/`.

## Boundary

Do not promote without an explicit user-approved plan.

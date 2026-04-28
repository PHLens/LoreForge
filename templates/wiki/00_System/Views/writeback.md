# Writeback View

Use this view when conversation or query synthesis may become durable shared wiki knowledge.

## Load First

- `AGENTS.md`
- `00_System/Vault Map.md`
- `00_System/+Wiki Index.md`
- Relevant Cards and MOCs

## Workflow

1. Deliver the answer first.
2. Decide whether the synthesis is reusable professional knowledge.
3. Skip one-off debugging, current task state, agent-local experience, and preferences.
4. Create a staged package under `10_Inbox/writeback/`.
5. Put candidate cards under package `Cards/`.
6. Put optional MOC deltas under package `Deltas/` or candidate MOCs under package `MOCs/`.
7. Include `00_System/+Wiki Index.md` in `updates` when the package contains card candidates.
8. Hand stable writes to `promote`.

## Boundary

Writeback stages reviewed candidate knowledge. It does not directly edit stable Cards, MOCs, Sources, or indexes.

# Query View

Use this view for answering questions from existing wiki knowledge.

## Load First

- `AGENTS.md`
- `00_System/Vault Map.md`
- `00_System/+Wiki Index.md`
- `MOCs/Scope/+Atlas.md`, if present

## Search Order

1. `00_System/+Wiki Index.md` for stable card candidates.
2. `MOCs/Scope/+Atlas.md`, if present, to preselect likely views.
3. Relevant `MOCs/` for semantic context.
4. `Cards/` by title, aliases, and content.
5. `Sources/` only when provenance, freshness, or source-grounded detail matters.

## Writeback Rule

Query normally does not write. If a query exposes durable missing knowledge, stage a writeback package under `10_Inbox/writeback/`.

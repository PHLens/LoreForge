# Domain Query View

Use this view for answering questions from existing wiki knowledge.

## Load First

- `AGENTS.md`
- `00_System/Vault Map.md`
- Target domain map
- Relevant section of target domain `+Wiki Index.md`

## Search Order

1. Domain map for scope and MOCs
2. `+Wiki Index.md` for candidate notes
3. `Cards/` by title and aliases
4. `MOCs/` for synthesis
5. `Sources/` for provenance

## Writeback Rule

Query normally does not write.

If a query exposes a durable missing concept or broken connection, stage a writeback package under `10_Inbox/writeback/`.

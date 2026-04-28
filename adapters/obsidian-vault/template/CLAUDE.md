# Keep in sync with AGENTS.md

# Vault Constraints

All agents operating on this vault MUST follow these rules.

## Note Format

- `up` field: frontmatter `up: "[[Parent]]"` (single colon, double quotes around wikilink); inline `up:: [[Parent]]` (double colon, no quotes)
- `X::` links: ONLY for distinction/comparison or easily confused concepts, NOT for all related notes
- `agent` tag: add to all notes created by agents
- `#map` tag for MOC notes, not `#moc`
- Reference section: external sources only (articles, URLs), not internal cards
- Figures: save to `Extras/Media/Img/`, reference with `![[filename.png]]`

## Source Immutability

- Source notes (`Sources/`) are write-once. After creation, only additive updates allowed (new references, new concept links)
- Never rewrite, restructure, or delete content from source notes
- Corrections go to concept cards, not back to source

## Two-Tier Autonomy

- **Auto** (no confirmation): read-only query, lint reports, quick captures, and staged packages under the configured inbox.
- **Confirm**: promotion to stable notes, index updates, semantic edits, structural changes, note moves, deletions, and schema/view changes.
- **Principle**: staging is low-risk; stable wiki changes require an explicit approved promotion plan.

## Staging

- New ingest/writeback candidates stage as packages under `10_Inbox/ingest/` or `10_Inbox/writeback/`.
- Legacy vaults may still contain `Sources/agents/`; treat it as an older staging area and migrate touched material into staged packages before promotion.
- Wait for user confirmation before moving to final locations (`Cards/`, `MOCs/`, `Spaces/`)
- Do not touch final locations until user confirms

## +Wiki Index & Log

- `MOCs/Scope/+Wiki Index.md` — agent-facing manifest of stable knowledge only. Update during approved promotion, not during ordinary staging.
- `MOCs/Scope/+Wiki Log.md` — append-only operation log for substantive staged packages and approved promotions.
  - Format: `## [YYYY-MM-DD] ingest|query|lint | <title>`
  - Body: `- source:`, `- created:`, `- updated:`, `- touched: N cards`
  - Do NOT edit historical entries

## MOC Emergence

- Create MOC only when 5+ related cards share a theme and no MOC covers it
- Update MOC only when new cards genuinely belong to its scope
- Do NOT create MOCs proactively or update on every ingest

## Ingest Ripple

- After creating new cards, scan and update all related existing cards
- Additive only: add backlinks, see also, short fact deltas, source references
- Do not rewrite existing content, delete content, or restructure sections
- MOC update is NOT part of ripple — only update MOC if ripple reveals genuine new connection within MOC scope

## Discoverability

- A note is discoverable if reachable via ANY of: inbound `[[link]]`, `+Wiki Index` entry, or `up` field
- Lint reports "undiscoverable" notes (triply unreachable), not "orphans"

---

## Claude-Specific

- Writeback: a stop hook may propose a staged writeback package when durable shared knowledge is detected; it must not update stable notes, indexes, or logs directly.
- Skills path: install from repository root `skills/`; Obsidian vault template lives in `adapters/obsidian-vault/template/`

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

- **Auto** (no confirmation): metadata/backlink/index updates, lint reports, new staged notes in `Sources/agents/`, +Wiki Log entries, additive-only ripple updates (add `X::` links, See also, source refs, short fact paragraphs <3 lines)
- **Confirm**: semantic edits (rewriting/rephrasing existing content), structural changes, note moves, deletions, promotion from `Sources/agents/` to final locations
- **Principle**: additive-only changes that don't alter existing text → auto; changes that modify or remove existing text → confirm

## Staging

- All new notes stage in `Sources/agents/` first
- Wait for user confirmation before moving to final locations (`Cards/`, `MOCs/`, `Spaces/`)
- Do not touch final locations until user confirms

## +Wiki Index & Log

- `MOCs/Scope/+Wiki Index.md` — agent-facing manifest. Update after every ingest/writeback. One line per entry: `[[Note]] — <summary> [category]`
- `MOCs/Scope/+Wiki Log.md` — append-only operation log. Append after every ingest, query writeback, or lint.
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

- Writeback: Stop hook triggers writeback evaluation when `MOCs/Scope/+Wiki Index.md` exists
- Skills path: install from repository root `skills/`; Obsidian vault template lives in `adapters/obsidian-vault/template/`

---
aliases:
tags:
  - system/guide
  - agent
kind: moc
up: "[[+Atlas]]"
---
# +Agent Workflow

Workflow guide for agents operating on this vault. Read alongside CLAUDE.md / AGENTS.md for constraints.

## Core Pipeline

```
Source → Concept Card → Connections → Cluster → MOC (emergent)
```

Knowledge grows bottom-up. MOCs emerge when conceptual clusters form naturally.

## 1. Source Note Creation

Location: `Sources/<Type>/`

```markdown
---
aliases:
tags:
  - source/article
source_type: article
source_system: cubox
url: <original_url>
author: <author>
---
# Title

## Why
<Motivation/context>

## What
<Key concepts with links to concept cards>
- [[Concept Card 1]]

## How
<Implementation details, insights>

## References
1. Reference list
```

## 2. Concept Card Creation

Location: `Cards/`

Each card is atomic — ONE concept per card.

```markdown
---
aliases:
  - Alternative names
category:
modification date: YYYY-MM-DD
tags:
  - concept
  - concept/<domain>
  - agent
up: "[[Parent Concept]]"
---
X:: [[Related Concept]]
# Why <Concept>
<Motivation>

# What is <Concept>
<Definition and details>

Reference:
- [[Source Note]]
```

## 3. Ingest Ripple Update

After creating new cards, scan and update all related existing cards:
- Scope: 1 source hub + all related cards (no artificial limit)
- Additive only: add backlinks, See also, source references, short fact paragraphs (<3 lines)
- Do NOT: rewrite existing content, delete content, restructure sections
- Autonomy: additive-only → auto; semantic changes → confirm
- Detection: use `up` field, `X::` links, wikilink references, and `+Wiki Index` to find related cards

## 4. MOC Emergence (conditional)

Location: `MOCs/`

- Create: when 5+ related cards share a theme and no MOC covers it
- Update: when new cards genuinely add navigation value within its scope
- Skip: if loosely related or cluster isn't ready

```markdown
## Category Name
- [[Card 1]] - Brief description
- [[Card 2]] - Brief description
```

## 5. +Wiki Index Update

Location: `MOCs/Scope/+Wiki Index.md`

Update the index only during approved promotion:
- Add stable card entries: `<card wikilink> — <one-line summary> [category]`
- Update existing stable entries if the approved promotion changes retrieval text
- Remove entries only when an approved promotion or maintenance plan moves/deletes stable notes

## 6. +Wiki Log Append

Location: `MOCs/Scope/+Wiki Log.md`

Append logs for substantive staged packages and approved promotions:
```markdown
## YYYY-MM-DD | stage|promote|lint | <package-or-scope>
- source: <what was processed>
- created: <new notes>
- updated: <modified notes>
- touched: N cards
```

## Query Writeback

When a synthesized answer has lasting value:
1. Deliver answer first — do not delay for writeback evaluation
2. Evaluate: comparison/analysis → high; concept explanation → medium; simple lookup → skip
3. Stage a writeback package under `10_Inbox/writeback/`
4. Include package-relative candidate notes, proposed deltas, provenance, and promotion rationale in `manifest.md`
5. Use `promote` for stable notes, index updates, archive moves, and promotion log entries after approval

## Comparison Card Format

```markdown
---
aliases:
tags:
  - concept
  - concept/comparison
  - agent
up: "[[Parent Topic]]"
---
X:: [[Concept A]]
X:: [[Concept B]]
# A vs B
## Summary
<One-line verdict>

| Dimension | A | B |
|---|---|---|
| ... | ... | ... |

## When to use A
## When to use B
## Trade-offs

Reference:
- [[Source Note]]
```

## Concept Tag Patterns

| Tag | Domain |
|-----|--------|
| `concept` | General concept |
| `concept/gpu` | GPU architecture |
| `concept/ca` | Computer architecture |
| `concept/dl` | Deep learning |
| `concept/network` | Networking |
| `concept/distributed` | Distributed systems |

## Quality Checklist

- [ ] Source note has Why/What/How structure
- [ ] Each card is atomic (one concept)
- [ ] Connections discovered and recorded (wikilinks, `X::`, `up`)
- [ ] Cards reference source notes
- [ ] Tags follow convention (concept, concept/domain)
- [ ] MOC created/updated ONLY if genuine cluster formed

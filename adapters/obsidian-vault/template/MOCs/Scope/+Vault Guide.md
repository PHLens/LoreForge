---
aliases:
tags:
  - system/guide
  - agent
up: "[[+Atlas]]"
---
# +Vault Guide

Structural guide for agents operating on this vault. For workflow steps, see [[+Agent Workflow]]. For constraints, read CLAUDE.md or AGENTS.md in the vault root.

## Directory Layout

| Directory | Purpose | Agent Access |
|-----------|---------|-------------|
| `Cards/` | Atomic concept notes | Stage first, confirm to promote |
| `MOCs/` | Maps of Content | Stage first, confirm to promote |
| `MOCs/Scope/` | Agent-facing indexes | Auto-update |
| `Sources/Article/` | Article source notes | Write-once, additive only |
| `Sources/Papers/` | Paper notes | Write-once, additive only |
| `Sources/Cubox/` | Cubox sync content | Write-once, additive only |
| `Sources/agents/` | Staging area for agent drafts | Auto-create |
| `Spaces/` | GTD, research, work | Stage first, confirm to promote |
| `Inbox/` | Quick capture | Auto-create |
| `Extras/Media/Img/` | Images and figures | Auto-save |
| `Extras/Templates/` | Note templates | Read-only |

## Key Index Files

| File | Purpose | Update Rule |
|------|---------|------------|
| `MOCs/Scope/+Wiki Index.md` | Agent-facing compact manifest | Auto-update after ingest/writeback |
| `MOCs/Scope/+Wiki Log.md` | Append-only operation log | Auto-append after ingest/query/lint |
| `MOCs/Scope/+Atlas.md` | User dashboard | Do NOT modify |
| `Cards/+ Index of Cards.md` | Dataview BOAT/Evergreen index | Do NOT modify |

## Note Types & Tags

| Type | Tags | Location |
|------|------|----------|
| Concept card | `concept`, `concept/<domain>`, `agent` | `Cards/` |
| Comparison card | `concept`, `concept/comparison`, `agent` | `Cards/` |
| MOC | `map` | `MOCs/` |
| Source article | `source/article` | `Sources/Article/` |
| Source paper | `source/paper` | `Sources/Papers/` |
| Inbox capture | `inbox` | `Inbox/` |

## Frontmatter Format

```yaml
---
aliases:
tags:
  - concept
  - concept/<domain>
  - agent
category:
modification date: YYYY-MM-DD
up: "[[Parent Note]]"
---
```

### Inline Metadata

- `up:: [[Parent Note]]` — double colon, no quotes (Dataview inline field)
- `X:: [[Related Note]]` — only for distinction/comparison concepts

## Naming Conventions

- English titles for technical content
- Date suffix for inbox: `Title-YYYY-MM-DD.md`
- Source articles: `Title-YYYY-MM-DD.md` in `Sources/Article/`

## Lint (Health Check)

Run `bash <skill-path>/lint/scripts/lint-wiki.sh [vault_path]`.

Check items:
1. Undiscoverable notes (triply unreachable: no inbound link, no +Wiki Index entry, no `up` field)
2. Missing `up` field (informational)
3. Unresolved `[[link]]` targets
4. Duplicate/near-duplicate titles
5. Stale staged drafts in `Sources/agents/`
6. MOC stale references (entries pointing to missing cards)
7. Metadata drift (inconsistent tags, empty sub-tags, missing frontmatter)

Output: structured report in chat. No file writes. Append entry to +Wiki Log after lint.

## Technical Findings

Agent-discovered corrections with future decision value:

- **MCP config**: goes in `~/.claude.json`, NOT `~/.claude/settings.json`. WebSearch fails with DashScope; WebFetch works; DuckDuckGo + Firecrawl MCPs available.
- **SVG render-check**: always render with `inkscape file.svg -o /tmp/file.png` and inspect PNG. Text near bottom of boxed panels often clips.
- **Chinese sites**: WeChat articles require browser path (Playwright), not `requests`. Mobile UA does NOT bypass captcha.

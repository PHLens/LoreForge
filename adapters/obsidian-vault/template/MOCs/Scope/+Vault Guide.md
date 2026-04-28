---
aliases:
tags:
  - system/guide
  - agent
kind: moc
up: "[[+Atlas]]"
---
# +Vault Guide

Structural guide for agents operating on this vault. For workflow steps, see [[+Agent Workflow]]. For constraints, read CLAUDE.md or AGENTS.md in the vault root.

## Directory Layout

| Directory | Purpose | Agent Access |
|-----------|---------|-------------|
| `Cards/` | Flat atomic concept notes | Stage first, confirm to promote |
| `MOCs/` | Emergent Maps of Content | Stage first, confirm to promote |
| `MOCs/Scope/` | Vault-level views plus adapter index/log | Update index/log during approved promotion |
| `Sources/Article/` | Legacy article source notes | Write-once, additive only |
| `Sources/Papers/` | Paper notes | Write-once, additive only |
| `Sources/Cubox/` | Legacy Cubox sync content | Migration source only |
| `10_Inbox/ingest/` | Staged source packages | Auto-create packages |
| `10_Inbox/writeback/` | Staged conversation/query packages | Auto-create packages |
| `Spaces/` | GTD, research, work | Human workspace, not a promote target |
| `10_Inbox/capture/` | Quick capture | Auto-create |
| `Extras/Media/Img/` | Images and figures | Auto-save |
| `Extras/Templates/` | Note templates | Read-only |

## Key Index Files

| File | Purpose | Update Rule |
|------|---------|------------|
| `MOCs/Scope/+Wiki Index.md` | Adapter-configured operational card index | Update for promoted cards during approved promotion |
| `MOCs/Scope/+Wiki Log.md` | Append-only operation log | Append for substantive staging and approved promotion |
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
up: "<parent wikilink>"
---
```

### Inline Metadata

- `up:: <parent wikilink>` — double colon, no quotes (Dataview inline field)
- `X:: <related wikilink>` — only for distinction/comparison concepts

## Naming Conventions

- English titles for technical content
- Date suffix for inbox: `Title-YYYY-MM-DD.md`
- Source articles: `Title-YYYY-MM-DD.md` in `Sources/Article/`

## Lint (Health Check)

Run `bash <skill-path>/lint/scripts/lint-wiki.sh [vault_path]`.

Check items:
1. Card index membership and integration classification
2. Flat Cards structure
3. Unresolved wikilink targets
4. Duplicate/near-duplicate titles
5. Staged packages in `10_Inbox/ingest/` or `10_Inbox/writeback/`, including missing or invalid manifests
6. Source reference/provenance health
7. Metadata drift (inconsistent tags, empty sub-tags, missing frontmatter)

Output: structured report in chat. No file writes. Log lint only when it has meaningful findings and the user approves.

## Technical Findings

Agent-discovered corrections with future decision value:

- **MCP config**: goes in `~/.claude.json`, NOT `~/.claude/settings.json`. WebSearch fails with DashScope; WebFetch works; DuckDuckGo + Firecrawl MCPs available.
- **SVG render-check**: always render with `inkscape file.svg -o /tmp/file.png` and inspect PNG. Text near bottom of boxed panels often clips.
- **Chinese sites**: WeChat articles require browser path (Playwright), not `requests`. Mobile UA does NOT bypass captcha.

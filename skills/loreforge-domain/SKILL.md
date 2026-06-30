---
name: loreforge-domain
description: Internal LoreForge workflow for one Card domain's orientation, initialization, generic query, root Sources/Spaces updates, and legacy domain repair after the main entrypoint has resolved config, routing, and write policy. Card and MOC authoring belong to loreforge-card and loreforge-moc.
user-invocable: false
version: 0.3.0
metadata:
  origin: "Inspired by NousResearch Hermes LLM Wiki, MIT"
---

# LoreForge Domain

Use this skill as a delegated orientation, initialization, generic query,
Source/Space update, and legacy repair workflow for one Card domain. For
user-facing routing, configuration, capture, import, checks, Card authoring, or
MOC authoring, use `loreforge` and the focused internal workflows first. When
source-layer details matter, read
[references/raw-first-wiki.md](references/raw-first-wiki.md).

Card and MOC authoring belong to loreforge-card and loreforge-moc. This
workflow may inspect Cards and Atlas views for context, but it does not author
them.

## Always

- Resolve the wiki root, selected Card domain, sync backend, and write policy
  before writing.
- Act as the selected Card-domain expert when interpreting vocabulary and
  boundaries.
- Query existing knowledge first.
- Read `00_System/wiki-layout.md`, `00_System/domains.md`,
  `00_System/card-policy.md`, `00_System/card-domains.md`, and
  `00_System/agent-policy.md` when present.
- Use optional `00_System/card-index.json` as a retrieval cache only; confirm
  important facts from the Markdown pages themselves.
- Keep Card-domain writes inside `Cards/<domain>/` only when a leaf Card
  workflow has been invoked.
- delegate Card authoring to `loreforge-card`.
- delegate Atlas/MOC authoring to `loreforge-moc`.
- Write equations and derivations with Obsidian-compatible LaTeX: inline math
  as `$...$`, standalone equations as `$$...$$`, never as plain-text
  pseudo-notation.

## When This Skill Activates

Use this skill when the main entrypoint delegates one selected Card domain, or
when the user directly asks one selected domain to:

- query a LoreForge wiki or domain
- orient before a leaf Card/MOC workflow writes a page
- ingest an already captured non-paper source when the output is a root
  `Sources/` lens, root `Spaces/` page, or generic repair
- update, revise, or maintain generic Source/Space knowledge that is not a
  Card or MOC
- initialize or repair the root wiki structure and Card-domain registry
- repair legacy `Domains/<domain>/` pages after a lint/check

**DO NOT** use this skill for:

- agent-local memory
- user preferences
- temporary task state
- full chat transcripts
- one-off debugging details
- main-entrypoint routing, sync setup, raw capture-only work, or full checks
- Card authoring; use `loreforge-card`
- Atlas/MOC authoring; use `loreforge-moc`

Do not author Card pages in this workflow. Do not author Atlas/MOC pages in this workflow.

## Wiki Location

The LoreForge main entrypoint should resolve wiki path, domain, and sync before
delegating here. If this skill is called directly, assume those values are
already resolved and avoid broad guessing.

```bash
WIKI_NAME="${WIKI_NAME:-}"
WIKI="${WIKI_PATH:-$HOME/wiki}"
DOMAIN_NAME="${DOMAIN_NAME:-<domain>}"
CARD_DOMAIN="$WIKI/Cards/$DOMAIN_NAME"
LEGACY_DOMAIN="$WIKI/Domains/$DOMAIN_NAME"
```

`~/.config/loreforge/registry.toml` and sync backend choices are owned by
`loreforge-config`. After this skill writes durable wiki files, return the file
change summary so the main entrypoint or `loreforge-config` can run post-write
sync. Do not run a bidirectional sync from this workflow.

If Obsidian config/profile directories exist (`.obsidian*`, such as
`.obsidian-desktop` or `.obsidian-mobile`), treat them as editor state. Do not
query, ingest, import, index, run checks on, or write their contents.

## Architecture: Root Layout

```text
wiki/
  00_System/       # Wiki policy, domain registry, write policy, generated caches
  Atlas/           # Human-facing MOC/view pages; agent writes only on request
  Calendar/        # Daily and weekly notes
  Cards/           # Agent-maintained reusable Card domains
    <domain>/      # One Card domain, e.g. cs, pkm, investment
  Sources/         # Raw packages, paper notes, clippings, source lenses
    Raw/           # Non-paper source packages with origin.md and manifest.md
    Papers/        # Zotero-backed paper notes, one <citekey>.md per paper
    Clippings/     # Optional human-facing clipping notes
  Spaces/          # Projects, work items, people, tools, systems, contexts
  Extras/          # Templates, images, Excalidraw, and other non-source assets
  z-Legacy/        # Imported material waiting for migration
```

Treat `00_System/` as the wiki-level operating surface. Treat `Cards/<domain>/`
as the agent-maintained Card domain. Treat root `Atlas/` as human-facing unless
the caller explicitly asks for a MOC. Treat root `Sources/` and `Spaces/` as
shared durable areas, not domain-local subtrees.

Do not create `Shared/Raw/`, `Shared/Templates/`, or new
`Domains/<domain>/SCHEMA.md`, `index.md`, or `log.md` files in the active root
layout. Those paths are legacy compatibility surfaces only.

## Resuming A Domain

When the user specified a domain, orient before answering or writing:

1. Read `00_System/card-domains.md` and the matching domain entry.
2. Read `00_System/card-policy.md` for Card shape and taxonomy constraints.
3. Read `00_System/agent-policy.md` for write gates, risk levels, and
   transaction requirements.
4. Inspect `Cards/<domain>/` for existing Card pages.
5. Use `00_System/card-index.json` when present to narrow search, then confirm
   matches from Markdown pages.
6. Read relevant root `Atlas/`, `Sources/`, and `Spaces/` pages.
7. Read `Sources/Raw/<source-id>/manifest.md` when provenance matters, and
   read `origin.md` directly only when compiled layers are insufficient.

This orientation prevents duplicate pages, missed cross-references,
contradicting centralized policy, and unneeded source rereads.

For large Card domains, run a quick file search for the topic before creating
anything new. Obsidian Bases, Dataview pages, and `card-index.json` can help
human browsing and rough filtering, but agent indexing should still rely on
filesystem search plus Markdown verification because those views are not a
semantic source of truth.

## Initializing A Wiki Or Card Domain

When delegated to initialize or repair a wiki:

1. Create the wiki root if needed.
2. Create `00_System/`, `00_System/index.md`, `00_System/wiki-layout.md`,
   `00_System/domains.md`, `00_System/card-policy.md`,
   `00_System/card-domains.md`, and `00_System/agent-policy.md` if missing.
3. Create `Calendar/dailynotes/` and `Calendar/weeklynotes/` if missing.
4. Create `Sources/Raw/`, `Sources/Papers/`, and `Sources/Clippings/` if
   missing.
5. Create `Spaces/` if missing.
6. Create `Extras/Templates/`, `Extras/Img/`, and `Extras/Excalidraw/` if
   missing.
7. Create `z-Legacy/` if missing.
8. Create `Cards/<domain>/` if a domain name is provided.
9. Add or update the domain row in `00_System/domains.md` and the detailed
   policy entry in `00_System/card-domains.md`.
10. Return the file change summary so the main entrypoint can run post-write
    sync.

Do not seed per-domain `SCHEMA.md`, `index.md`, or `log.md` files for the root
layout. Domain policy is centralized under `00_System/`; operational history is
reported through final handoff, validator output, and policy-controlled
transactions.

## 00_System Minimal Files

`00_System/index.md` should point humans and agents at the canonical policy
files:

```markdown
# Wiki Index

- Layout: [[wiki-layout]]
- Domains: [[domains]]
- Card policy: [[card-policy]]
- Card domains: [[card-domains]]
- Agent policy: [[agent-policy]]
```

`00_System/wiki-layout.md` should describe the root directories and state that
`Cards/<domain>/` is the agent-maintained Card surface, `Atlas/` is a root
human-facing view layer, non-paper raw packages live in `Sources/Raw/`, paper
notes live in `Sources/Papers/`, and shared non-source assets live in
`Extras/`.

`00_System/agent-policy.md` should contain:

- allowed write roots by page type
- pre-write gate expectations
- post-write validator expectation
- risk levels
- transaction snapshot rules for high-risk writes only
- transaction retention and cleanup expectations

## Page-Type Boundary

- `Cards/<domain>/`: reusable concepts, mechanisms, methods, patterns,
  tradeoffs, comparisons, and decision frameworks. Delegate Card authoring to
  `loreforge-card`.
- `Atlas/`: question-driven views, relationship maps, and human-facing MOCs.
  Delegate Atlas/MOC authoring to `loreforge-moc`.
- `Sources/Raw/<source-id>/`: non-paper source packages owned by
  `loreforge-capture`.
- `Sources/Papers/<citekey>.md`: Zotero-backed paper notes owned by
  `loreforge-paper`.
- `Sources/Clippings/` or other `Sources/` notes: source-specific human or
  agent lenses when the raw package is too large or the user asks for a source
  note.
- `Spaces/`: durable projects, people, tools, systems, organizations, work
  items, proposals, research plans, and contexts. Use `loreforge-work-item` for
  project/work records.
- `Extras/`: templates, images, Excalidraw, and other non-source assets.

Do not force uncertain material into Cards or Atlas. When the page-type
decision is weak, use a conservative Source/Space path or return a blocker.

## Compiled Page Language Gate

Apply the `loreforge` Compiled Page Language Gate before handoff for every
synthesized Source/Space page touched by this workflow.

- Write the durable artifact itself: evidence, decision, context, status,
  reusable implication, or source lens.
- Keep process, placement, routing, and edit-history commentary out of page
  bodies.
- Avoid self-describing boilerplate such as "this page records", "this page
  discusses", "current draft", "moved from", "renamed from", or "I added".
- Prefer direct positive claims. Use negative contrast only when it prevents a
  specific technical misconception.

## Formal Project Artifacts

Formal project artifacts under root `Spaces/`, including `proposal*.md`,
`research-plan*.md`, `literature-survey*.md`, experimental protocols, and
project design notes, are Space pages. They must not be routed to Cards as
related-work notes or to Atlas as active proposal drafts once a project
directory exists.

When this workflow repairs or updates a project artifact, apply
`loreforge-work-item`'s "Formal Project Artifacts" gate before handoff.
Literature surveys should compare mechanisms, assumptions, scope, IR level,
backend coverage, artifact generation, and evaluation signals. Research plans
should use milestone, artifact, experiment, and validation language.

## Source Capture

Raw source packages live under `Sources/Raw/<source-id>/`. Capture writes the
raw package only; it does not create Cards, Atlas pages, Spaces, or non-raw
Source notes. Ingest may update the package metadata and compile durable pages
from it.

Use `origin.md` for canonical agent-readable source text or for a thin wrapper
around preserved artifacts. Use `manifest.md` for title, canonical URL or
source description, retrieval date, source type, source language,
`content_hash`, `origin`, `candidate_domains`, `compiled_pages`, status,
artifact pointers, and extraction lineage.

For web pages, use a clipper-style capture plan before synthesis: save an
original artifact when possible, extract deterministic page variables such as
title, author, published date, site, language, meta tags, schema.org data,
selection/highlights, and clean article content, apply site-specific CSS
selectors only when the main extractor misses stable structure, localize
important assets, and record the extractor/source-mode/selector decisions in
`manifest.md`. Obsidian Web Clipper exports or `obsidian-clipper` CLI/API
output can be used as capture input when available.

Optional Source notes under `Sources/` are compact source-specific lenses over
large raw packages. They should link back to the raw manifest, preserve the
source language unless the user asked otherwise, and contain only the extracted
slice needed for future work.

Compiled pages do not use YAML `sources:` for provenance. Prefer
path-qualified inline wikilinks to wiki-local raw artifacts, raw manifests,
paper notes, or Source notes, such as
`[[Sources/Raw/<source-id>/manifest|readable source alias]]` or
`[[Sources/Papers/<citekey>|paper alias]]`. Use source footnotes only when
paragraph-level provenance would otherwise be ambiguous, especially in
multi-source synthesis.

## Paper Ingest Handoff

Papers have their own workflow in `loreforge-paper`. When this workflow
receives a paper handoff, treat Zotero as the paper manifest/raw-file system.
Do not require or create `Sources/Raw/` paper packages, paper manifests,
`origin.md`, copied PDFs, or Source notes just for provenance.

Paper notes live under `Sources/Papers/<citekey>.md`. Keep Zotero PDFs and
attachments read-only and outside the vault. If a paper request reaches this
skill without paper-specific context, read `skills/loreforge-paper/SKILL.md`
before writing any downstream Source/Space page.

## Work Item Handoff

Project work items have their own workflow in `loreforge-work-item`. When this
workflow receives a work-item handoff, follow the root `Spaces/` boundary and
apply the work-item shape: problem background, desired behavior, solution,
implementation details, bug diagnosis and fixes, verification, current status,
and follow-ups.

Work-item pages are durable project records, not activity logs. Do not save
chat transcripts, command-by-command chronology, raw CI logs, or temporary task
state. If a work-item request reaches this skill without work-item-specific
context, read `skills/loreforge-work-item/SKILL.md` before writing the page.

## Spaces

Use root `Spaces/` for durable non-Card objects and context notes:

- people
- organizations
- projects
- tools
- systems
- communities
- products
- research groups
- work items
- archived pages

One page per notable person, entity, tool, or project. Include overview, key
facts and dates, relationships to other pages, and source references when they
matter. Prefer coarse tags and natural wikilinks over broad mechanical related
lists.

## Legacy Domain Repair

Old LoreForge wikis may still contain:

```text
Domains/<domain>/
  SCHEMA.md
  index.md
  log.md
  Atlas/
  Cards/
  Sources/
  Spaces/
Shared/Raw/
Shared/Templates/
```

Treat these paths as legacy inputs. Read them when needed for migration,
validation, or compatibility, but do not create new pages there unless the user
explicitly asks to repair a legacy wiki in place.

Preferred migration targets:

- `Domains/<domain>/Cards/*.md` -> `Cards/<domain>/*.md`
- `Domains/<domain>/Atlas/*.md` -> root `Atlas/*.md`
- `Domains/<domain>/Sources/*` -> root `Sources/`
- `Domains/<domain>/Spaces/*` -> root `Spaces/`
- `Shared/Raw/<source-id>/` -> `Sources/Raw/<source-id>/`
- `Shared/Templates/*` -> `Extras/Templates/`
- domain `SCHEMA.md`, `index.md`, and `log.md` -> centralized `00_System/`
  policy plus validator/report output

Ask before migrating 10+ pages or deleting legacy files. For high-risk
migrations, follow `00_System/agent-policy.md` and create a transaction
snapshot only when policy requires it.

---
name: loreforge-moc
description: Internal LoreForge leaf workflow for creating or updating Atlas/MOC pages under Domains/<domain>/Atlas with a strict view decision, human-readable relationship structure, and post-write acceptance gate.
user-invocable: false
version: 0.1.0
---

# LoreForge MOC

Use this workflow only for `Domains/<domain>/Atlas/` pages that act as Maps of
Content, question-driven views, proposal views, or problem framing pages. It is
a leaf authoring workflow, not a router. The `loreforge` entrypoint chooses
this workflow after resolving wiki, domain, write permission, and sync.

A MOC is a human-readable view over relationships. It is not an index mirror,
not a Card list, and not a source summary.

## Hard Gate

Before writing, make a page-type decision:

```text
page_type_decision:
  selected: moc
  view_question: <the problem, claim, project, decision, or comparison this view answers>
  reason: <why relationships/current judgment matter more than one reusable definition>
  rejected:
    card: <why this is not a single reusable concept/method/mechanism>
    source: <why this is not just a source excerpt or source summary>
    space: <why this is not a project/person/tool/system/context record>
```

Do not write a MOC without a clear view question. Return control to `loreforge`
for a Card, Source lens, Space, paper workflow, work-item workflow, or blocker
question.

## Orientation

Read before writing:

1. `Domains/<domain>/SCHEMA.md`
2. `Domains/<domain>/index.md`
3. latest 20-30 entries from `Domains/<domain>/log.md`
4. relevant `Cards/`, `Spaces/`, `Sources/`, and existing `Atlas/` pages
5. `Shared/Raw/<source-id>/manifest.md` when provenance matters

Search for the topic before creating a new page. Update an existing MOC when a
view already exists.

## MOC Contract

Create or update a MOC only for:

- a question-driven or problem-driven view
- proposal, project, or decision framing
- a relationship map across multiple Cards, Spaces, Sources, or prior views
- comparison that depends on current interpretation and open decisions

Do not use a MOC for:

- a single stable concept that belongs in a Card
- a mechanical inventory that belongs in `index.md`
- a paper-shaped review or long source summary
- a project record that belongs in `Spaces/projects/`

Required shape:

- YAML frontmatter with `title`, `created`, `updated`, `type: map`, `tags`,
  `confidence`, `status`, `contested`, and `contradictions`.
- H1 matches the title.
- Early paragraph states the view question or current problem.
- Body explains relationships, not just page names.
- Links to Cards, Spaces, Sources, or other Atlas pages are woven into the
  prose with readable aliases where useful.
- Includes current judgment, interpretation, tradeoffs, open decisions, or
  remaining questions when the view calls for them.
- Update `index.md` under `## Atlas` and insert a newest-first `log.md` entry.

## Zettelkasten Adaptation

Treat MOCs as Zettelkasten-style structure notes for this domain:

- A MOC is an entry point into a cluster of Cards, Spaces, Sources, and other
  views.
- The page explains why the linked notes belong together and what question,
  problem, claim, project, or decision the cluster helps answer.
- Links are not a bibliography or a broad related-pages dump. Each link should
  sit near the relationship, contrast, dependency, sequence, or tension it
  helps explain.
- When the MOC starts accumulating definitions, extract those definitions into
  Cards and keep the MOC as the relationship view.

Do not copy the physical Zettelkasten numbering/sequence system into
LoreForge. Use readable filenames, aliases, natural wikilinks, `index.md`,
`log.md`, and MOCs as the navigation layer.

## Writing Style

Write for a human trying to understand how pieces connect.

Apply the `loreforge` Compiled Page Language Gate before handoff.

Prefer:

- concise overview of the problem or claim
- relationship map in prose or compact bullets
- current interpretation and tradeoffs
- open decisions or next questions

Avoid:

- standalone "related Cards" or "related pages" tables whose main purpose is
  bookkeeping
- copying the domain index
- hiding the current argument behind a broad list of links
- turning the page into a source summary

MOCs may carry project framing, current arguments, open decisions, and
commentary about how reusable Cards connect. Keep reusable definitions in
Cards and link to them naturally.

## Provenance

Do not use YAML `sources:` for compiled-page provenance.

For wiki-local raw artifacts, manifests, or domain Source notes, prefer inline
wikilinks using the filename or stem with an alias when useful. Use source
footnotes only when paragraph-level provenance would otherwise be ambiguous.

Cards, Spaces, and Atlas pages linked from the MOC are semantic knowledge
links, not source citations.

## Default Template

```markdown
---
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: map
tags: []
confidence: medium
status: active
contested: false
contradictions: []
---

# Page Title

This view asks: ...

## Current View

## Key Relationships

## Tradeoffs

## Open Questions
```

Use only the sections that help the page. Do not create empty headings.

## Acceptance Gate

Before reporting completion, check:

- The page-type decision selected `moc` and named a clear view question.
- The page is not mainly an index mirror, source summary, project record, or
  single-concept Card.
- The page explains relationships or current judgment in human-readable prose.
- The page acts as a structure note: an entry point with relationship context,
  not a broad link dump.
- Links are woven naturally into the body rather than listed mechanically.
- Reusable definitions stay in Cards; project/current-view commentary stays in
  the MOC.
- `index.md` and `log.md` were updated.

If any item fails, repair the page before handoff or report a blocker instead
of landing a weak MOC.

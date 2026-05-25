---
name: loreforge-card
description: Internal LoreForge leaf workflow for creating or updating reusable Card pages under Domains/<domain>/Cards with a strict page-type decision, narrow Card structure, provenance rules, and post-write acceptance gate.
user-invocable: false
version: 0.1.0
---

# LoreForge Card

Use this workflow only for `Domains/<domain>/Cards/` pages. It is a leaf
authoring workflow, not a router. The `loreforge` entrypoint chooses this
workflow after resolving wiki, domain, write permission, and sync. If called
directly, assume those values are already resolved.

Cards are shared reusable knowledge objects for a domain. A Card should make
future human reading and future agent retrieval easier by answering a stable
"what is it" and "what is it good for" question without carrying project,
proposal, or source-summary clutter.

## Hard Gate

Before writing, make a page-type decision:

```text
page_type_decision:
  selected: card
  reason: <why this is reusable concept/method/mechanism/pattern/tradeoff/comparison>
  rejected:
    moc: <why this is not primarily a view over several pages>
    source: <why this is not just a source excerpt or source summary>
    space: <why this is not a project/person/tool/system/context record>
```

Do not write a Card when the decision is weak. Return control to `loreforge`
for a MOC, Source lens, Space, paper workflow, work-item workflow, or a blocker
question.

## Orientation

Read before writing:

1. `Domains/<domain>/SCHEMA.md`
2. `Domains/<domain>/index.md`
3. latest 20-30 entries from `Domains/<domain>/log.md`
4. existing Card candidates from `Cards/`
5. relevant `Atlas/`, `Sources/`, and `Spaces/` pages
6. `Shared/Raw/<source-id>/manifest.md` when provenance matters

Search for the topic before creating a new page. Update an existing Card when a
stable concept already exists.

## Card Contract

Create or update a Card only for:

- durable concepts
- mechanisms or methods
- reusable patterns
- tradeoffs or constraints
- comparisons and decision frameworks

Do not use a Card for:

- proposal evidence, project framing, or current task commentary
- paper-shaped review or long source summary
- project records, bugfix records, PR/MR notes, or CI failure narratives
- broad relationship maps or problem-specific views
- passing mentions that are not reusable domain knowledge

Required shape:

- YAML frontmatter with `title`, `created`, `updated`, `type: concept`,
  `aliases`, `tags`, `confidence`, `status`, `contested`, and
  `contradictions`.
- `aliases` must contain at least one human-searchable name, acronym, spelling
  variant, Chinese/English term, or short readable label. Do not use aliases as
  a tag dump.
- H1 matches the title.
- First body paragraph is a direct definition or problem statement. Do not
  start with "this Card explains", "this page discusses", or equivalent
  self-description.
- Body focuses on definition, mechanism, constraints, examples, limits, and
  open questions.
- At least two meaningful outbound `[[wikilinks]]` when related pages exist.
- Update `index.md` under `## Cards` and insert a newest-first `log.md` entry.

## Writing Style

Write Cards like concise reference entries. Prefer direct definitions,
mechanisms, constraints, examples, and open questions.

Keep Card prose reusable:

- Avoid proposal framing, project support arguments, and current-view
  commentary.
- Avoid dumping a source summary. Extract the durable concept instead.
- Prefer direct positive descriptions. Use negative contrast only when it
  prevents a concrete likely misconception.
- Do not add mechanical "related Cards" sections. Weave semantic
  `[[wikilinks]]` into the relevant sentence.
- Optional `related:: [[concept-a]], [[concept-b|Readable label]]` fields may
  be used near the top only for relevant pages not naturally mentioned in the
  body. Do not add `related::` by default and do not repeat body links.

## Provenance

Do not use YAML `sources:` for compiled-page provenance.

For wiki-local raw artifacts, manifests, or domain Source notes, prefer inline wikilinks.
Use the filename or stem with an alias when useful:
`[[source-artifact-or-manifest|readable source alias]]`.

Use source footnotes only when paragraph-level provenance would otherwise be
ambiguous, especially in multi-source synthesis. In a single-source Card, link
the dominant source once or in a small number of boundary-setting locations
instead of repeating the same marker in every paragraph.

Knowledge links to Cards, Atlas pages, and Spaces are semantic wiki links, not
source citations. Do not cite Cards with source-style footnote markers.

## Default Template

```markdown
---
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: concept
aliases:
  - Page Title
tags: []
confidence: medium
status: active
contested: false
contradictions: []
---

# Page Title

One-sentence direct definition or problem statement.

## Why

## What Is Page Title

## Constraints

## Open Questions
```

Use only the sections that help the page. Do not reserve a mandatory proposal,
project, or source-summary section inside Cards.

## Acceptance Gate

Before reporting completion, check:

- The page-type decision selected `card` for a reusable concept, method,
  mechanism, pattern, tradeoff, or comparison.
- The page is not mainly a source summary, project record, proposal argument,
  or MOC.
- Frontmatter includes non-empty `aliases`.
- The first body paragraph is a direct definition or problem statement.
- Related pages are linked naturally in the body.
- Provenance is represented with wiki-local links or sparse footnotes only
  where useful.
- `index.md` and `log.md` were updated.

If any item fails, repair the page before handoff or report a blocker instead
of landing a weak Card.

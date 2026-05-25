---
name: loreforge-domain
description: Internal LoreForge workflow for one domain's orientation, initialization, generic query, Sources/Spaces updates, and legacy domain repair after the main entrypoint has resolved config, routing, and write policy. Card and MOC authoring belong to loreforge-card and loreforge-moc.
user-invocable: false
version: 0.2.0
metadata:
  origin: "Inspired by NousResearch Hermes LLM Wiki, MIT"
---

# LoreForge LLM Wiki

Build and maintain a persistent, compounding Markdown wiki for one expert-owned
domain.

LoreForge follows the [LLM Wiki](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/llm-wiki/SKILL.md)
pattern: capture the raw source package once, compile it during ingest, keep
durable knowledge linked, and update it as questions arrive. It adds expert-owned
domains, reusable Cards, and Atlas MOCs for preserving evolving project and
conceptual views.

Use this skill as a delegated domain orientation, initialization, and generic
domain maintenance workflow. For user-facing routing, configuration, capture,
import, checks, Card authoring, or MOC authoring, use `loreforge` and the
focused internal workflows first. When source-layer details matter, read
[references/raw-first-wiki.md](references/raw-first-wiki.md).

Always:

- act as the domain expert
- query existing knowledge first
- update pages directly after orientation
- keep `index.md` and `log.md` current
- delegate Card authoring to `loreforge-card`
- delegate Atlas/MOC authoring to `loreforge-moc`
- write equations and derivations with Obsidian-compatible LaTeX: inline math
  as `$...$`, standalone equations as `$$...$$`, never as plain-text
  pseudo-notation

## When This Skill Activates

Use this skill when the main entrypoint delegates one expert-owned domain, or when
the user directly asks one selected domain to:

- query a LoreForge wiki or domain
- ingest an already captured source, raw package, URL, paper, doc, repo, local
  file, or pasted material into one selected domain when the output is a
  `Sources/` lens, `Spaces/` page, or generic domain repair
- update, revise, or maintain generic domain knowledge that is not a Card or MOC
- create a domain wiki
- apply domain page fixes from a lint or check
- repair or orient a domain before a leaf workflow writes a page

**DO NOT** use this skill for:

- agent-local memory
- user preferences
- temporary task state
- full chat transcripts
- one-off debugging details
- main-entrypoint routing, sync setup, raw capture-only work, or full checks
- Card authoring; use `loreforge-card`
- Atlas/MOC authoring; use `loreforge-moc`

Those belong in the agent runtime or memory system, not in the shared wiki.

## Wiki Location

The LoreForge main entrypoint should resolve wiki path, domain, and sync before
delegating here. If this skill is called directly, assume those values are
already resolved and avoid broad guessing.

```bash
WIKI_NAME="${WIKI_NAME:-}"
WIKI="${WIKI_PATH:-$HOME/wiki}"
DOMAIN_NAME="${DOMAIN_NAME:-<domain>}"
DOMAIN="$WIKI/Domains/$DOMAIN_NAME"
```

`~/.config/loreforge/registry.toml` and sync backend choices are owned by
`loreforge-config`. After this skill writes durable wiki files, return the file
change summary so the main entrypoint or `loreforge-config` can run post-write sync.
For rclone-backed wikis, the caller should pull the configured remote before
this skill orients on domain files and push after this skill reports its local
changes. Do not run a bidirectional sync from this domain workflow.

The wiki is just a directory of Markdown files — open it in Obsidian, VS Code,
or any editor. No database, no special tooling required.

If Obsidian config/profile directories exist (`.obsidian*`, such as
`.obsidian-desktop` or `.obsidian-mobile`), treat them as editor state. Do not
query, ingest, import, index, run checks on, or write their contents.

## Architecture: Multi-Layer Wiki

```text
wiki/
  00_System/       # Wiki-level entrypoints, shared protocols, views, and domain registry
  Calendar/        # Date-based notes such as daily notes
    dailynotes/    # Default daily-note folder
    weeklynotes/   # Default weekly planning folder
  Shared/          # Raw source packages and reusable templates
    Raw/           # Raw source packages with origin.md and manifest.md
    Templates/     # Wiki-level reusable note templates, such as diary templates
  Domains/         # Expert-owned domain wiki collection
    <domain>/      # One domain maintained by one expert agent
```

```text
Domains/<domain>/
  SCHEMA.md        # Domain boundary, conventions, taxonomy, and update rules
  index.md         # Mechanical inventory with one-line page summaries
  log.md           # Reverse chronological action log, newest entry first
  Atlas/           # Maps of Content (MOCs), emergent thinking views
  Cards/           # Durable concepts, methods, patterns, tradeoffs, comparisons
  Sources/         # Optional source excerpts or source-specific lenses
  Spaces/          # Durable people, orgs, projects, tools, systems, contexts
```

Treat `00_System/` as the wiki-level operating surface. Treat each
`Domains/<domain>/` as a self-contained LLM Wiki for a single expert-owned
domain. Treat `Shared/Raw/` and `Shared/Templates/` as the shared raw source
and template infrastructure for the whole wiki. Treat `Calendar/` as
wiki-level dated personal notes, not as a domain knowledge area.

Do not create a wiki-root `Shared/SourceRecords/` layer in the active
structure. If an old wiki still has one, import raw capture material to
`Shared/Raw/`. Capture derives a source-id and writes
`Shared/Raw/<source-id>/origin.md` plus `manifest.md`. Domain `Sources/` is
optional and should be used only when a domain needs a compact excerpt or
source-specific lens over a large raw package.

Create `Domains/<domain>/Extras/` only when a domain truly needs local
non-source attachments.

Orient, query, ingest, and update inside the selected domain. Apply delegated
domain page fixes from checks when requested. DO NOT write across
domains unless the user explicitly asks. During ingest, update the raw package
under `Shared/Raw/<source-id>/`, then compile reusable knowledge from it. Only
write `Calendar/` or `Shared/Templates/`
when the user explicitly asks for daily-note, weekly-note, diary, calendar,
planning, or reusable template work.

## Resuming an Existing Domain (CRITICAL — do this every session)

When the user specified a domain, **always orient yourself before doing anything**:

1. Read `SCHEMA.md`.
2. Read `index.md`.
3. Read the latest 20-30 entries from `log.md`.
4. Search existing pages for the topic.
5. Read relevant `Atlas/`, `Cards/`, `Sources/`, and `Spaces/` pages; read
   `Shared/Raw/<source-id>/manifest.md` when provenance matters, and read
   `origin.md` directly only when the compiled layers are insufficient.

Only after orientation should you ingest, query, or update. This orientation
prevents:

- Creating duplicate pages for entities that already exist
- Missing cross-references to existing content
- Contradicting the schema's conventions
- Repeating work already logged

For large domains(100+ pages), also run a quick search for the topic at hand before creating anything new.

## Initializing a New Wiki or Domain

When delegated to create or start a wiki or domain:

1. Create the wiki root if needed.
2. Create `00_System/`, `00_System/index.md`, `00_System/domains.md`, and
   `00_System/wiki-layout.md` if missing.
3. Create `Calendar/`, `Calendar/dailynotes/`, and `Calendar/weeklynotes/` if
   missing.
4. Create `Shared/Raw/` and `Shared/Templates/` if missing.
5. Create the minimal `Shared/Templates/weekly.md` below if missing. Preserve
   an existing weekly template unless the user explicitly asks to rewrite it.
6. Create `Domains/<domain>/`.
7. Create the required domain files and directories above.
8. Ask for a concise domain description and the default language for extracted
   Cards, Atlas pages, and Spaces.
9. Write `SCHEMA.md` customized to the domain (see template below).
10. Write `index.md` with sectioned header and `wiki-layout.md` with the
   canonical shared/domain layout summary.
11. Write initial `log.md` with creation entry.
12. Add or update the domain row in `00_System/domains.md`.
13. Return the file change summary so the main entrypoint can run post-write sync.

### Shared Templates

Weekly templates are human-facing Obsidian notes. Users may freely customize
their headings and review style; LoreForge should require only the template
path, not a strict template body.

`Shared/Templates/weekly.md`:

```markdown
---
date: "{{date:gggg-[W]ww}}"
type: weekly
tags:
  - weekly
---

# {{title}}

## Focus

## This Week

- [ ]

## Daily Notes

- [[{{monday:YYYY-MM-DD}}|Mon]]
- [[{{tuesday:YYYY-MM-DD}}|Tue]]
- [[{{wednesday:YYYY-MM-DD}}|Wed]]
- [[{{thursday:YYYY-MM-DD}}|Thu]]
- [[{{friday:YYYY-MM-DD}}|Fri]]
- [[{{saturday:YYYY-MM-DD}}|Sat]]
- [[{{sunday:YYYY-MM-DD}}|Sun]]

## Risks / Blockers

-

## Decisions

-

## Review

- Done:
- Carry forward:
```

### 00_System Minimal Files

Use `00_System/` for wiki-level orientation only. Domain behavior still lives in
each domain's `SCHEMA.md`.

`00_System/index.md`:

```markdown
# Wiki Index

- Layout: [[wiki-layout]]
- Domains: [[domains]]
```

`00_System/wiki-layout.md`:

```markdown
# Wiki Layout

Canonical shared layer:

- `Shared/Raw/<source-id>/` for raw source packages and attachments
- `Shared/Templates/` for reusable templates

Domain layer:

- `Domains/<domain>/Atlas/` for durable maps and conceptual views
- `Domains/<domain>/Cards/` for durable concepts and comparisons
- `Domains/<domain>/Sources/` for optional source excerpts or source-specific lenses
- `Domains/<domain>/Spaces/` for durable people, tools, projects, and contexts

Capture writes raw source packages into `Shared/Raw/<source-id>/` and stops
there. Ingest updates those packages and compiles durable synthesis into
`Atlas/`, `Cards/`, and `Spaces/`. Optional domain source excerpts live in
`Sources/`. Compiled pages should prefer plain internal wikilinks to wiki-local
raw artifacts, raw manifests, or domain source notes; use source footnotes only
when paragraph-level provenance would otherwise be ambiguous.
```

Create `Domains/<domain>/Extras/` only when the domain needs its own
non-source attachments.

`00_System/domains.md`:

```markdown
# Domains

| Domain | Purpose | Default Language | Expert | Status |
|---|---|---|---|---|
| <domain> | <purpose> | <language> | <expert name or role> | active |
```

### SCHEMA.md Template

Adapt to the user's domain. The schema constrains agent behavior and ensures consistency. Use these minimal templates when initializing a domain:

````markdown
# Schema

## Domain
[What this domain covers — e.g., "AI/ML research", "personal health", "startup intelligence"]

## Language Policy
- Raw packages preserve the source language by default. Optional domain Source
  notes preserve it too.
- Extracted Cards, Atlas pages, and Spaces use this domain's configured default note language: `[language]`.
- If this policy is missing, ask once before creating synthesized pages, then add it to `SCHEMA.md`.
- Do not translate source material unless the user asks for translation or bilingual notes.

## Conventions
- File names: lowercase, hyphens, no spaces (e.g., `transformer-architecture.md`)
- Every wiki page starts with YAML frontmatter (see below)
- Every Card frontmatter includes `aliases`, a short list of human-searchable
  names, acronyms, spelling variants, or common Chinese/English names. Keep
  `title` as the canonical page name; use `aliases` only to improve search.
- Use `[[wikilinks]]` to link between pages (minimum 2 outbound links per page)
- When updating a page, always bump the `updated` date
- Every new page must be added to `index.md` under the correct section
- Every action must be inserted into `log.md` as the newest entry
- Optional `related:: [[concept-a]], [[concept-b|Readable label]]` fields may
  be used near the top of Cards or Atlas pages as a light navigation seed for
  relevant pages that are not naturally mentioned in the body. Use aliases when
  the page title would be awkward in context. Do not add `related::` by default,
  do not repeat links already expressed naturally in the body, and do not use it
  as a substitute for semantic in-body wikilinks.
- Write equations and derivations with LaTeX math: use `$...$` for inline
  expressions and `$$...$$` for standalone equations.
- **Provenance links:** Do not use YAML `sources:` for compiled-page provenance.
  When the source is already a wiki-local raw artifact, raw manifest, or domain
  Source note, prefer an inline wikilink using the note filename/stem and an
  alias when useful, such as `[[clip-name|readable alias]]`. Use a source
  footnote only when paragraph-level provenance would otherwise be ambiguous,
  especially in multi-source synthesis where adjacent claims come from different
  sources. Do not add the same source marker to every paragraph in a
  single-source Card or Source lens.
- **Knowledge links:** Links to Cards, Atlas pages, and Spaces are semantic wiki
  links, not provenance markers. Insert them naturally where the concept is
  used, and use aliases when needed for readable prose, e.g.
  `[[kv-cache-memory-hierarchy|KV cache hierarchy]]`. Do not cite Cards with
  source-style footnote markers or append mechanical Card references at the end
  of paragraphs. Body wikilinks are preferred over maintaining a broad
  `related::` list.

## Writing Style
- Write domain `Sources/` and `Spaces/` pages as durable reference material,
  not process narration.
- Prefer direct positive descriptions over repeated "not X but Y" framing.
  Use negative contrast only when it prevents a specific misconception.
- Do not write Card or MOC prose in this workflow. Delegate Card pages to
  `loreforge-card` and MOC pages to `loreforge-moc` so their acceptance gates
  run before handoff.

## Frontmatter
```yaml
---
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: map | concept | source | space
tags: []
confidence: high | medium | low
status: active | tentative | archived
contested: false
contradictions: []
---
```
confidence and contested are optional but recommended for opinion-heavy or fast-moving topics. Lint surfaces contested: true and confidence: low pages for review so weak claims don't silently harden into accepted wiki fact.

## Tag Taxonomy

Tags are a small domain-internal classification surface, not a keyword dump.
Prefer 1-3 tags per page and only use tags that help stable filtering across
the domain. If a page feels like it needs many tags, split the page or tighten
the taxonomy before adding more tags.

[Define 10-20 top-level tags for the domain. Add new tags here BEFORE using them.]

Example for AI/ML:
- Models: model, architecture, benchmark, training
- People/Orgs: person, company, lab, open-source
- Techniques: optimization, fine-tuning, inference, alignment, data
- Meta: comparison, timeline, controversy, prediction

Rule: every tag on a page must appear in this taxonomy. Keep page tags coarse
and minimal; if you need more than 3 tags on a page, pause and reassess whether
the page should be split or the taxonomy should be narrowed first. This
prevents tag sprawl.

## Page Thresholds
- **Create a page** when an entity/concept appears in 2+ sources OR is central to one source
- **Add to existing page** when a source mentions something already covered
- **DON'T create a page** for passing mentions, minor details, or things outside the domain
- **Split a page** when it exceeds ~200 lines — break into sub-topics with cross-links
- **Archive a page** when its content is fully superseded — move to `_archive/`, remove from index
- For MOCs, use view quality rather than source count. Create one ONLY when a
reusable thinking view exists.

## Atlas/MOC Pages
Do not author Atlas/MOC pages in this workflow. Delegate to `loreforge-moc`
after domain orientation and page-type decision. The MOC leaf workflow owns the
view question, relationship structure, writing contract, and acceptance gate.

## Cards
Do not author Card pages in this workflow. Delegate to `loreforge-card` after
domain orientation and page-type decision. The Card leaf workflow owns
reusable concept boundaries, `aliases`, writing style, provenance rules, and
the Card acceptance gate.

## Extras
Create domain `Extras/` only for non-source attachments owned by this domain:
- diagrams
- reusable templates or other non-note assets

Put source PDFs, images, HTML snapshots, origin captures, and manifest files
under `Shared/Raw/<source-id>/`, not under domain `Extras/`.

If `Extras/` exists, do not index it directly. Link domain attachments from
relevant Cards or Atlas pages.

## Source Capture

Raw source packages live under `Shared/Raw/<source-id>/`. Domain pages do not
keep YAML `sources:` links. Optional domain `Sources/` pages are compact
excerpt notes or source-specific lenses over large raw packages. Compiled
`Cards/`, `Atlas/`, `Spaces/`, and `Sources/` pages prefer internal wikilinks
to wiki-local raw artifacts, raw manifests, or domain source notes. Do not use
YAML source links. Use source footnotes only for genuinely ambiguous
paragraph-level provenance.

### Paper Ingest Handoff

Papers have their own workflow in `loreforge-paper`. When this domain skill
receives a paper handoff, follow the domain boundary and schema while applying
the paper-specific shape from `loreforge-paper`: paper identity, problem,
mechanism, assumptions, evaluation signal, limits, reusable implications,
natural concept links, and related paper/problem cases.

Do not mix the paper workflow into ordinary single-source ingest. If a paper
request reaches this skill without paper-specific context, read
`skills/loreforge-paper/SKILL.md` before writing the domain page.

### Work Item Handoff

Project work items have their own workflow in `loreforge-work-item`. When this
domain skill receives a work-item handoff, follow the domain boundary and
schema while applying the work-item shape: problem background, desired behavior,
solution, implementation details, bug diagnosis and fixes, verification,
current status, and follow-ups.

Work-item pages are durable project records, not activity logs. Do not save
chat transcripts, command-by-command chronology, raw CI logs, or temporary task
state. If a work-item request reaches this skill without work-item-specific
context, read `skills/loreforge-work-item/SKILL.md` before writing the domain
page.

### Single-Source Ingest Style

Single-source ingest covers non-paper source material such as articles, docs,
transcripts, reports, local notes, or web pages. Its goal is to preserve the
source and compile the useful domain slice, not to force a paper-shaped review.

- Decide whether the source should become a compact `Sources/<source-id>.md`
  lens, update existing Spaces, or hand off to `loreforge-card` /
  `loreforge-moc` for Card/Atlas authoring.
- Keep the synthesized page about reusable domain knowledge. Do not include
  editor/process narration.
- Prefer inline wikilinks to wiki-local source artifacts or manifests, using the
  file stem and alias syntax when useful. Use source footnotes only when a
  multi-source page needs paragraph-level provenance disambiguation. For a
  single-source Card or Source lens, link the dominant source once or in a small
  number of boundary-setting locations instead of mechanically repeating the
  same source marker on every paragraph.
- Weave semantic `[[wikilinks]]` into prose for concepts already represented in
  the wiki. Use direct positive descriptions and avoid mechanical related-link
  lists. For reusable concepts or relationship views, hand off to
  `loreforge-card` or `loreforge-moc` instead of writing them here.

### Source Capture Policy

- Preserve the shared raw source before synthesizing cards.
- Capture writes the raw source package only. It does not create Cards, Atlas
  pages, Spaces, or domain `Sources/` pages.
- Ingest updates the package under `Shared/Raw/<source-id>/` and compiles
  durable domain pages from it.
- The manifest should record title, canonical URL or source description,
  retrieval date, source type, source language, `content_hash`, `origin`,
  `candidate_domains`, `compiled_pages`, status, and local artifact pointers.
- Keep `origin.md` in the source language and preserve structure, links, and
  image refs where possible. For human-captured Markdown/HTML/PDF artifacts,
  preserve the original export unchanged under `original/` with the original
  filename; use `origin.md` only as a thin wrapper when duplicating or rewriting
  the full export would reduce fidelity. Prefer complete transcription when the
  material is user-provided, local, permissively licensed, public domain, or
  otherwise appropriate to reuse in full. For third-party web pages where full
  transcription is not appropriate, keep a faithful structured capture with
  specific excerpts and grounded notes; do not add generic boilerplate unless a
  concrete capture limitation matters.
- Article images/diagrams, PDFs, and other attachments belong in the raw
  package directory with clear local references from `origin.md` and the
  manifest.
- Optional domain Source note: create or update `Domains/<domain>/Sources/<source-id>.md`
  only when the raw package is large, when a source-specific excerpt should stay
  queryable, or when multiple compiled pages need a stable local lens. A source
  note should preserve source language, link back to the raw manifest, and keep
  only the extracted slice needed by the domain.
- Language: raw packages and optional domain Source notes preserve the source
  language by default. Synthesized Cards, Atlas pages, and Spaces use the
  domain default note language from `SCHEMA.md`.
- Durable local paths in raw packages must point to wiki-local files, such as
  `Shared/Raw/...`. Do not put transient extractor paths such as
  `/tmp/topic-research/...` in source metadata; if those paths are useful for
  debugging, record them in `log.md` only.

### Built-In Capture Tools

- For web topics, direct links, Zhihu, WeChat, and pages that need browser
  state, use the bundled `topic-research` skill before writing raw source
  packages, optional domain Source notes, or compiled domain pages.
- For local documents or exported files, use `convert-to-markdown` when it can
  preserve structure or extract images better than manual conversion.
- For standard web pages where a lightweight extractor is enough, `defuddle`
  can provide clean Markdown before ingest.
- Auth/session files used by capture tools belong in the tool's local `auth/`
  directory or another machine-local path and must not be committed.

## Spaces
Use `Spaces/` for durable non-Card objects and context notes:
- people
- organizations
- projects
- tools
- systems
- communities
- products
- research groups
- archived pages

Use tags to distinguish Spaces. Index active Spaces tagged `person`, `entity`,
`tool`, or `project`. Do not index `Spaces/_archive/` or transient workspace
notes.

One page per notable person, entity, tool, or project. Include:
- Overview / what it is
- Key facts and dates
- Relationships to other pages ([[wikilinks]])
- Source references

## Update Policy
When new information conflicts with existing content:
1. Check the dates — newer sources generally supersede older ones
2. If genuinely contradictory, note both positions with dates and sources
3. Mark the contradiction in frontmatter: `contradictions: [page-name]`
4. Flag for user review in the lint report
5. **Ask before updating 10+ existing pages.**
````

### index.md Template

The index is sectioned by type. Each entry is one line: wikilink + summary.

```markdown
# Domain Index

> Mechanical inventory. Every active Markdown page under Atlas, Cards, Sources,
> and indexable Spaces should appear here with a one-line summary.
> Index Spaces only when tagged `person`, `entity`, `tool`, or `project`.
> Do not index `Spaces/_archive/` or transient workspace notes.
> Last updated: YYYY-MM-DD | Total pages: N

## Atlas

## Cards

## Sources

## Spaces
```

**Scaling rule:** When any section exceeds 50 entries, split it into sub-sections
by first letter or sub-domain. When the index exceeds 200 entries total, create
a `Atlas/Scope/topic-map.md` that groups pages by theme for faster navigation.

### log.md Template

```markdown
# Domain Log

> Reverse chronological audit trail. Newest entries go first.
> Insert each new entry directly below this instruction block.
> Format: `## YYYY-MM-DD | <action> | <subject>`
> Actions: create, query, ingest, update, lint, archive, delete

## YYYY-MM-DD | create | Domain initialized
- domain: <domain>
- default_note_language: <language>
- files: SCHEMA.md, index.md, log.md
```

**Rotate the log** — when log.md exceeds 500 entries, rename it `log-YYYY.md` and start fresh.
  The agent should check log size during lint.

**Log insertion rule:** Do not append new entries to the bottom. Insert the new
entry directly after the `# Domain Log` heading and any leading `>` instruction
block, before the previous newest `## YYYY-MM-DD | ...` entry. Do not reorder or
rewrite older entries unless correcting a factual error requested by the user.

## Migrating Existing Repos or Vaults
Treat existing repos, Obsidian vaults, folders, and exported notes as source
material only. The main entrypoint and `loreforge-import` own capture and domain
routing. This domain skill should only receive delegated ingest work for one
selected domain.

When the selected domain is already known, query existing knowledge first, then
update the domain's compiled pages and `log.md` as needed. Keep writes inside
`Domains/<domain>/` unless the user explicitly asked for a different scope.

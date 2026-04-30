---
name: loreforge-wiki
description: Use for LoreForge domain wiki query, source ingest, durable updates, review, and Health Checks. One expert owns one domain.
user-invocable: true
version: 0.1.2
metadata:
  origin: "Inspired by NousResearch Hermes LLM Wiki, MIT"
---

# LoreForge LLM Wiki

Build and maintain a persistent, compounding Markdown wiki for one expert-owned
domain.

LoreForge follows the [LLM Wiki](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/llm-wiki/SKILL.md)
pattern: compile durable knowledge once, keep it linked, and update it as
sources and questions arrive. It adds expert-owned domains and Atlas MOCs for
preserving evolving conceptual views.

Always:

- act as the domain expert
- query existing knowledge first
- update pages directly after orientation
- keep `index.md` and `log.md` current

## When This Skill Activates

Use this skill when the user or another agent asks to:

- query a LoreForge wiki or domain
- ingest a source, URL, paper, doc, repo, local file, or pasted material
- update, revise, or maintain durable domain knowledge
- create a domain wiki
- review, audit, or run a Health Check on a domain wiki
- save reusable synthesis into a domain wiki

**DO NOT** use this skill for:

- agent-local memory
- user preferences
- temporary task state
- full chat transcripts
- one-off debugging details

Those belong in the agent runtime or memory system, not in the shared wiki.

## Wiki Location

Resolve the active wiki and domain before reading or writing.

**Wiki root discovery order:**

1. Use the wiki/domain path named by the user.
2. Otherwise use `WIKI_PATH`.
3. Otherwise use `WIKI_NAME` to look up `~/.config/loreforge/registry.toml`.
4. Otherwise use the registry's `default` wiki.
5. Otherwise fall back to `~/wiki`; before writing there, tell the user.

**Domain discovery order:**

1. Use the domain named by the user.
2. Otherwise use `DOMAIN_NAME`.
3. Otherwise use the selected wiki's `default_domain` from the registry.
4. Otherwise, if multiple domains exist, ask which domain to use before writing.

```bash
WIKI_NAME="${WIKI_NAME:-}"
WIKI="${WIKI_PATH:-$HOME/wiki}"
DOMAIN_NAME="${DOMAIN_NAME:-<domain>}"
DOMAIN="$WIKI/Domains/$DOMAIN_NAME"
```

`~/.config/loreforge/registry.toml` is machine-local discovery config. It is not
a knowledge store and should not contain notes, findings, summaries, or agent
memory.

```toml
default = "main"

[[wikis]]
name = "main"
path = "/path/to/loreforge-wiki"
description = "Personal LoreForge wiki"
sync = "local"
default_domain = "ai-research"
remote = ""

[[sources]]
name = "old-obsidian"
kind = "obsidian-vault"
path = "/path/to/source-vault"
default_target_wiki = "main"
default_target_domain = "ai-research"
```

`[[wikis]]` entries are writable LoreForge wiki roots. `[[sources]]` entries are
read-only source aliases for repeated imports from existing repos, vaults, or
folders.

The wiki is just a directory of Markdown files — open it in Obsidian, VS Code,
or any editor. No database, no special tooling required.

If Obsidian config/profile directories exist (`.obsidian*`, such as
`.obsidian-desktop` or `.obsidian-mobile`), treat them as editor state. Do not
query, ingest, migrate, index, run Health Checks on, or write their contents.

## Architecture: Multi-Layer Wiki

```text
wiki/
  00_System/       # Wiki-level entrypoints, shared protocols, views, and domain registry
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
  Sources/         # Mutable source-grounded Markdown notes
  Spaces/          # Durable people, orgs, projects, tools, systems, contexts
  Extras/          # Non-Markdown attachments such as PDFs and images
```

Treat `00_System/` as the wiki-level operating surface. Treat each
`Domains/<domain>/` as a self-contained LLM Wiki for a single expert-owned
domain.

Orient, query, ingest, update, review, and Health Check inside the selected
domain. DO NOT write across domains unless the user explicitly asks.

## Resuming an Existing Domain (CRITICAL — do this every session)

When the user specified a domain, **always orient yourself before doing anything**:

1. Read `SCHEMA.md`.
2. Read `index.md`.
3. Read the latest 20-30 entries from `log.md`.
4. Search existing pages for the topic.
5. Read relevant `Atlas/`, `Cards/`, `Sources/`, and `Spaces/` pages.

Only after orientation should you ingest, query, or lint. This prevents:

- Creating duplicate pages for entities that already exist
- Missing cross-references to existing content
- Contradicting the schema's conventions
- Repeating work already logged

For large domains(100+ pages), also run a quick search for the topic at hand before creating anything new.

## Initializing a New Wiki or Domain

When the user asks to create or start a wiki or domain:

1. Resolve the wiki root and domain name using the discovery order above.
2. Create the wiki root if needed.
3. Create `00_System/`, `00_System/index.md`, and `00_System/domains.md` if
   missing.
4. Create `Domains/<domain>/`.
5. Create the required domain files and directories above.
6. Ask for a concise domain description and the default language for extracted
   Cards, Atlas pages, and Spaces.
7. Write `SCHEMA.md` customized to the domain (see template below).
8. Write `index.md` with sectioned header.
9. Write initial `log.md` with creation entry.
10. Add or update the domain row in `00_System/domains.md`.
11. If the user is setting up a durable local wiki and the registry has no
    matching `[[wikis]]` entry, offer to add one.
12. Report the wiki path, domain path, and next useful actions.

### 00_System Minimal Files

Use `00_System/` for wiki-level orientation only. Domain behavior still lives in
each domain's `SCHEMA.md`.

`00_System/index.md`:

```markdown
# Wiki Index

- Domains: [[domains]]
```

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
- Source notes preserve the source language by default.
- Extracted Cards, Atlas pages, and Spaces use this domain's configured default note language: `[language]`.
- If this policy is missing, ask once before creating synthesized pages, then add it to `SCHEMA.md`.
- Do not translate source material unless the user asks for translation or bilingual notes.

## Conventions
- File names: lowercase, hyphens, no spaces (e.g., `transformer-architecture.md`)
- Every wiki page starts with YAML frontmatter (see below)
- Use `[[wikilinks]]` to link between pages (minimum 2 outbound links per page)
- When updating a page, always bump the `updated` date
- Every new page must be added to `index.md` under the correct section
- Every action must be inserted into `log.md` as the newest entry
- **Provenance markers:** On pages that synthesize 3+ sources, append `^[Sources/articles/source-file.md]`
  at the end of paragraphs whose claims come from a specific source. This lets a reader trace each
  claim back without re-reading the whole source file. Optional on single-source pages where the
  `sources:` frontmatter is enough.

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
sources: []
contested: false
contradictions: []
---
```
confidence and contested are optional but recommended for opinion-heavy or fast-moving topics. Lint surfaces contested: true and confidence: low pages for review so weak claims don't silently harden into accepted wiki fact.

## Tag Taxonomy
[Define 10-20 top-level tags for the domain. Add new tags here BEFORE using them.]

Example for AI/ML:
- Models: model, architecture, benchmark, training
- People/Orgs: person, company, lab, open-source
- Techniques: optimization, fine-tuning, inference, alignment, data
- Meta: comparison, timeline, controversy, prediction

Rule: every tag on a page must appear in this taxonomy. If a new tag is needed,
add it here first, then use it. This prevents tag sprawl.

## Page Thresholds
- **Create a page** when an entity/concept appears in 2+ sources OR is central to one source
- **Add to existing page** when a source mentions something already covered
- **DON'T create a page** for passing mentions, minor details, or things outside the domain
- **Split a page** when it exceeds ~200 lines — break into sub-topics with cross-links
- **Archive a page** when its content is fully superseded — move to `_archive/`, remove from index
- For MOCs, use view quality rather than source count. Create one ONLY when a
reusable thinking view exists.

## Atlas/MOC Pages
MOCs is NOT just a collection of cards or a  mirror of `index.md`, it is a place for mental
squeeze point.When multiple concepts are collected and lots of relations between them, it may be a time
for creating a MOC. A MOC includes:
- Tags: [map] for MOCs.
- Overview: what problem/claim the MOC is trying to discuss
- Key related concepts and relations/comparison
- Key idea/comments about these concepts
- Remaining issues/questions

## Cards
Use `Cards/` for durable synthesized knowledge:
- concepts
- methods
- patterns
- tradeoffs
- comparisons
- reusable decision frameworks

### Concept Pages
One page per concept or topic. Include:
- Definition / explanation
- Current state of knowledge
- Open questions or debates
- Related concepts ([[wikilinks]])

### Comparison Pages
Side-by-side analyses. Include:
- What is being compared and why
- Dimensions of comparison (table format preferred)
- Verdict or synthesis
- Sources

## Extras
Use `Extras/` for non-Markdown artifacts:
- PDFs
- images
- diagrams
- HTML snapshots
- local file attachments
- reusable templates or other non-note assets

DO NOT index `Extras/` directly. Link attachments from relevant Sources, Cards,
or Atlas pages.

## Sources
Use `Sources/` for mutable source-grounded Markdown notes.
Create or update a Source note when the source has durable domain value:
- paper
- article
- docs
- talk
- repo
- dataset
- book
- local file
- user-provided material

Include key claims, evidence, provenance, limitations, relevance, and links to
Cards, Atlas views, or Spaces.

### Source Capture Policy

- Preserve the source before synthesizing cards.
- Text articles, blogs, docs, and pasted text: save source-language Markdown in
  `Sources/articles/` or the right `Sources/` directory. Preserve title,
  author/publisher, dates, canonical URL, headings, links, and local image refs.
  Prefer complete transcription when the material is user-provided, local,
  permissively licensed, public domain, or otherwise appropriate to reuse in
  full. For third-party web pages where full transcription is not appropriate,
  keep a faithful structured source note with specific excerpts and grounded
  notes; do not add generic boilerplate explaining that the note is not a full
  transcription unless a concrete capture limitation matters.
- Article images/diagrams: download to `Extras/<source-slug>/`, link them from
  the Source note, and create a manifest for multiple images.
- PDFs: download the original PDF to `Extras/<source-slug>/`; create a
  `Sources/papers/` or `Sources/docs/` summary note with metadata, key claims,
  limitations, and a local PDF link. Extract full text only when needed or asked.
- Language: Source notes stay in the source language. Synthesized Cards, Atlas
  pages, and Spaces use the domain default note language from `SCHEMA.md`.
- Durable local paths in Source notes must point to wiki-local files, such as
  the Source note itself and files under `Extras/`. Do not put transient
  extractor paths such as `/tmp/topic-research/...` in Source note metadata; if
  those paths are useful for debugging, record them in `log.md` only.

### Built-In Capture Tools

- For web topics, direct links, Zhihu, WeChat, and pages that need browser state,
  use the bundled `topic-research` skill before writing Source notes.
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

Treat existing repos, Obsidian vaults, folders, and exported notes as **sources**
by default. Do not register them as writable LoreForge wiki roots unless the
user explicitly asks to convert them in place.

When migrating:

1. Resolve the source:
   - use the path named by the user, or
   - use a `[[sources]]` alias from `~/.config/loreforge/registry.toml`.
2. Resolve the target wiki and domain using the normal discovery order.
3. If the target domain does not exist, initialize it first.
4. Read from the source without changing it.
5. Ingest durable material into the native domain structure:
   - source-grounded notes into `Sources/`
   - synthesized reusable concepts into `Cards/`
   - emergent thinking views into `Atlas/`
   - people, entities, tools, projects, systems, and contexts into `Spaces/`
   - non-Markdown attachments into `Extras/`
6. Insert a newest-first migration entry in target `log.md`, including source
   alias or source description, import scope, and files created or updated.

Do not preserve an alternate long-term layout inside the LoreForge wiki. If the
user asks to adopt an existing repo in place, state that this changes that repo's
structure and get explicit confirmation before writing.

## Core Operations

### 1. Ingest

When the user provides a source (URL, file, paste), integrate it into the wiki:

1. **Capture the source:**
   - Determine source type and language first.
   - Text URL/article/blog/docs → extract source-language Markdown, preserve
     structure/links/metadata, save to `Sources/articles/` or the right
     `Sources/` directory. Prefer complete transcription when the material can
     appropriately be stored in full; otherwise keep a faithful structured note
     and record only concrete capture limitations.
   - Article images/diagrams → download to `Extras/<source-slug>/`, manifest
     multiple files, and link local images from the Source note.
   - PDF → download the original PDF to `Extras/<source-slug>/`; create a
     `Sources/papers/` or `Sources/docs/` summary note with metadata, key claims,
     limitations, and a local PDF link. Extract full text only when needed.
   - Pasted text → save in the original language; prefer complete transcription.
   - Source note metadata → use wiki-local durable paths only. Do not cite
     temporary extractor output directories as source artifacts inside the note.
   - Name the file descriptively: `Sources/articles/karpathy-llm-wiki-2026.md`

2. **Discuss takeaways** with the user — what's interesting, what matters for
   the domain. (Skip this in automated/cron contexts — proceed directly.)

3. **Check what already exists** — search index.md and `search`
   existing pages for mentioned entities/concepts. This is the difference between
   a growing wiki and a pile of duplicates.

4. **Write or update wiki pages:**
   - **New entities/concepts:** Create pages only if they meet the Page Thresholds
     in SCHEMA.md (2+ source mentions, or central to one source)
   - **Existing pages:** Add new information, update facts, bump `updated` date.
     When new info contradicts existing content, follow the Update Policy.
   - **Language:** Source notes stay in the source language. New Cards, Atlas
     pages, and Spaces use the domain's configured default note language from
     `SCHEMA.md`.
   - **Cross-reference:** Every new or updated page must link to at least 2 other
     pages via `[[wikilinks]]`. Check that existing pages link back.
   - **Tags:** Only use tags from the taxonomy in `SCHEMA.md`
   - **Provenance:** On pages synthesizing 3+ sources, append `^[Sources/articles/source.md]`
     markers to paragraphs whose claims trace to a specific source.
   - **Confidence:** For opinion-heavy, fast-moving, or single-source claims, set
     `confidence: medium` or `low` in frontmatter. Don't mark `high` unless the
     claim is well-supported across multiple sources.

5. **Update navigation:**
   - Add new pages to `index.md` under the correct section, alphabetically
   - Update the "Total pages" count and "Last updated" date in index header
   - Insert at the top of `log.md`: `## [YYYY-MM-DD] ingest | Source Title`
   - List every Source, Card, Atlas, Space, image, PDF, manifest, and other file
     created or updated in the log entry

6. **Report what changed** — list every file created or updated to the user,
   including local image/PDF attachment paths.

### 2. Query

When the user asks a question about the wiki's domain:

1. **Read `index.md`** to identify relevant pages.
2. **For wikis with 100+ pages**, also search across all `.md` files
   for key terms — the index alone may miss relevant content.
3. **Read the relevant pages**.
4. **Synthesize an answer** from the compiled knowledge. Cite the wiki pages
   you drew from: "Based on [[page-a]] and [[page-b]]..."
5. **File valuable answers back** — if the answer is a substantial comparison,
   deep dive, or novel synthesis, create a new page in `Cards/` or `Atlas/`.
   Don't file trivial lookups — only answers that would be painful to re-derive.
6. **Update `log.md`** with a newest-first entry for the query and whether it
   was filed.

### 3. Lint

When asked to lint, audit, or run a health-check:

1. **Orphan pages:** Find pages with no inbound `[[wikilinks]]` from other pages.
  ```python
  # Use available scripting tools for this — programmatic scan across all wiki pages
  import os, re
  from collections import defaultdict
  pages = "<WIKI_PATH>/Domains/<domain>"
  # Scan all .md files in Cards/,
  # Extract all [[wikilinks]] — build inbound link map
  # Pages with zero inbound links are orphans
  ```

2. **Broken wikilinks:** Find `[[links]]` that point to pages that don't exist.
3. **Domain boundary:** Surface wikilinks or path-shaped links that point outside
   the selected domain unless the user explicitly asked for cross-domain work.
4. **Index completeness:** Every active page under `Atlas/`, `Cards/`, and
   `Sources/` should appear in `index.md`. Active `Spaces/` pages should appear
   only when tagged `person`, `entity`, `tool`, or `project`. Do not require
   `Spaces/_archive/` or transient workspace notes in the index.
5. **Frontmatter validation:** Every wiki page must have all required fields
   (title, created, updated, type, tags, status, sources). Tags must be in the taxonomy.
6. **Stale content:** Pages whose `updated` date is >90 days older than the most
   recent source that mentions the same entities.
7. **Contradictions:** Pages on the same topic with conflicting claims. Look for
   pages that share tags/entities but state different facts. Surface all pages
   with `contested: true` or `contradictions:` frontmatter for user review.
8. **Quality signals:** List pages with `confidence: low` and any page that cites
   only a single source but has no confidence field set — these are candidates
   for either finding corroboration or demoting to `confidence: medium`.
9. **Page size:** Flag pages over 200 lines — candidates for splitting.
10. **Tag audit:** List all tags in use, flag any not in the `SCHEMA.md` taxonomy.
11. **Log rotation:** If `log.md` exceeds 500 entries, rotate it.
12. **Report findings** with specific file paths and suggested actions, grouped by
   severity (broken links > orphans > source drift > contested pages > stale content > style issues).
13. **Insert into log.md:** `## [YYYY-MM-DD] lint | N issues found`

## Working with the Wiki

### Bulk Ingest

When ingesting multiple sources at once, batch the updates:
1. Read all sources first
2. Identify all entities and concepts across all sources
3. Check existing pages for all of them (one search pass, not N)
4. Create/update pages in one pass (avoids redundant updates)
5. Update index.md once at the end
6. Write a single log entry covering the batch

### Archiving

When content is fully superseded or the domain scope changes:
1. Create `Spaces/_archive/` if it doesn't exist.
2. Move the page to `Spaces/_archive/<original-dir>/<page>.md`.
3. Set `status: archived` in frontmatter.
4. Remove it from `index.md`.
5. Update any active pages that linked to it — replace the wikilink with plain text + "(archived)" or link to a replacement page.
6. Log the archive action.

## Pitfalls

- **Always orient first** — read SCHEMA + index + recent log before any operation in a new session.
  Skipping this causes duplicates and missed cross-references.
- **Always update index.md and log.md** — skipping this makes the wiki degrade. These are the
  navigational backbone.
- **Don't drop source attachments** — article images, diagrams, PDFs, and other durable source
  artifacts belong in `Extras/<source-slug>/` and should be linked from the Source note.
- **Don't silently translate sources** — Source notes preserve the original language. Use the
  domain default note language only for synthesized Cards, Atlas pages, and Spaces.
- **Don't create pages for passing mentions** — follow the Page Thresholds in SCHEMA.md. A name
  appearing once in a footnote doesn't warrant an entity page.
- **Don't create pages without cross-references** — isolated pages are invisible. Every page must
  link to at least 2 other pages.
- **Frontmatter is required** — it enables search, filtering, and staleness detection.
- **Tags must come from the taxonomy** — freeform tags decay into noise. Add new tags to SCHEMA.md
  first, then use them.
- **Keep pages scannable** — a wiki page should be readable in 30 seconds. Split pages over
  200 lines. Move detailed analysis to dedicated deep-dive pages.
- **Ask before mass-updating** — if an ingest would touch 10+ existing pages, confirm
  the scope with the user first.
- **Rotate the log** — when log.md exceeds 500 entries, rename it `log-YYYY.md` and start fresh.
  The agent should check log size during lint.
- **Handle contradictions explicitly** — don't silently overwrite. Note both claims with dates,
  mark in frontmatter, flag for user review.

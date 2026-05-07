---
name: loreforge-wiki
description: Use for LoreForge domain query, capture, ingest, durable updates, review, and Health Checks. One expert owns one domain.
user-invocable: true
version: 0.1.7
metadata:
  origin: "Inspired by NousResearch Hermes LLM Wiki, MIT"
---

# LoreForge LLM Wiki

Build and maintain a persistent, compounding Markdown wiki for one expert-owned
domain.

LoreForge follows the [LLM Wiki](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/llm-wiki/SKILL.md)
pattern: capture the raw clip once, normalize it during ingest, keep durable
knowledge linked, and update it as questions arrive. It adds expert-owned
domains and Atlas MOCs for preserving evolving conceptual views.

When source-layer details matter, read [references/raw-first-wiki.md](references/raw-first-wiki.md).

Always:

- act as the domain expert
- query existing knowledge first
- update pages directly after orientation
- keep `index.md` and `log.md` current
- write equations and derivations with Obsidian-compatible LaTeX: inline math
  as `$...$`, standalone equations as `$$...$$`, never as plain-text
  pseudo-notation

## When This Skill Activates

Use this skill when the user or another agent asks to:

- query a LoreForge wiki or domain
- capture a raw source package or clip
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

Treat the local wiki directory as an existing working copy when it is available.
For LoreForge-style setups, `~/wiki` is the default local repo directory unless
the user or `WIKI_PATH` says otherwise.

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

`~/.config/loreforge/registry.toml` is the machine-local discovery and sync
config. It is not a knowledge store and should not contain notes, findings,
summaries, or agent memory. Keep sync/backend choices there so different
machines can use different sync modes for the same wiki.

```toml
default = "main"

[[wikis]]
name = "main"
path = "/path/to/loreforge-wiki"
description = "Personal LoreForge wiki"
sync = "local" # local | webdav | git
default_domain = "ai-research"
remote = ""
sync_bootstrapped = false

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

## Sync Workflow

Before creating or updating durable wiki files, resolve the wiki sync backend
from the machine-local registry. Use explicit user instructions first, then the
selected registry `[[wikis]]` entry. If no backend is configured, ask the user
to choose one:

- `webdav`: ask the user to configure `rclone config`, provide the
  `remote:path` target, and confirm whether first-machine bootstrap has already
  been completed.
- `git`: ask for the remote repo URL, ensure the wiki path is a git working
  copy with that remote, and confirm that commits should be pushed after edits.
- `local`: allow local-only mode only after warning that the wiki is not linked
  to remote sync and local machine loss can lose data.

For WebDAV-backed wikis, use `scripts/sync_webdav.sh` as the canonical helper
for the actual `rclone bisync` invocation. It supports normal steady-state sync
and the first-machine bootstrap/resync case where the local wiki should win.

For new wikis, confirm the backend during initialization before the first
durable write. For existing wikis without sync config, offer to add sync
behavior in the machine-local registry before making the requested update.
Record the chosen backend in the machine-local registry so the next agent on
that machine can recover the intended behavior.

After every wiki modification:

- For WebDAV-backed wikis, run `scripts/sync_webdav.sh` against the local wiki
  checkout and configured `remote:path`. Use the helper's bootstrap/resync mode
  when the local copy should be treated as the source of truth for first sync.
- For git-backed wikis, run `git add`, commit the wiki changes with a concise
  message, and push to the configured remote.
- For local-only wikis, report that no remote sync ran and repeat the data-loss
  warning.

Keep local edits in the wiki directory and sync after changes using the
configured backend.

- If the repo does not document the sync command yet, look for the wiki's sync
  notes before inventing a new one.

The wiki is just a directory of Markdown files — open it in Obsidian, VS Code,
or any editor. No database, no special tooling required.

If Obsidian config/profile directories exist (`.obsidian*`, such as
`.obsidian-desktop` or `.obsidian-mobile`), treat them as editor state. Do not
query, ingest, migrate, index, run Health Checks on, or write their contents.

## Architecture: Multi-Layer Wiki

```text
wiki/
  00_System/       # Wiki-level entrypoints, shared protocols, views, and domain registry
  Calendar/        # Date-based notes such as daily notes
    dailynotes/    # Default daily-note folder
  Shared/          # Raw source clips and reusable templates
    Raw/           # Raw clip files first, then normalized origin.md/manifest.md packages
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
structure. If an old wiki still has one, migrate raw capture material to
`Shared/Raw/`. Capture writes the raw clip only. Ingest later derives a
source-id and normalizes that clip into `Shared/Raw/<source-id>/origin.md` and
`manifest.md`. Domain `Sources/` is
optional and should be used only when a domain needs a compact excerpt or
source-specific lens over a large raw package.

Create `Domains/<domain>/Extras/` only when a domain truly needs local
non-source attachments.

Orient, query, capture, ingest, update, review, and Health Check inside the
selected domain. DO NOT write across domains unless the user explicitly asks.
During capture, copy the source clip into `Shared/Raw/` as a flat file and do
not create Cards, Atlas pages, Spaces, source-id directories, `origin.md`, or
`manifest.md`. During ingest, normalize the clip into `origin.md` and
`manifest.md` under `Shared/Raw/<source-id>/`, then compile reusable knowledge
from them. Only write `Calendar/` or
`Shared/Templates/` when the user explicitly asks for daily-note, diary,
calendar, or reusable template work.

## Resuming an Existing Domain (CRITICAL — do this every session)

When the user specified a domain, **always orient yourself before doing anything**:

1. Read `SCHEMA.md`.
2. Read `index.md`.
3. Read the latest 20-30 entries from `log.md`.
4. Search existing pages for the topic.
5. Read relevant `Atlas/`, `Cards/`, `Sources/`, and `Spaces/` pages; read
   `Shared/Raw/<source-id>/manifest.md` when provenance matters, and read
   `origin.md` or the raw clip file directly only when the compiled layers are
   insufficient or ingest has not normalized the clip yet.

Only after orientation should you ingest, query, update, or lint. Capture-only
can write flat raw clip files under `Shared/Raw/` after resolving the wiki
root; do not compile or update domain pages until after orientation. This
prevents:

- Creating duplicate pages for entities that already exist
- Missing cross-references to existing content
- Contradicting the schema's conventions
- Repeating work already logged

For large domains(100+ pages), also run a quick search for the topic at hand before creating anything new.

## Initializing a New Wiki or Domain

When the user asks to create or start a wiki or domain:

1. Resolve the wiki root and domain name using the discovery order above.
2. Confirm the sync backend from the machine-local registry:
   `webdav`, `git`, or explicit local-only.
3. For `webdav`, confirm the `rclone` remote target and whether bootstrap sync
   is already complete. For `git`, confirm the remote repo URL. For `local`,
   warn about data-loss risk before continuing.
4. Create the wiki root if needed.
5. Create `00_System/`, `00_System/index.md`, `00_System/domains.md`, and
   `00_System/wiki-layout.md` if missing.
6. Create or update the machine-local registry entry with the selected backend.
7. Create `Calendar/` and `Calendar/dailynotes/` if missing.
8. Create `Shared/Raw/` and `Shared/Templates/` if missing.
9. Create `Domains/<domain>/`.
10. Create the required domain files and directories above.
11. Ask for a concise domain description and the default language for extracted
   Cards, Atlas pages, and Spaces.
12. Write `SCHEMA.md` customized to the domain (see template below).
13. Write `index.md` with sectioned header and `wiki-layout.md` with the
    canonical shared/domain layout summary.
14. Write initial `log.md` with creation entry.
15. Add or update the domain row in `00_System/domains.md`.
16. If the machine-local registry has no matching `[[wikis]]` entry, offer to
   add one.
17. Run the configured post-write sync flow, or repeat the local-only warning.
18. Report the wiki path, domain path, sync backend, and next useful actions.

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

- `Shared/Raw/` for capture-only flat source clips
- `Shared/Raw/<source-id>/` for normalized raw packages and attachments after ingest
- `Shared/Templates/` for reusable templates

Domain layer:

- `Domains/<domain>/Atlas/` for durable maps and conceptual views
- `Domains/<domain>/Cards/` for durable concepts and comparisons
- `Domains/<domain>/Sources/` for optional source excerpts or source-specific lenses
- `Domains/<domain>/Spaces/` for durable people, tools, projects, and contexts

Capture writes raw source clips into `Shared/Raw/` and stops there. Ingest
normalizes flat clips into `Shared/Raw/<source-id>/`. Durable synthesis lives
in `Atlas/`, `Cards/`, and `Spaces/`. Optional domain source excerpts live in
`Sources/`. Compiled pages cite raw manifests or domain source notes with body
footnotes.
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
- Use `[[wikilinks]]` to link between pages (minimum 2 outbound links per page)
- When updating a page, always bump the `updated` date
- Every new page must be added to `index.md` under the correct section
- Every action must be inserted into `log.md` as the newest entry
- Put related page links near the top of Cards and Atlas pages as an Obsidian
  inline field, for example `related:: [[concept-a]], [[concept-b]]`, rather
  than burying them in a trailing related-pages section.
- Write equations and derivations with LaTeX math: use `$...$` for inline
  expressions and `$$...$$` for standalone equations.
- **Provenance markers:** Use body footnotes, not YAML, for compiled-page
  provenance. Append `[^1]` at the end of paragraphs whose claims come from a
  specific source, and put definitions at the end of the page using wikilinks
  such as `[^1]: [[Sources/source-note-name]]` or
  `[^1]: [[Shared/Raw/<source-id>/manifest.md]]`. Single-source pages should
  still use a footnote for source-backed claims.

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
- Footnote provenance for source-backed claims

## Extras
Create domain `Extras/` only for non-source attachments owned by this domain:
- diagrams
- reusable templates or other non-note assets

Put source PDFs, images, HTML snapshots, origin captures, and manifest files
under `Shared/Raw/<source-id>/`, not under domain `Extras/`.

If `Extras/` exists, do not index it directly. Link domain attachments from
relevant Cards or Atlas pages.

## Source Capture

Raw capture clips live as flat files under `Shared/Raw/` until ingest
normalizes them into packages under `Shared/Raw/<source-id>/`. Domain pages do
not keep YAML `sources:` links. Optional domain `Sources/` pages are compact
excerpt notes or source-specific lenses over large raw packages. Compiled
`Cards/`, `Atlas/`, `Spaces/`, and `Sources/` pages cite raw manifests or
domain source notes with body footnotes, not YAML.

### Source Capture Policy

- Preserve the shared raw source before synthesizing cards.
- Capture writes the raw clip only. It does not create Cards, Atlas pages,
  Spaces, source-id directories, `origin.md`, or `manifest.md`.
- Ingest normalizes the clip into `Shared/Raw/<source-id>/origin.md` and
  `Shared/Raw/<source-id>/manifest.md`.
- The manifest should record title, canonical URL or source description,
  retrieval date, source type, source language, `content_hash`, `origin`,
  `candidate_domains`, `compiled_pages`, status, and local artifact pointers.
- Keep `origin.md` in the source language and preserve structure, links, and
  image refs where possible. Prefer complete transcription when the material is
  user-provided, local, permissively licensed, public domain, or otherwise
  appropriate to reuse in full. For third-party web pages where full
  transcription is not appropriate, keep a faithful structured capture with
  specific excerpts and grounded notes; do not add generic boilerplate unless a
  concrete capture limitation matters.
- Article images/diagrams, PDFs, and other attachments belong in the raw
  package directory with clear local references from `origin.md` and the
  manifest once ingest has normalized the clip.
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
5. Capture source material into `Shared/Raw/` as raw clip files. A source-id
   directory is not required at capture time.
6. Ingest durable material into the native domain structure:
   - derive a stable source-id from the clip filename or source metadata
   - normalize the clip into `Shared/Raw/<source-id>/origin.md` and `manifest.md`
   - optional source excerpts into `Domains/<domain>/Sources/<source-id>.md`
     when the raw package is large or a stable local lens is useful
   - synthesized reusable concepts into `Cards/`
   - emergent thinking views into `Atlas/`
   - people, entities, tools, projects, systems, and contexts into `Spaces/`
7. Insert a newest-first migration entry in target `log.md`, including source
   alias or source description, import scope, and files created or updated.

Do not preserve an alternate long-term layout inside the LoreForge wiki. If the
user asks to adopt an existing repo in place, state that this changes that repo's
structure and get explicit confirmation before writing.

## Core Operations

### 0. Capture

When the user asks to clip, save, or preserve a source before compiling it:

1. Determine source type and language first.
2. Copy the source clip into `Shared/Raw/` as-is. Do not require a source-id
   subdirectory.
3. Do not create Cards, Atlas pages, Spaces, `origin.md`, `manifest.md`, or
   domain `index.md` / `log.md` entries during capture alone.
4. Report the capture path and any concrete limitations to the user.

### 1. Ingest

When the user asks to compile a source or raw package into the wiki:

1. **Frame the ingest as an inquiry loop:**
   - Identify the user-facing question, uncertainty, or problem the source helps
     answer before splitting it into records and pages.
   - If the problem is unclear, ask a short clarifying question before broad
     expansion.
   - Track the loop explicitly: problem framing → evidence capture → synthesis →
     validation against existing pages → unresolved questions or next sources.
   - Avoid turning ingest into mechanical source decomposition. The goal is to
     reduce future cognitive load by making the useful problem, answer, and
     feedback path easy to see.

2. **Use the raw clip first:**
   - If `Shared/Raw/` contains a flat clip file, derive a stable source-id from
     the filename or source metadata, create `Shared/Raw/<source-id>/`, preserve
     the clip under the normalized package, and write `origin.md` plus
     `manifest.md` before compiling.
   - If `Shared/Raw/<source-id>/` already exists, reuse it.
   - If it contains only a raw clip, normalize that clip into `origin.md` and
     `manifest.md` before compiling.
   - Keep the normalized raw package shape stable: raw clip(s) plus
     `origin.md`, `manifest.md`, optional `assets/` or `original/`
     attachments, and wiki-local artifact paths only.
   - Update the manifest hash when the normalized package changes so downstream
     pages know whether recompilation is needed.

3. **Discuss takeaways** with the user — what's interesting, what matters for
   the domain. (Skip this in automated/cron contexts — proceed directly.)

4. **Check what already exists** — search `index.md` and existing pages for
   mentioned entities/concepts before creating anything new.

5. **Write or update wiki pages:**
   - **New entities/concepts:** Create pages only if they meet the Page Thresholds
     in SCHEMA.md (2+ source mentions, or central to one source).
   - **Existing pages:** Add new information, update facts, bump `updated` date.
     When new info contradicts existing content, follow the Update Policy.
   - **Language:** Raw packages and optional domain Source notes stay in the
     source language. New Cards, Atlas pages, and Spaces use the domain's
     configured default note language from `SCHEMA.md`.
   - **Related links:** Put important related pages near the top of Cards and
     Atlas pages with `related:: [[...]]` so readers see the local graph before
     the body.
   - **Cross-reference:** Every new or updated page must link to at least 2 other
     pages via `[[wikilinks]]`. Check that existing pages link back.
   - **Tags:** Only use tags from the taxonomy in `SCHEMA.md`.
   - **Provenance:** Use body footnotes, not YAML. Append `[^1]` markers to
     source-backed claims and define them with optional source-note or raw
     manifest wikilinks such as `[^1]: [[Sources/source-note-name]]` or
     `[^1]: [[Shared/Raw/<source-id>/manifest.md]]`.
   - **Confidence:** For opinion-heavy, fast-moving, or single-source claims, set
     `confidence: medium` or `low` in frontmatter. Don't mark `high` unless the
     claim is well-supported across multiple sources.

6. **Update navigation:**
   - Add new pages to `index.md` under the correct section, alphabetically.
   - Update the "Total pages" count and "Last updated" date in index header.
   - Insert at the top of `log.md`: `## [YYYY-MM-DD] ingest | Source Title`.
   - List every raw package, optional domain Source note, Card, Atlas, Space,
     and other file created or updated in the log entry.

7. **Report what changed** — list every file created or updated to the user,
   including local image/PDF attachment paths.

### 2. Query

When the user asks a question about the wiki's domain:

1. **Read `index.md` and `log.md` first** to identify relevant compiled pages.
2. **Start with compiled knowledge** — `Atlas/`, `Cards/`, `Spaces/`, and
   `Sources/` before dropping into raw packages.
3. **Use raw packages only when needed** — read `Shared/Raw/<source-id>/manifest.md`
   for provenance, hash checks, or source pointers, and read `origin.md` or the
   raw clip file directly only when the compiled pages are insufficient or the
   user explicitly wants the raw material.
4. **For wikis with 100+ pages**, also search across all `.md` files for key
   terms — the index alone may miss relevant content.
5. **Synthesize an answer** from the least-detailed layer that answers the
   question. Cite the wiki pages you drew from: "Based on [[page-a]] and
   [[page-b]]..."
6. **File valuable answers back** — if the answer is a substantial comparison,
   deep dive, or novel synthesis, create a new page in `Cards/` or `Atlas/`.
   Don't file trivial lookups — only answers that would be painful to re-derive.
7. **Update `log.md`** with a newest-first entry for the query and whether it
   was filed.

### 3. Lint

When asked to lint, audit, or run a health-check:

1. **Raw capture integrity:** Validate normalized `Shared/Raw/<source-id>/`
   packages first. Flat capture-only files and raw clip-only folders are
   allowed and skipped until ingest.
   Check that `manifest.md` and `origin.md` either both exist or both do not,
   `content_hash` matches the normalized raw clip, and all wiki-local artifact
   and `compiled_pages` pointers are valid. For native domains, prefer the
   skill-local validator:
   ```bash
   python3 skills/loreforge-wiki/scripts/validate_native_domain.py <domain-path>
   python3 skills/loreforge-wiki/scripts/validate_native_domain.py --fix <domain-path>
   ```
   `--fix` may remove orphan footnote definitions. Missing definitions still
   require manual repair.
2. **Orphan pages:** Find pages with no inbound `[[wikilinks]]` from other pages.
  ```python
  # Use available scripting tools for this — programmatic scan across all wiki pages
  import os, re
  from collections import defaultdict
  pages = "<WIKI_PATH>/Domains/<domain>"
  # Scan all .md files in Cards/,
  # Extract all [[wikilinks]] — build inbound link map
  # Pages with zero inbound links are orphans
  ```
3. **Broken wikilinks:** Find `[[links]]` that point to pages that don't exist.
4. **Footnote/citation integrity:** Check every footnote marker has a matching
   definition and every footnote definition is referenced from the page body.
5. **Domain boundary:** Surface wikilinks or path-shaped links that point outside
   the selected domain unless the user explicitly asked for cross-domain work.
6. **Index completeness:** Every active page under `Atlas/`, `Cards/`, and
   `Sources/` should appear in `index.md`. Active `Spaces/` pages should appear
   only when tagged `person`, `entity`, `tool`, or `project`. Do not require
   `Spaces/_archive/` or transient workspace notes in the index.
7. **Frontmatter validation:** Every wiki page must have all required fields
   (title, created, updated, type, tags, status). Tags must be in the taxonomy.
8. **Stale content:** Pages whose `updated` date is >90 days older than the most
   recent source that mentions the same entities.
9. **Contradictions:** Pages on the same topic with conflicting claims. Look for
   pages that share tags/entities but state different facts. Surface all pages
   with `contested: true` or `contradictions:` frontmatter for user review.
10. **Quality signals:** List pages with `confidence: low` and any page that cites
   only a single source but has no confidence field set — these are candidates
   for either finding corroboration or demoting to `confidence: medium`.
11. **Page size:** Flag pages over 200 lines — candidates for splitting.
12. **Tag audit:** List all tags in use, flag any not in the `SCHEMA.md`
    taxonomy, and flag pages that have tag sprawl (more than 3 tags) so they
    can be simplified.
13. **Log rotation:** If `log.md` exceeds 500 entries, rotate it.
14. **Report findings** with specific file paths and suggested actions, grouped by
   severity (broken links > orphans > source drift > contested pages > stale content > style issues).
15. **Insert into log.md:** `## [YYYY-MM-DD] lint | N issues found`

## Working with the Wiki

### Bulk Ingest

When ingesting multiple sources at once, keep capture and ingest separated:
1. Capture can drop many raw clip files directly into `Shared/Raw/`.
2. Route or group captured clips by candidate domain.
3. Start domain ingest passes or subagents up to the caller's max concurrency
   when the runtime supports parallel work.
4. Each domain pass derives stable source IDs, normalizes assigned clips into
   `Shared/Raw/<source-id>/`, and updates hashes before compiling pages.
5. Identify all entities and concepts across the assigned clips.
6. Check existing pages for all of them in one search pass, not N passes.
7. Create/update pages in one pass to avoid redundant updates.
8. Update index.md once at the end.
9. Write a single log entry covering the batch.

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
- **Don't drop source attachments** — article images, diagrams, PDFs, and other
  durable source artifacts belong in `Shared/Raw/` during capture and in
  `Shared/Raw/<source-id>/` after ingest normalization. Link them from the raw
  package or optional domain Source note.
- **Don't duplicate raw sources** — search `Shared/Raw/` before adding a source.
  Reuse the shared raw package across domains, and add a domain Source note
  only when its excerpt/lens is actually useful.
- **Don't confuse capture with ingest** — capture only copies raw clip files.
  Ingest normalizes them into `origin.md` and `manifest.md`, then compiles
  reusable domain knowledge from that raw package.
- **Don't make ingest purely mechanical** — start from the user's problem or
  uncertainty, then use raw packages and Cards to lower future cognitive load.
- **Don't jump to full raw during query** — use `index.md`, `log.md`, Atlas,
  Cards, Spaces, and optional Source notes first. Open `origin.md` only when the
  compiled layers cannot answer or need verification.
- **Don't silently translate sources** — raw packages and optional domain
  Source notes preserve the original language. Use the domain default note
  language only for synthesized Cards, Atlas pages, and Spaces.
- **Don't create pages for passing mentions** — follow the Page Thresholds in SCHEMA.md. A name
  appearing once in a footnote doesn't warrant an entity page.
- **Don't create pages without cross-references** — isolated pages are invisible. Every page must
  link to at least 2 other pages.
- **Frontmatter is required** — it enables search, filtering, and staleness detection.
- **Tags must come from the taxonomy** — freeform tags decay into noise. Keep
  tag counts small and coarse. Add new tags to SCHEMA.md first, then use them.
- **Keep pages scannable** — a wiki page should be readable in 30 seconds. Split pages over
  200 lines. Move detailed analysis to dedicated deep-dive pages.
- **Ask before mass-updating** — if an ingest would touch 10+ existing pages, confirm
  the scope with the user first.
- **Rotate the log** — when log.md exceeds 500 entries, rename it `log-YYYY.md` and start fresh.
  The agent should check log size during lint.
- **Handle contradictions explicitly** — don't silently overwrite. Note both claims with dates,
  mark in frontmatter, flag for user review.

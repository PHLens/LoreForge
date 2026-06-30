# Schema

LoreForge wiki instances use one shared wiki root with root-level Cards,
Sources, Spaces, and Atlas areas.

## Wiki Shape

```text
wiki/
  00_System/
    index.md
    wiki-layout.md
    domains.md
    card-policy.md
    card-domains.md
    agent-policy.md
    card-index.json  # optional generated cache
  Atlas/
  Calendar/
    dailynotes/
    weeklynotes/
  Cards/
    <domain>/
      <card>.md
  Sources/
    Raw/
      <source-id>/
        origin.md
        manifest.md
        original/
        extracted/
        assets/
    Papers/
      <citekey>.md
    Clippings/
  Spaces/
  Extras/
    Templates/
    Img/
    Excalidraw/
  z-Legacy/
```

`00_System/` is the wiki-level operating surface. It contains layout policy,
domain registry, Card policy, Card-domain taxonomy, agent write policy, and
optional generated caches. `Cards/<domain>/` is the agent-maintained reusable
Card layer. Root `Atlas/` is a human-facing view/MOC layer. Root `Sources/`
stores raw packages, paper notes, clippings, and optional source lenses. Root
`Spaces/` stores durable projects, people, tools, systems, organizations, work
items, proposals, research plans, and contexts. `Extras/` stores shared
templates and non-source assets.

Paper raw files are managed by Zotero outside the vault; Markdown paper notes
live under `Sources/Papers/<citekey>.md` and use `zotero://` PDF jump links.

## Root Files

| Path | Purpose |
|---|---|
| `00_System/wiki-layout.md` | Human/agent-readable directory contract |
| `00_System/domains.md` | Active Card-domain registry |
| `00_System/card-policy.md` | Card shape, page-type boundaries, and reusable note rules |
| `00_System/card-domains.md` | Domain boundaries, taxonomy, and out-of-scope rules |
| `00_System/agent-policy.md` | Pre-write gates, allowed write roots, validator expectations, transaction policy |
| `00_System/card-index.json` | Optional generated retrieval cache; not source of truth |

## Calendar Files

| Path | Purpose |
|---|---|
| `Calendar/dailynotes/` | Default folder for daily diary or daily-note pages |
| `Calendar/weeklynotes/` | Default folder for weekly planning and review pages |

## Source Files

| Path | Purpose |
|---|---|
| `Sources/Raw/` | Wiki-root raw source area. Capture writes `Sources/Raw/<source-id>/origin.md` and `manifest.md`; ingest may update the same package with candidate domains, compiled page pointers, original artifacts, extracted artifacts, and source-specific assets |
| `Sources/Papers/` | Zotero-backed paper notes. Zotero owns PDFs and paper metadata outside the vault |
| `Sources/Clippings/` | Optional human-facing clipping notes |

## Knowledge Files

| Path | Purpose |
|---|---|
| `Cards/<domain>/` | Durable concepts, methods, mechanisms, patterns, tradeoffs, comparisons, and decision frameworks |
| `Atlas/` | Maps of Content, relationship views, and human-facing problem views |
| `Spaces/` | Durable non-Card objects, contexts, projects, work items, and archive space |
| `Extras/Templates/` | Reusable note templates |
| `Extras/Img/` | Shared image assets |
| `Extras/Excalidraw/` | Shared Excalidraw assets |

Tags are stable classification labels, not keyword dumps. Prefer 1-3 tags per
page and treat tag sprawl as a lint smell rather than a richer description.

## Operating Rules

Agents should orient before writing:

1. Read `00_System/card-domains.md` and the selected domain entry.
2. Read `00_System/card-policy.md`.
3. Read `00_System/agent-policy.md`.
4. Search `Cards/<domain>/` and relevant root `Atlas/`, `Sources/`, and
   `Spaces/` pages.
5. Use `00_System/card-index.json` only as a cache; confirm important facts
   from Markdown pages.

Routine maintenance writes directly to the allowed root area after orientation.
There is no staged promotion pipeline in the active core workflow.
Capture-only writes may create or refresh raw packages under
`Sources/Raw/<source-id>/` after the wiki root is resolved; compiled updates
still require orientation first.

Query and ingest should stay question-driven: start from the problem being
answered, then make a page-type decision. Use strict Card authoring for durable
reusable concepts, strict Atlas/MOC authoring for relationship or problem
views, and conservative Source/Space paths when the reusable shape is weak.

Durable project work items belong in root `Spaces/`, commonly
`Spaces/projects/<project>/<work-item>.md` when no local project convention
exists. They should summarize problem background, solution, bug diagnosis,
verification, and status, not preserve chat transcripts or command-by-command
logs.

When several raw packages are present, a main entrypoint or caller may group
them by candidate domain and dispatch bounded parallel ingest jobs. The
selected leaf workflow owns its page write inside the allowed root boundary.
Centralized policy and validator output replace routine per-domain index/log
edits.

Paper notes under `Sources/Papers/` are not Cards and are not maintained
through per-domain index/log files. Zotero metadata and paper-note frontmatter
are their provenance surface, and the paper workflow writes only the paper-note
Markdown file unless the user explicitly requests downstream synthesis.

## Source Capture

Raw source packages preserve the source language by default. Capture derives a
stable `source-id`, writes `origin.md` for the source text/transcription, and
writes `manifest.md` with source metadata, `content_hash`, `compiled_pages`,
`candidate_domains`, capture notes, and links to original and extracted
artifacts when those artifacts are stored. For text articles, blogs, docs, and
pasted text, keep title, author/publisher, dates, canonical URL, headings,
links, and local image references. Prefer complete transcription when the
material is user-provided, local, permissively licensed, public domain, or
otherwise appropriate to reuse in full. Otherwise keep a faithful structured
capture and record only concrete limitations.

Web capture should be planned before extraction. Save the original artifact
when available, then build `origin.md` from deterministic page variables such
as article body, title, author, site, description, published date, canonical
URL, language, word count, meta tags, schema.org data, selections/highlights,
and site-specific selectors when the article extractor misses stable structure.
Use a minimal Web Clipper-like note shape in `origin.md`: frontmatter keeps
only note-facing index fields such as `title`, `source`, `author`,
`published`, `created`, and `tags`, while the Markdown body directly holds
cleaned `content`. Keep package lifecycle and provenance fields such as
`source_id`, `retrieved_at`, selector/schema decisions, fallback, limitations,
prompt-assistance choices, and compiled-page state in `manifest.md` as
manifest extraction lineage. Localize important figures or diagrams under the
raw package. The body should be filtered so metadata already promoted to
fields, such as title, authors, citation, source URL, description, and
publication date, is not duplicated in the body. If capture falls back from an
unavailable search source to public pages or alternate APIs, record the
unavailable source and substitute source in manifest extraction lineage.

For papers, use Zotero instead of `Sources/Raw/` or wiki-local PDF storage.
The original PDF is a read-only Zotero-managed raw artifact outside the vault,
and the agent-owned output is a Markdown paper note under
`Sources/Papers/<citekey>.md`. Agents must not create, rename, move, delete,
overwrite, copy, or reorganize paper PDFs or Zotero attachment directories.
The paper note should store the PDF jump as a Zotero URI such as
`[PDF](zotero://open-pdf/...)`.

Compiled pages do not carry YAML `sources:` links. Prefer source-backed
provenance as path-qualified internal wikilinks to wiki-local raw artifacts,
raw manifests, paper notes, or source notes, such as
`[[Sources/Raw/<source-id>/manifest|readable source alias]]` or
`[[Sources/Papers/<citekey>|paper alias]]`. Bare wikilinks are for active Cards
whose stems are unique in the validated domain. Use source footnotes only when
paragraph-level provenance would otherwise be ambiguous. Source metadata should
point to wiki-local files, not temporary extractor outputs such as
`/tmp/topic-research/...`.

## Write Policy And Rollback

`00_System/agent-policy.md` owns write restrictions:

- pre-write gate before file changes
- allowed write roots by page type
- post-write validator expectation
- risk levels for routine, medium, and high-risk operations
- transaction snapshots only for high-risk writes
- transaction retention and cleanup policy

Routine writes should not create per-edit logs. High-risk writes, broad
migrations, destructive cleanup, and multi-area rewrites may require a
transaction snapshot according to policy. Validator output and final handoff
are the default audit surfaces.

## Boundaries

- Do not store agent-local memory, preferences, task state, or chat transcripts
  in the wiki.
- Do not write across multiple Card domains unless the user explicitly asks.
- Do not duplicate the same raw source or PDF under multiple domains.
- Do not treat capture and ingest as the same action.
- Do not mechanically split every source into a Source note and new Cards.
  Start from the question and create durable synthesis only when it reduces
  future work.
- Do not force weak material into Cards or MOCs; use Source/Space records or
  ask a blocker question when the page type is unclear.
- If `Extras/` exists, do not index it directly.
- Do not index archive or transient workspace notes as active knowledge.
- Mark low-confidence and contested knowledge explicitly.

## Legacy Layout

Older LoreForge wikis may contain `Domains/<domain>/SCHEMA.md`, `index.md`,
`log.md`, domain-local `Atlas/`, `Cards/`, `Sources/`, `Spaces/`, `Shared/Raw/`,
or `Shared/Templates/`. Treat these as legacy inputs. The preferred migration
targets are root `Cards/<domain>/`, `Atlas/`, `Sources/`, `Spaces/`,
`Sources/Raw/`, and `Extras/Templates/`. Legacy paper notes are a special case:
move `Domains/research/Spaces/papers/<citekey>.md` to
`Sources/Papers/<citekey>.md`; paper notes are not generic Space records. Ask
before migrating 10+ pages or deleting legacy files.

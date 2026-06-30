# Skills

Core LoreForge operations and bundled helper skills live here.

LoreForge exposes one user entrypoint plus focused internal workflows. Agents
should start from `loreforge`; the entrypoint delegates to paper, plan,
capture, config, work-item, check, import, and domain workflows only when
needed.

| Skill | Purpose |
|---|---|
| `loreforge` | Default user entrypoint for config, capture, ingest, lint, init, import, query, plan, work-item records, and cross-domain coordination |
| `loreforge-config` | Resolve wiki location, registry, sync backend, and post-write sync |
| `loreforge-capture` | Preserve raw clips under `Sources/Raw/` without compiling domain pages |
| `loreforge-paper` | Update paper notes under `Sources/Papers/` while treating Zotero-managed PDFs as read-only raw artifacts outside the vault |
| `plan-docomposer` | Decompose personal or research goals into weekly and daily note plans under `Calendar/` |
| `loreforge-work-item` | Turn project, Jira, issue, MR/PR, bugfix, CI failure, and implementation context into durable root `Spaces/projects/` records |
| `loreforge-card` | Strict reusable Card authoring under `Cards/<domain>/` |
| `loreforge-moc` | Strict root Atlas/MOC view authoring under `Atlas/` |
| `loreforge-check` | Lint, audit, and structural checks for raw packages and native domains |
| `loreforge-import` | Treat existing repos, vaults, folders, and exports as source material |
| `loreforge-domain` | Domain initialization, generic domain orientation, Sources/Spaces updates, and legacy domain repair |

It also bundles reusable helper skills that a wiki agent can call during
capture or Obsidian-facing work:

| Skill | Purpose |
|---|---|
| `topic-research` | Browser-backed web research, URL extraction, Zhihu detail expansion, WeChat probing, and research packs |
| `convert-to-markdown` | Convert Word, Confluence MIME exports, HTML, and text files to Markdown, extracting images when supported |
| `defuddle` | Lightweight clean Markdown extraction for standard web pages via the Defuddle CLI |
| `obsidian-markdown` | Obsidian-flavored Markdown syntax: wikilinks, embeds, callouts, properties, and related references |
| `obsidian-cli` | Optional interaction with a running Obsidian app through the Obsidian CLI |
| `json-canvas` | Create and edit Obsidian JSON Canvas files |
| `obsidian-bases` | Create and edit Obsidian Bases files |

The `loreforge` skill owns intent classification, config/sync resolution,
source capture handoff, plan handoff, domain routing, write gates, and subagent
fan-out. `loreforge-paper` owns paper-specific page shape and related-work
linking before bounded domain handoff; it writes only Markdown note files under
`Sources/Papers/` and never modifies Zotero-managed PDFs or
attachment structure. `plan-docomposer` owns goal-to-weekly and
daily note decomposition in the wiki Calendar layer. `loreforge-work-item`
owns durable project record shape before bounded root `Spaces/` writes. The
domain skill follows the LLM Wiki pattern with root-layout policy: one expert
agent orients on `00_System/card-domains.md`, `00_System/card-policy.md`,
`00_System/agent-policy.md`, existing `Cards/<domain>/`, and relevant
Atlas/Sources/Spaces pages before writing. Raw clips are preserved separately,
and compiled pages use path-qualified wikilinks to raw artifacts/manifests,
paper notes, or source notes for source provenance; use source footnotes only
for ambiguous paragraph-level provenance, not YAML source links.

Web capture should borrow the Obsidian Web Clipper shape without making
Obsidian a dependency: preserve the original artifact when possible, extract
deterministic variables and selectors, render minimal Web Clipper-like note
frontmatter in `origin.md`, put cleaned content directly in the note body,
filter duplicated metadata out of that body, keep important assets wiki-local,
and record extractor/selector/fallback lineage in the raw manifest before any
ingest or domain synthesis.

## Core Workflow

Use `loreforge` as the default user-facing entry point.
Use `loreforge-config` when location or sync needs to be resolved.
Use `loreforge-capture` when a source should be preserved without synthesis.
Use `loreforge-paper` when the source is a paper or paper-like technical report.
Use `plan-docomposer` when a large goal or proposal should become weekly and
daily note plans.
Use `loreforge-work-item` when current project, Jira, issue, MR/PR, bugfix, CI
failure, or implementation context should become a durable project record.
Use `loreforge-check` when the user asks for linting, audit, validation, or checks.
Use `loreforge-import` when an existing repo, vault, folder, or export should
be treated as source material.
Use `loreforge-card` for reusable Card pages.
Use `loreforge-moc` for Atlas/MOC view pages.
Use `loreforge-domain` for domain initialization, Sources/Spaces updates, and
generic domain repair.

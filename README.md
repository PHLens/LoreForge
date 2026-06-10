# LoreForge

LoreForge is a framework for building LLM-wiki style professional knowledge bases.

It is inspired by [Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), but its scope is narrower and more practical:

- compile reusable professional knowledge from questions, sources, and queries
- make that knowledge readable by humans and agents
- reduce repeated raw search and re-summarization
- keep agent-local experience out of the shared wiki

## Core Boundary

```text
pamem
  agent-local memory
  preferences
  task state
  agent-local experience

LoreForge wiki instance
  professional knowledge
  concepts
  raw source packages
  maps and indexes

LoreForge framework repo
  plugin metadata
  schema
  skills
  config examples
```

LoreForge is not an agent memory store. It is a framework and plugin distribution used to create and operate separate wiki instances.

## Repository Form

This repository contains the framework:

```text
LoreForge/
├── .codex-plugin/plugin.json  # Codex plugin metadata
├── .claude-plugin/            # Claude plugin metadata
├── README.md
├── docs/                     # Philosophy, schema, install guidance
├── templates/config/          # Optional local registry example
└── skills/                   # LoreForge entrypoint, domain skill, and helper skills
```

Actual knowledge should live in a separate wiki repository or vault.

Agents should use an explicit wiki path when available, or `WIKI_PATH` plus a
domain name. If unset, the main entrypoint and `loreforge-config` fall back to
`~/wiki`.

## Wiki Instance Shape

The domain skill expects this shape:

```text
wiki/
  00_System/
    ...
  Calendar/
    dailynotes/
    weeklynotes/
  Shared/
    Raw/
      <source-id>/
        manifest.md
        origin.md
        original/
        extracted/
        assets/
    Templates/
  Domains/
    <domain>/
      SCHEMA.md
      index.md
      log.md
      Atlas/
      Cards/
      Sources/  # optional compiled source excerpts
      Spaces/
```

Each domain is a self-contained LLM Wiki owned by one expert agent. The agent
orients on `SCHEMA.md`, `index.md`, recent `log.md`, and relevant pages before
querying, ingesting, updating, reviewing, or running a Check.

`Extras/` is optional for a domain and only used when the domain truly needs
its own non-source attachments.

`Shared/Raw/<source-id>/` stores the canonical raw source package:
`origin.md` keeps the agent-readable source text, and `manifest.md` keeps
metadata, source hash, compiled page pointers, and links to original/extracted
artifacts when those artifacts are stored. `original/`, `extracted/`, and
`assets/` are optional package subdirectories, not mandatory storage quotas.
For web pages, capture follows a clipper-style plan: preserve an original
artifact when possible, extract deterministic page variables and selectors,
render a fixed Web Clipper-like capture card in `origin.md`, localize important
assets, and record extractor/selector lineage in `manifest.md`. Obsidian Web
Clipper exports or `obsidian-clipper` CLI/API output can be used as capture
input when available, but the durable wiki contract remains the LoreForge raw
package.
Paper capture should default to compact metadata-and-text preservation and
archive PDF binaries only when the user asks or exact/offline audit requires
the original. `Calendar/dailynotes/` and `Calendar/weeklynotes/` hold dated
personal planning notes when the wiki role is asked to decompose goals into
daily or weekly work. `Shared/Templates/` stores reusable wiki templates.
`Domains/<domain>/Sources/` is optional and can hold source excerpts or
source-specific lenses when the raw package is large. `Cards/`, `Atlas/`, and
`Spaces/` hold the durable synthesis and should prefer plain internal wikilinks
to wiki-local raw artifacts, raw manifests, or domain source notes; use
source footnotes only when paragraph-level provenance would otherwise be ambiguous.
Do not use YAML source links.

## Skills

LoreForge exposes one user-facing entrypoint plus focused internal workflows.
Agents should start from `loreforge`; the entrypoint opens paper, plan,
capture, config, work-item, check, import, and domain workflows only when they
are needed.

| Skill | Purpose |
|---|---|
| `loreforge` | Default main entrypoint for config, capture, ingest, lint, init, import, query, plan, work-item records, and cross-domain coordination |
| `loreforge-config` | Resolve wiki location, registry, sync backend, and post-write sync |
| `loreforge-capture` | Preserve raw source packages under `Shared/Raw/<source-id>/` without compiling domain pages |
| `loreforge-paper` | Route paper-specific capture/ingest for arXiv, DOI, PDF, preprints, conference papers, and paper-like technical reports |
| `plan-docomposer` | Decompose personal or research goals into weekly and daily note plans under `Calendar/` |
| `loreforge-work-item` | Turn project, Jira, issue, MR/PR, bugfix, CI failure, and implementation context into durable `Spaces/projects/` records |
| `loreforge-card` | Strict reusable Card authoring under `Domains/<domain>/Cards/` |
| `loreforge-moc` | Strict Atlas/MOC view authoring under `Domains/<domain>/Atlas/` |
| `loreforge-check` | Lint, audit, and structural checks for raw packages and native domains |
| `loreforge-import` | Treat existing repos, vaults, folders, and exports as source material |
| `loreforge-domain` | Domain initialization, generic domain orientation, Sources/Spaces updates, and legacy domain repair |
| `topic-research` | Browser-backed web research, URL extraction, Zhihu detail expansion, WeChat probing, and source research packs |
| `convert-to-markdown` | Convert local documents and exported pages to Markdown |
| `defuddle` | Extract clean Markdown from standard web pages with the Defuddle CLI |
| `obsidian-markdown` | Work with Obsidian-flavored Markdown syntax |
| `obsidian-cli` | Optional automation against a running Obsidian app |
| `json-canvas` | Create and edit JSON Canvas files |
| `obsidian-bases` | Create and edit Obsidian Bases files |

The main entrypoint owns domain selection, config, capture handoff, plan
handoff, and cross-domain coordination. `loreforge-paper` owns the
paper-specific ingest shape before bounded domain handoff. `plan-docomposer`
owns wiki-local goal decomposition into Calendar notes. `loreforge-work-item`
owns project record shape before bounded domain handoff. `loreforge-domain`
owns domain initialization and generic Sources/Spaces maintenance.
`loreforge-card` and `loreforge-moc` own Card/MOC authoring contracts and
acceptance gates. Helper skills produce capture input or Obsidian-specific
artifacts; they should not replace routing, domain orientation, index, log,
and check workflow.

The previous Obsidian `wiki` adapter layout is not bundled. Existing Obsidian
vaults can still be used as sources, and LoreForge wiki instances can still be
opened in Obsidian as plain Markdown vaults.

## Plugin Distribution

LoreForge can be installed as a Codex or Claude plugin.

The plugin layer is intentionally thin:

- expose the `loreforge` main entrypoint
- keep `loreforge-config`, `loreforge-capture`, `loreforge-check`,
  `loreforge-paper`, `plan-docomposer`, `loreforge-work-item`,
  `loreforge-card`, `loreforge-moc`, `loreforge-import`, and
  `loreforge-domain` available as internal workflows for the entrypoint
- provide boundary instructions for when to use LoreForge
- keep actual knowledge in separate wiki instances
- recover after context compaction from domain `SCHEMA.md`, `index.md`,
  `log.md`, and relevant pages

Plugin metadata lives in:

```text
.codex-plugin/plugin.json
.claude-plugin/plugin.json
.claude-plugin/marketplace.json
```

## Component Contract

External orchestrators can inspect LoreForge through a read-only component
surface documented in `docs/component-contract.md`:

```bash
loreforge status --json
loreforge validate --wiki /path/to/wiki --all-domains --json
loreforge init --wiki /path/to/wiki --domain ai-research --json
loreforge setup --wiki /path/to/wiki --domain ai-research --json
```

`status` and `validate` are read-only doctor checks. `init` is proposal-only and
does not write registry files, wiki notes, domains, sync state, or fixes.
`setup` is the component-facing bootstrap command for external tools: it writes
the machine-local registry entry plus the minimal wiki/domain skeleton and
returns a JSON report. It does not run capture, ingest, rclone sync, or git
sync.

## GitHub-Backed Wikis

LoreForge supports wiki instances backed by GitHub repositories.

The intended mode is local-first:

```text
GitHub remote -> local clone -> local query/search/edit -> git synchronization
```

Agents should use the local clone for search and editing. GitHub is for persistence and cross-machine synchronization, not per-query retrieval.

## Sync Backends

LoreForge wiki instances are local-first and can be configured for `rclone`,
`git`, or explicit `local` mode. New wiki initialization should confirm the
backend before the first durable write, and existing wikis can add sync behavior
by updating the machine-local registry entry for that machine.

For rclone-backed wikis, remote is authoritative by default: run
`skills/loreforge-domain/scripts/sync_rclone.sh --mode pull` before reading or
editing, then run the same helper with `--mode push` after agent-owned edits.
Use `--mode bootstrap` only when the local copy should intentionally seed the
remote on first sync or recovery. Git-backed wikis should commit and push, and
local-only wikis should report that no remote sync ran and warn about data-loss
risk. The rclone helper supports WebDAV, SFTP, and other rclone remotes through
one backend.

## Existing Repos And Vaults

Existing repos or vaults should be treated as sources. Use `loreforge-import`
and `loreforge-capture` to preserve raw material under `Shared/Raw/`, then
route selected material through the main `loreforge` page-type decision so
native `Domains/<domain>/` synthesis lands in `loreforge-card`,
`loreforge-moc`, or conservative Source/Space workflows instead of keeping
long-term alternate layouts or source mirrors.

## License

MIT

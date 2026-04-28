# LoreForge

LoreForge is a framework for building LLM-wiki style professional knowledge bases.

It is inspired by [Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), but its scope is narrower and more practical:

- compile reusable professional knowledge from sources and queries
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
  source notes
  maps and indexes

LoreForge framework repo
  plugin metadata
  templates
  schema
  task views
  skills
  adapters
```

LoreForge is not an agent memory store. It is a framework and plugin distribution used to create and operate separate wiki instances.

## Repository Form

This repository contains the framework:

```text
LoreForge/
├── .codex-plugin/plugin.json  # Codex plugin metadata
├── .claude-plugin/            # Claude plugin metadata
├── .claude/CLAUDE.md          # Claude always-on LoreForge router
├── AGENTS.md                 # Rules for agents editing this framework repo
├── README.md
├── docs/                     # Philosophy, schema, install guidance
├── templates/config/          # Local registry templates
├── templates/wiki/           # Generic LoreForge wiki instance template
├── skills/                   # Core LoreForge operations
└── adapters/
    └── obsidian-vault/       # Obsidian-specific template and conventions
```

Actual knowledge should live in a separate wiki repository or vault created from `templates/wiki/`.

Agents discover those wiki instances through a machine-local registry:

```text
~/.config/loreforge/registry.toml
```

Each wiki instance also carries self-description in:

```text
<wiki>/.loreforge/wiki.toml
```

See [docs/config.md](docs/config.md) for registration and discovery.

## Wiki Instance Shape

The generic wiki template uses:

```text
AGENTS.md
00_System/
  +Wiki Index.md
  Vault Map.md
  Schema.md
  Wiki Log.md
  Views/
    default.md
    query.md
    ingest.md
    writeback.md
    promote.md
    maintenance.md
10_Inbox/
  capture/
  ingest/
  writeback/
Cards/
Sources/
  Papers/
  Articles/
  Docs/
MOCs/
  Scope/
Archive/
```

The important idea is task-oriented views, not agent-specific views. Any session that loads the wiki rules can follow the same process.

## First Operations

Keep the initial workflow simple:

| Operation | Purpose |
|---|---|
| Query | Use the card index, Atlas/MOCs, and stable notes before broad search |
| Capture | Quick alias for `ingest mode=capture` |
| Ingest | Capture or process external source material into staged packages |
| Writeback | Stage reusable conversation/query synthesis as candidate notes |
| Promote | Batch-promote reviewed staged packages into stable notes, archive staging, update indexes, and log |
| Lint | Run read-only structural health checks |
| Register | Register local wiki paths and remotes |
| Sync | Keep local wiki clones aligned with Git remotes |

Automation should grow from repeated usage pain, not be designed up front.

These operations are framework core concepts, implemented under `skills/`. Adapter-specific path conventions should be documented under `adapters/`.

`capture` remains a convenient command, but its behavior is `ingest mode=capture`. Processed `ingest` and `writeback` outputs are staged packages with a `manifest.md`; `promote` is the stable-write transaction that can promote one or more candidate notes, update `00_System/+Wiki Index.md` for stable cards, optionally update MOCs, move consumed staging material to `Archive/`, and append the wiki log.

## Plugin Distribution

LoreForge can be installed as a Codex or Claude plugin.

The plugin layer is intentionally thin:

- expose the operation skills in `skills/`
- provide router instructions for when to use each skill
- keep actual knowledge in separate wiki instances
- recover after context compaction from registry, package manifests, indexes, and log files

Plugin metadata lives in:

```text
.codex-plugin/plugin.json
.claude-plugin/plugin.json
.claude-plugin/marketplace.json
.claude/CLAUDE.md
```

## GitHub-Backed Wikis

LoreForge supports wiki instances backed by GitHub repositories.

The intended mode is local-first:

```text
GitHub remote -> local clone -> local query/search/edit -> git sync
```

Agents should use the local clone for search and editing. GitHub is for persistence and cross-machine synchronization, not per-query retrieval.

## Relationship To Existing `~/wiki`

The current `~/wiki` structure already has useful ideas:

- `00_System/Vault Map.md`
- compact indexes
- agent/task views

LoreForge should generalize those ideas into a reusable framework. `~/wiki` can remain a concrete wiki instance or source of design feedback.

## Obsidian Adapter

The previous Obsidian-oriented draft now lives under:

```text
adapters/obsidian-vault/
```

Use it when the target wiki is an Obsidian vault that expects `MOCs/Scope/` conventions.

## License

MIT

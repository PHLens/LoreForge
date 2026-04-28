# LoreForge

LoreForge is a framework for binding LLM-assisted knowledge workflows to user-owned repositories.

It is inspired by [Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), but its scope is narrower and more practical:

- compile reusable professional knowledge from sources and queries
- make that knowledge readable by humans and agents
- reduce repeated raw search and re-summarization
- keep agent-local experience out of shared repositories
- keep durable knowledge separate from review staging and runtime state

## Core Boundary

```text
pamem
  agent-local memory
  preferences
  current task state
  agent-local experience

LoreForge runtime state
  generic staged ingest and writeback packages
  native source extracts and optional snapshots
  reports, caches, locks, and temporary files
  run metadata

User target repositories
  durable professional knowledge
  notes, docs, source notes, and examples
  optional native LoreForge structure and 10_Inbox review staging
  user-owned Git history and remotes

LoreForge framework repo
  plugin metadata
  setup helper scripts
  generic conventions and docs
  optional native starter template
  skills and tests
```

LoreForge core is a workflow layer over user-owned repositories. It is not an agent memory store, not the authoritative content repository, and not a requirement that every target repo follow a single native shape.

Stable professional knowledge belongs in the target repository selected by a binding. Generic staged packages and generated working files belong in LoreForge runtime state. Native staged packages belong in the target repo `10_Inbox/` so humans and other agents can review them before promotion. Agent-local experience, preferences, and task state belong in `pamem`.

## Repository Form

This repository contains the framework:

```text
LoreForge/
├── .codex-plugin/plugin.json  # Codex plugin metadata
├── .claude-plugin/            # Claude plugin metadata
├── .claude/CLAUDE.md          # Claude always-on LoreForge router
├── AGENTS.md                  # Rules for agents editing this framework repo
├── README.md
├── docs/                      # Philosophy, schema, install, and config guidance
├── scripts/                   # Deterministic helper scripts
├── templates/config/          # Local binding registry templates
├── templates/wiki/            # Optional native starter template
├── tests/                     # Focused shell regressions
└── skills/                    # LoreForge operation skills
```

Actual knowledge lives in user target repositories. A target repo can be an existing Markdown or documentation repo with its own layout, or it can opt into LoreForge's native profile for structured query and promotion.

Agents discover target repositories through the machine-local binding registry:

```text
~/.config/loreforge/registry.toml
```

A binding records the user-owned `target_repo`, LoreForge-managed `state_dir`, searchable `read_roots`, writeback or staging targets, and mode. See [docs/config.md](docs/config.md) for the registry format.

## Operations

| Operation | Layer | Purpose |
|---|---|---|
| Setup | Core | Bind an existing target repo or create an optional native starter, initialize runtime state, and update the registry |
| Ingest | Core | Read source material and stage a package without writing stable knowledge |
| Writeback | Core | Generic: apply approved staged outputs to configured targets. Native: stage conversation/query outputs in `10_Inbox/writeback/` |
| Search | Core | Run lightweight filesystem and Markdown search over configured read roots |
| Lint protocol | Core | Check registry resolution, runtime state, package manifests, targets, and writeback safety |
| Query | Native | Answer from native indexes, views, cards, sources, MOCs, and provenance conventions |
| Promote | Native | Move reviewed native staged material into stable native notes, indexes, logs, and archives |
| Lint native | Native | Check native structure, index health, provenance health, and promotion rules |
| Register | Support | Maintain registry entries directly when low-level edits are needed |
| Sync | Support | Pull, inspect, commit, or push a bound target repo through Git |

Core means setup, ingest, writeback, search, and protocol lint. These operations work for generic and native bindings, but their write backend depends on mode: generic uses `state_dir` package manifests, while native uses repo-local `10_Inbox/` packages for review.

Native means query, promote, and native lint. These operations require `mode = "native"` and a native retrieval contract. In native mode, stable writes to `Cards/`, `Sources/`, `MOCs/`, indexes, logs, and archive happen through `promote`.

`register` is intentionally lower level than `setup`: use `setup` for normal binding creation and adoption, and `register` only when directly maintaining the registry. `sync` operates on the target repo's Git state.

## Binding Modes

Generic bindings are the default adoption path for existing repositories. Generic setup creates or updates:

- the local registry entry
- the LoreForge runtime state directory
- configured read roots and writeback targets

Generic setup does not require target-local LoreForge metadata and does not reshape the target repository.

Native bindings are optional. A native target repo follows LoreForge's structured profile for higher-capability retrieval and promotion. The current starter template lives at:

```text
templates/wiki/
```

The template name is historical; it is now the native starter profile, not the default shape for every LoreForge binding.

## Native Starter Generation

Create a native starter only when the target should use the high-structure profile for query, promote, and native lint:

```bash
bash scripts/setup-binding.sh cs /path/to/cs-native \
  --mode native \
  --init-native-template \
  --target "writeback_staging=10_Inbox/writeback:Native staged writeback packages" \
  --target "ingest_staging=10_Inbox/ingest:Native staged ingest packages" \
  --default-target writeback_staging
```

Bind an existing repository without the native starter when the user's current layout should remain authoritative:

```bash
bash scripts/setup-binding.sh notes /path/to/notes \
  --target "notes=docs:General notes" \
  --target "sources=references:Source notes" \
  --default-target notes
```

See [docs/install.md](docs/install.md) for setup flows.

## GitHub-Backed Targets

LoreForge supports target repositories backed by GitHub or another Git remote.

The intended mode is local-first:

```text
Git remote -> local clone -> local search/read/write -> git sync
```

Agents should use the local clone for search and editing. GitHub is for persistence and cross-machine synchronization, not per-query retrieval.

## Relationship To Existing `~/wiki`

An existing `~/wiki` can be bound as either:

- a generic target, preserving its current layout and using search/writeback over configured paths
- a native target, if it already follows or intentionally adopts the native profile

LoreForge should generalize useful patterns from existing knowledge repos without making every repository adopt those paths.

## License

MIT

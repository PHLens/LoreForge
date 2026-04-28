# Philosophy

LoreForge is a framework for LLM-assisted professional knowledge workflows over user-owned repositories.

It is not agent memory, not a full agent runtime, and not a mandate that every repository adopt a native LoreForge layout.

The goal is to reduce repeated raw search and summarization by compiling useful source material into durable, queryable, human-readable knowledge where the user already keeps that knowledge.

## Separation

```text
pamem
  local agent/workspace memory
  preferences
  current task state
  agent-local experience

LoreForge runtime state
  staged packages
  source extracts and optional snapshots
  reports, caches, locks, and temporary files
  operation metadata

User target repositories
  durable professional knowledge
  notes, docs, source-grounded summaries, and examples
  optional native LoreForge profile
  Git history and remotes owned by the user

LoreForge framework repo
  plugin metadata
  setup helpers
  generic workflow conventions
  optional native starter template
  skills, tests, and documentation
```

LoreForge core is a workflow layer over user-owned repositories. It binds a target repo to runtime state, stages ingest and writeback work outside the target repo, and applies durable writes only through explicit validated operations.

Native repos are optional. They provide a higher-structure profile for `query`, `promote`, and `lint native` through indexes, views, cards, sources, MOCs, provenance conventions, and logs.

## First Principle

Shared knowledge should make both humans and agents smarter without forcing either to scan raw sources every time.

## What LoreForge Is Not

LoreForge should not compete with full lifelong-agent systems.

Do not expand LoreForge into:

- personal agent memory
- user preference storage
- autonomous agent runtime
- gateway or chat UI
- cron scheduler
- subagent orchestration platform
- automatic skill evolution system

Those belong in systems such as `pamem`, Hermes, OpenClaw, Slock, or the host agent runtime.

LoreForge should stay focused on workflow boundaries for shared professional knowledge: where durable content lives, where temporary workflow state lives, and how agents safely move from source material to reviewed repository updates.

## Relationship To Agent Memory

Agent growth and shared knowledge are different problems.

```text
Hermes / pamem
  agent grows
  agent remembers local experience
  agent learns procedures and preferences

LoreForge
  shared knowledge compounds in user repositories
  professional concepts become reusable
  source summaries become queryable
  staged work remains reviewable
```

The boundary is intentional:

| Content | Destination |
|---|---|
| User preference | `pamem` or host agent memory |
| Agent operating experience | `pamem` or host agent memory |
| Current task state | session, project files, or `pamem` |
| Runtime package, extract, report, cache, or lock | LoreForge runtime state |
| Reusable professional concept | user target repository |
| Source-grounded summary | user target repository |
| Cross-agent knowledge package awaiting review | LoreForge runtime state |
| Stable reviewed knowledge | user target repository |

## Difference From Other LLM-Wiki Systems

Many LLM-wiki implementations are all-in-one skills: read a schema, ingest sources, update pages, update indexes, append logs, and lint one repository shape.

That is useful for a single autonomous agent, but it has weak boundaries when humans and multiple agents share repositories with different layouts.

LoreForge's defensible difference is a binding-centric, reviewable, agent-agnostic knowledge workflow.

Key differences:

1. **Target repo plus runtime state**

   ```text
   target_repo + state_dir + configured targets
   ```

   Durable content and workflow artifacts are separated by default.

2. **Staged package before stable write**

   ```text
   ingest/writeback package -> validation -> writeback or native promote
   ```

   Agents do not directly turn every answer or source into stable repository content.

3. **Manifest as handoff protocol**

   A staged package records provenance, candidates, output plans, and write intent. One agent can stage, another can review, and a human can inspect the package.

4. **Human-readable first**

   Target repositories should remain useful to human readers, whether they are generic Markdown repos or native LoreForge repos.

5. **Agent-agnostic operation**

   LoreForge should be usable from Codex, Claude, Hermes, OpenClaw-connected agents, Slock-style collaborative agents, or plain Git/Markdown workflows.

6. **Native structure only where it earns its cost**

   Native indexes, views, MOCs, and promotion logs are valuable for structured retrieval, but generic bindings should not pay that schema cost.

7. **Shared knowledge, not private experience**

   Agent-local experience stays outside shared repositories. This prevents professional knowledge bases from becoming memory dumps.

## What To Learn From Hermes

Hermes is closer to a lifelong agent runtime than a shared knowledge workflow layer, but several ideas are worth adapting carefully.

Borrow:

- **Session orientation**: before operating on a binding, resolve the registry entry, target repo, runtime state, recent package manifests, and relevant target context.
- **Memory/knowledge split**: keep facts, preferences, procedures, runtime packages, and durable knowledge in separate stores.
- **Source immutability**: preserve source provenance and avoid rewriting source-grounded notes casually.
- **Session search as recovery**: use file-based manifests, reports, indexes, and logs so agents can recover work after compaction or session changes.
- **Profile isolation lesson**: do not let agent-local experience leak into shared professional knowledge.
- **Quality signals**: consider `confidence`, `contested`, `superseded_by`, or contradiction markers for mature notes.
- **Source drift detection**: later, record source URL, access date, and optional hash/version to detect changed external sources.
- **Log hygiene**: keep native logs useful as an evolution timeline, with rotation or archive if they grow too large.
- **Skill evolution discipline**: update skills from repeated real usage pain, not from speculative design.

Do not borrow:

- autonomous memory growth into target repositories
- agent profile state
- gateway/chat UI responsibilities
- runtime orchestration
- unrestricted self-modifying skills

LoreForge can be used by Hermes-hosted agents, but LoreForge should remain the shared knowledge workflow layer rather than becoming a Hermes replacement.

## Design Trade-Off

LoreForge is slower than a fully autonomous all-in-one knowledge skill.

That is acceptable. The extra friction buys:

- reviewability
- recoverability after context compaction
- cross-agent handoff
- clearer human inspection
- lower risk of repository pollution
- cleaner separation between shared knowledge, runtime state, and agent memory

For small personal experiments, a lighter workflow may be enough. LoreForge is for knowledge bases that should survive multiple agents, multiple sessions, varied repository layouts, and human review.

## Roadmap

### Phase 1: Binding Protocol Stability

- tighten staged package `manifest.toml`
- define required and optional package fields
- clarify source, output, target, status, and provenance vocabulary
- add examples for ingest and writeback packages
- make writeback validation deterministic enough for different agents to follow

### Phase 2: Native Profile

- keep the native starter as an optional high-structure profile
- define source note, card, MOC, and card index conventions for native repos
- clarify how `Cards/`, `Sources/`, `MOCs/`, and `Archive/` interact in native repos
- define naming rules and duplicate handling for native notes
- improve native task views for query, ingest, writeback, promotion, and maintenance

Next discussion focus:

- refine exact native `Sources/`, `Cards/`, `MOCs/`, and `+Wiki Index.md` responsibilities from real use
- define how staged package candidates map to stable native notes
- define minimum frontmatter and naming rules for native stable notes
- decide how source provenance should be represented without making notes noisy

### Phase 3: Quality Gates

- expand protocol lint for package manifests, target mismatches, path traversal, writeback conflicts, and state directory health
- expand native lint for package manifests, broken provenance, stale index entries, duplicate cards, and orphaned stable notes
- add promotion checklist rules for native repos
- add examples of acceptable and unacceptable writeback
- consider confidence, contested, superseded, and contradiction markers for mature notes
- consider source drift checks using access dates, source versions, or hashes
- define native log rotation or archival strategy

### Phase 4: Tooling

- add small scripts only where deterministic behavior matters
- generate package skeletons for ingest and writeback
- validate manifest files
- summarize writeback and promotion plans
- avoid large automation until repeated usage proves the need

### Phase 5: Integration

- maintain Codex and Claude plugin metadata
- document binding setup for existing repositories
- document native starter bootstrap conventions
- document how Hermes/OpenClaw/Slock-hosted agents can use LoreForge as a shared knowledge workflow layer
- support Git-backed target repos through local-first sync

### Phase 6: Real-World Evaluation

- run LoreForge against real personal and professional repositories
- measure whether query cost and repeated summarization decrease
- collect failure cases where agents stage low-value knowledge
- compare generic binding usage against native profile usage
- refine package, index, and promotion rules from actual use

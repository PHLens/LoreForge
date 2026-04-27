# Philosophy

LoreForge is a framework for LLM-wiki style professional knowledge bases.

It is not agent memory and not a full agent runtime.

The goal is to reduce repeated raw search and summarization by compiling useful source material into durable, queryable, human-readable knowledge.

## Separation

```text
pamem
  local agent/workspace memory
  preferences
  current task state
  agent-local experience

LoreForge wiki instance
  professional knowledge
  source-grounded notes
  concepts
  maps and indexes

LoreForge framework repo
  plugin metadata
  templates
  schema
  task views
  skills
  adapters
```

## First Principle

The wiki should make both humans and agents smarter without forcing either to scan raw sources every time.

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

LoreForge should stay focused on shared professional knowledge that humans and multiple agents can read, query, review, and maintain.

## Relationship To Agent Memory

Agent growth and shared knowledge are different problems.

```text
Hermes / pamem
  agent grows
  agent remembers local experience
  agent learns procedures and preferences

LoreForge
  shared knowledge compounds
  professional concepts become reusable
  source summaries become queryable
  stable notes remain human-readable
```

The boundary is intentional:

| Content | Destination |
|---|---|
| User preference | `pamem` or host agent memory |
| Agent operating experience | `pamem` or host agent memory |
| Current task state | session, project files, or `pamem` |
| Reusable professional concept | LoreForge wiki |
| Source-grounded summary | LoreForge wiki |
| Cross-agent knowledge package | LoreForge staged package |
| Stable reviewed knowledge | LoreForge stable notes |

## Difference From Other LLM-Wikis

Many LLM-wiki implementations are all-in-one agent skills: read schema, ingest sources, update pages, update index, append log, and lint.

That is useful for a single autonomous agent, but it has weak boundaries when humans and multiple agents share the same knowledge base.

LoreForge's defensible difference is not "another llm-wiki." It is a reviewable, agent-agnostic knowledge protocol.

Key differences:

1. **Staged package before stable write**

   ```text
   ingest/writeback -> manifest package -> promote -> stable notes + index + log
   ```

   Agents do not directly turn every answer or source into stable wiki content.

2. **Manifest as handoff protocol**

   A staged package records source type, domain, provenance, candidate notes, proposed updates, and promotion reason. One agent can stage, another can review or promote, and a human can inspect the package.

3. **Human-readable first**

   The wiki is not just prompt fuel. Cards, source notes, MOCs, indexes, and logs should be useful to a human reader.

4. **Agent-agnostic operation**

   LoreForge should be usable from Codex, Claude, Hermes, OpenClaw-connected agents, Slock-style collaborative agents, or plain Git/Obsidian workflows.

5. **Stable index discipline**

   Indexes only point at stable knowledge. Captures and staged packages stay out of discovery indexes until promotion.

6. **Shared knowledge, not private experience**

   Agent-local experience stays outside the shared wiki. This prevents the professional knowledge base from becoming a memory dump.

## What To Learn From Hermes

Hermes is closer to a lifelong agent runtime than a shared knowledge substrate, but several ideas are worth adapting carefully.

Borrow:

- **Session orientation**: before operating on a wiki, read schema, maps, compact indexes, and recent meaningful log entries.
- **Memory/skill split**: keep facts, preferences, procedures, and durable knowledge in separate stores.
- **Source immutability**: preserve source provenance and avoid rewriting source-grounded notes casually.
- **Session search as recovery**: use file-based staged package manifests and logs so agents can recover work after compaction or session changes.
- **Profile isolation lesson**: do not let agent-local experience leak into shared professional knowledge.
- **Quality signals**: consider `confidence`, `contested`, `superseded_by`, or contradiction markers for mature notes.
- **Source drift detection**: later, record source URL, access date, and optional hash/version to detect changed external sources.
- **Log hygiene**: keep log useful as an evolution timeline, with rotation/archive if it grows too large.
- **Skill evolution discipline**: update skills from repeated real usage pain, not from speculative design.

Do not borrow:

- autonomous memory growth into the shared wiki
- agent profile state
- gateway/chat UI responsibilities
- runtime orchestration
- unrestricted self-modifying skills

LoreForge can be used by Hermes-hosted agents, but LoreForge should remain the shared knowledge layer rather than becoming a Hermes replacement.

## Design Trade-Off

LoreForge is slower than a fully autonomous all-in-one wiki skill.

That is acceptable. The extra friction buys:

- reviewability
- recoverability after context compaction
- cross-agent handoff
- clearer human inspection
- lower risk of index/log pollution
- cleaner separation between shared knowledge and agent memory

For small personal experiments, a lighter llm-wiki may be enough. LoreForge is for knowledge bases that should survive multiple agents, multiple sessions, and human review.

## Roadmap

### Phase 1: Protocol Stability

- tighten staged package `manifest.md`
- define required and optional manifest fields
- clarify `source_type`, `kind`, `status`, and provenance vocabulary
- add examples for ingest and writeback packages
- make `promote` behavior deterministic enough for different agents to follow

### Phase 2: Wiki Structure

- finalize domain-first directory structure
- define source note, concept card, MOC, and index conventions
- clarify when content belongs in `20_Domains` vs `30_Shared`
- define naming rules and duplicate handling
- improve task views for query, ingest, writeback, promotion, and maintenance

Next discussion focus:

- decide whether domain-first should remain the default structure
- define exact `Sources/`, `Cards/`, `MOCs/`, and `+Wiki Index.md` responsibilities
- define how staged package candidates map to stable notes
- define minimum frontmatter and naming rules for stable notes
- decide how source provenance should be represented without making notes noisy

### Phase 3: Quality Gates

- expand lint checks for package manifests, broken provenance, stale index entries, duplicate cards, and orphaned stable notes
- add promotion checklist rules
- add examples of acceptable and unacceptable writeback
- consider confidence, contested, superseded, and contradiction markers for mature notes
- consider source drift checks using access dates, source versions, or hashes
- define log rotation or archival strategy

### Phase 4: Tooling

- add small scripts only where deterministic behavior matters
- generate package skeletons for ingest and writeback
- validate manifest files
- summarize promotion plans
- avoid large automation until repeated usage proves the need

### Phase 5: Adapters And Integration

- maintain Codex and Claude plugin metadata
- improve Obsidian adapter conventions
- document how Hermes/OpenClaw/Slock-hosted agents can use LoreForge as a shared knowledge substrate
- support GitHub-backed wiki repos through local-first sync

### Phase 6: Real-World Evaluation

- run LoreForge against a real personal/professional wiki
- measure whether query cost and repeated summarization decrease
- collect failure cases where agents stage low-value knowledge
- compare usage against Hermes-style all-in-one llm-wiki workflows
- refine package, index, and promotion rules from actual use

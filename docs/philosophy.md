# Philosophy

LoreForge is a framework for LLM-wiki style professional knowledge bases.

It is not agent memory and not a full agent runtime. The goal is to reduce
repeated raw search and summarization by capturing useful source material once
as raw packages and compiling durable, queryable, human-readable knowledge.
Ingest should start from the user's question or uncertainty, not from mechanical
source decomposition.

## Separation

```text
pamem
  local agent/workspace memory
  preferences
  current task state
  agent-local experience

LoreForge wiki instance
  professional knowledge
  raw source packages
  optional domain source notes
  durable concepts
  maps, indexes, logs

LoreForge framework repo
  plugin metadata
  schema
  skills
  config examples
```

## First Principle

The wiki should make both humans and agents smarter without forcing either to
scan raw sources every time.

## What LoreForge Is Not

LoreForge should not compete with full lifelong-agent systems.

Do not expand LoreForge into:

- personal agent memory
- user preference storage
- autonomous agent runtime
- gateway or chat UI
- cron scheduler
- general-purpose subagent orchestration platform
- automatic skill evolution system

Those belong in systems such as `pamem`, Hermes, OpenClaw, Slock, or the host
agent runtime.

LoreForge should stay focused on shared professional knowledge that humans and
agents can read, query, review, and maintain.

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
  shared raw sources avoid duplicate capture
  optional domain source notes keep large sources queryable
  stable notes remain human-readable
```

| Content | Destination |
|---|---|
| User preference | `pamem` or host agent memory |
| Agent operating experience | `pamem` or host agent memory |
| Current task state | session, project files, or `pamem` |
| Reusable professional concept | LoreForge wiki |
| Raw source package | LoreForge wiki `Shared/Raw/<source-id>/origin.md` + `manifest.md` |
| Raw source artifact | LoreForge wiki `Shared/Raw/<source-id>/` |
| Reusable template | LoreForge wiki `Shared/Templates/` |
| Optional domain source note | LoreForge domain `Sources/` note |
| Durable domain view | LoreForge wiki |

## Current Design

LoreForge now follows a small core:

1. One shared wiki root can contain many domains.
2. The `loreforge` main entrypoint handles domain selection, config, capture
   handoff, batch grouping, and bounded fan-out to domain experts.
3. Shared raw sources live as packages in `Shared/Raw/<source-id>/`; capture
   creates `origin.md` plus `manifest.md`, and ingest updates the same package
   while compiling domain knowledge. Reusable templates live in
   `Shared/Templates/`, including separate starters for Cards, MOCs, and
   focused relationship views.
4. Optional domain source notes live in `Domains/<domain>/Sources/` when a raw
   package is large or needs a stable excerpt.
5. One expert agent owns and maintains one domain.
6. The main `loreforge` entrypoint makes page-type decisions before compiled
   writes.
7. `loreforge-card` and `loreforge-moc` own strict Card/MOC authoring
   contracts and acceptance gates. `loreforge-domain` handles domain
   initialization, generic orientation, Sources/Spaces updates, and repair.
8. Human supervision happens through `log.md`, `index.md`, confidence metadata,
   contradiction records, checks, and git diffs.

The old staged package pipeline is not part of the active core workflow.
Focused helper workflows may exist for config, capture, paper-specific ingest,
work-item records, Card/MOC authoring, checks, and import, but they should stay
behind the main entrypoint instead of becoming user surface area.

## What To Learn From LLM Wiki Systems

Borrow:

- **Session orientation**: before operating on a wiki, read schema, indexes, and
  recent meaningful log entries.
- **Question-driven capture and ingest**: frame source capture around the
  problem being solved, then decide whether the raw package, an optional domain
  Source note, or durable synthesis is actually needed.
- **Memory/knowledge split**: keep facts, preferences, procedures, and durable
  professional knowledge in separate stores.
- **Source discipline**: preserve provenance and avoid turning passing mentions
  into pages.
- **Quality signals**: use `confidence`, `contested`, and contradiction markers
  for weak or conflicting knowledge.
- **Log hygiene**: keep logs useful as an evolution timeline.
- **Skill evolution discipline**: update skills from repeated real usage pain,
  not speculative design.

Do not borrow:

- autonomous memory growth into the shared wiki
- agent profile state
- gateway/chat UI responsibilities
- general-purpose runtime orchestration
- unrestricted self-modifying skills

## Roadmap

1. Stabilize the single-domain expert workflow.
2. Keep initialization authority in `loreforge-domain`, not copied wiki templates.
3. Add focused check fixtures.
4. Keep main entrypoint behavior bounded to domain selection, config, capture handoff,
   batch grouping, and delegated expert work.

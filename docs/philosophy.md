# Philosophy

LoreForge is a framework for LLM-wiki style professional knowledge bases.

It is not agent memory and not a full agent runtime. The goal is to reduce
repeated raw search and summarization by capturing useful source material once,
normalizing it during ingest, and compiling durable, queryable, human-readable
knowledge. Capture should preserve the raw clip once; ingest should start from
the user's question or uncertainty, not from mechanical source decomposition.

## Separation

```text
pamem
  local agent/workspace memory
  preferences
  current task state
  agent-local experience

LoreForge wiki instance
  professional knowledge
  raw capture clips
  normalized raw packages
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
| Raw capture clip | LoreForge wiki `Shared/Raw/` as a flat file |
| Normalized raw package | LoreForge wiki `Shared/Raw/<source-id>/origin.md` + `manifest.md` |
| Raw source artifact | LoreForge wiki `Shared/Raw/<source-id>/` after ingest normalization |
| Reusable template | LoreForge wiki `Shared/Templates/` |
| Optional domain source note | LoreForge domain `Sources/` note |
| Durable domain view | LoreForge wiki |

## Current Design

LoreForge now follows a small core:

1. One shared wiki root can contain many domains.
2. Shared raw capture clips live as flat files in `Shared/Raw/`; ingest
   normalizes selected clips into `Shared/Raw/<source-id>/` packages. Reusable
   templates live in `Shared/Templates/`.
3. Optional domain source notes live in `Domains/<domain>/Sources/` when a raw
   package is large or needs a stable excerpt.
4. One expert agent owns and maintains one domain.
5. The optional `loreforge-router` skill handles domain selection, batch
   grouping, and bounded fan-out to domain experts. It is bypassed for clear
   single-domain work, and it does not capture raw content, transform sources,
   normalize packages, or write domain pages itself.
6. The core `loreforge-wiki` skill handles domain query, ingest, update,
   review, initialization, and Health Checks.
7. Expert agents write directly after orientation.
8. Human supervision happens through `log.md`, `index.md`, confidence metadata,
   contradiction records, Health Checks, and git diffs.

The old staged package pipeline is not part of the active core workflow.
Migration, domain-management, and sync helpers should be added only when
repeated use proves they are needed.

## What To Learn From LLM Wiki Systems

Borrow:

- **Session orientation**: before operating on a wiki, read schema, indexes, and
  recent meaningful log entries.
- **Question-driven capture and ingest**: frame source capture around the
  problem being solved, then decide whether a raw clip, an optional domain
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
2. Keep initialization authority in `loreforge-wiki`, not copied wiki templates.
3. Add focused Health Check fixtures.
4. Add migration support as raw source ingestion into native domains.
5. Keep router behavior bounded to domain selection, batch grouping, and
   delegated expert work; capture and ingest semantics remain in
   `loreforge-wiki`.

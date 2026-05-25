---
name: loreforge
description: Default LoreForge entrypoint for capture, ingest, query, lint, init, config, import, plan, work-item records, Card/MOC authoring, and cross-domain coordination. Resolves intent, config, domains, write gates, and subagent fan-out before delegating to focused leaf workflows.
user-invocable: true
version: 0.2.0
---

# LoreForge

Use this skill as the default user-facing entry point for LoreForge. The user
should be able to paste a link, file path, source, goal, or command such as
capture, ingest, lint, init, config, import, query, update, plan, or work-item
without choosing a lower level skill.

Use `loreforge` as the default user-facing entry point. Other LoreForge skills
are internal workflows; do not ask the user to choose them.

This skill owns:

- intent classification
- wiki/config/sync resolution
- source capture handoff
- domain selection and routing
- Calendar daily/weekly planning handoff
- write gates for multi-domain or destructive work
- subagent fan-out when the host supports it
- final synthesis and user-facing summary

It delegates durable work to focused workflows:

| Workflow | Use For |
|---|---|
| `loreforge-config` | wiki discovery, registry edits, init config, sync backend, post-write sync |
| `loreforge-capture` | URL/file/paste/doc/research pack -> raw package under `Shared/Raw/<source-id>/` |
| `loreforge-paper` | paper-specific capture/ingest flow for arXiv, DOI, PDF, preprint, conference paper, or paper-like technical report |
| `plan-docomposer` | decompose personal or research goals into weekly and daily note plans under `Calendar/` |
| `loreforge-work-item` | project, Jira, issue, MR/PR, bugfix, CI failure, and implementation records under domain `Spaces/projects/` |
| `loreforge-card` | strict reusable Card authoring under `Domains/<domain>/Cards/` |
| `loreforge-moc` | strict Atlas/MOC view authoring under `Domains/<domain>/Atlas/` |
| `loreforge-domain` | domain initialization, generic domain orientation, Sources/Spaces updates, and legacy domain repair |
| `loreforge-check` | lint, audit, structural checks, raw package integrity, validator execution |
| `loreforge-import` | existing repo/vault/folder/export -> source capture and native domain ingest |

Do not ask the user which LoreForge skill to invoke. Choose the workflow and
keep the user-facing command simple.

## Always

- resolve the active wiki before writing
- inspect available domains before choosing write targets
- keep each domain expert inside one `Domains/<domain>/` boundary
- treat raw source packages as shared wiki-root `Shared/Raw/` data
- gate writes that affect multiple domains, initialize new domains, or convert
  existing repos in place
- report domains consulted, domains written, changed files, conflicts, and
  confidence

## Do Not

- write domain pages directly as the entrypoint
- update raw packages, build manifests, or create Cards/Atlas/Spaces directly
- merge cross-domain answers without domain attribution
- update multiple domains unless the user requested it or approved the plan
- ingest editor state such as `.obsidian*`
- expose internal workflow complexity to the user

## Classify The Request

Map user intent to one operation:

- `config`: configure registry, sync backend, or wiki location
- `init`: create a wiki or domain
- `capture`: preserve source material only
- `ingest`: capture if needed, update raw package metadata, and compile domain knowledge
- `query`: answer from existing wiki knowledge
- `update`: revise durable domain pages
- `card`: create or update a reusable Card page
- `moc`: create or update an Atlas/MOC view page
- `plan`: decompose a personal, research, study, career, or project goal into weekly and daily note plans
- `work-item`: create or update a durable project, Jira, issue, MR/PR, bugfix,
  CI failure, implementation, or verification record
- `lint`: lint, audit, review, or structural check
- `import`: treat an existing repo, vault, folder, or export as source material

If the operation is unclear and a write would happen, ask one concise question.
For read-only queries, make a reasonable routing assumption and state it only
when ambiguity matters.

## Resolve Wiki And Domains

For all operations, use `loreforge-config` rules to resolve the wiki root and
sync backend. For rclone-backed wikis, pull the configured remote before
reading domain files or writing local changes. Read:

1. `00_System/domains.md`
2. `00_System/index.md` and `00_System/wiki-layout.md` if present
3. wiki-root `Shared/Raw/` when checking whether a source already exists
4. candidate `Domains/<domain>/SCHEMA.md`
5. candidate `Domains/<domain>/index.md` when more evidence is needed

Ignore `.obsidian*` directories. They are editor profile state.

## Select Domains

Build candidates from:

- explicit domain names in the user request
- domain purpose in `00_System/domains.md`
- domain boundary and out-of-scope rules in `SCHEMA.md`
- tags and sections in `SCHEMA.md`
- relevant entries in `index.md`
- source title, URL, filename, abstract, headings, and user intent

Routing rules:

- **Exact domain named:** select that domain unless the user asks for cross-domain work.
- **Single strong match:** select that domain and continue.
- **Multiple read matches:** query all relevant domains, then synthesize with attribution.
- **Multiple write matches:** choose one primary target when possible. Ask before
  writing multiple domains.
- **No suitable domain:** ask whether to initialize a new domain. Delegate
  initialization to `loreforge-domain`; do not create the domain directly as the
  entrypoint.

For ingest, default to one primary domain. Multi-domain ingest is allowed only
when the user explicitly asks or approves the split.

## Page-Type Decision

Before writing compiled domain knowledge, decide the target page type and fail
closed when the choice is weak:

- `card`: stable reusable concept, mechanism, method, pattern, tradeoff,
  comparison, or decision framework. Delegate directly to `loreforge-card`.
- `moc`: question-driven view, problem framing, proposal/project view, or
  relationship map across multiple pages. Delegate directly to `loreforge-moc`.
- `source`: source excerpt or source-specific lens. Use `loreforge-domain` for
  bounded `Sources/` work after capture.
- `space`: person, organization, project, tool, system, or context record. Use
  `loreforge-work-item` for project records or `loreforge-domain` for other
  bounded `Spaces/` work.

Do not force uncertain material into Cards or MOCs. Ask one concise question or
choose the more conservative Source/Space path.

## Operation Workflows

### Config

Delegate config and sync backend work to `loreforge-config`. After registry
updates, report the selected wiki, default domain, backend, and next action.

### Plan

1. Resolve the wiki root and sync backend through `loreforge-config`.
2. Delegate goal decomposition, weekly allocation, and daily projection to
   `plan-docomposer`.
3. Write only `Calendar/dailynotes/`, `Calendar/weeklynotes/`, and
   `Shared/Templates/` unless the user explicitly asks for a durable domain
   rollup.
4. Do not turn plan notes into agent memory, source capture, or domain ingest.
5. Run the configured post-write sync through `loreforge-config` after edits.

### Init

1. Resolve or collect wiki path, domain name, default language, and sync backend
   through `loreforge-config`.
2. Delegate domain creation to `loreforge-domain`.
3. Run the configured post-write sync through `loreforge-config`.

### Capture

1. Resolve the wiki root.
2. Delegate source preservation to `loreforge-capture`.
3. Capture source material only.
4. Stop after raw package creation. Do not route or compile unless the user
   asked for ingest.

### Ingest

1. Inspect source metadata enough to route.
2. If the source is a paper, DOI, arXiv link, PDF paper, conference preprint,
   or paper-like technical report, delegate the paper-specific workflow to
   `loreforge-paper`.
3. If no raw package exists, delegate non-paper capture to `loreforge-capture`.
4. Select a primary target domain.
5. If secondary domains look relevant, list them and ask before writing there.
6. Make a page-type decision for the compiled output. Delegate reusable Cards
   to `loreforge-card`, MOC/view pages to `loreforge-moc`, and Source/Space
   updates to `loreforge-domain` or the specific paper/work-item workflow.
7. Run post-write sync through `loreforge-config`.

For sources that matter to multiple domains, reuse the same
`Shared/Raw/<source-id>/` package. Do not reuse one domain's pages as another
domain's source of truth.

### Query

1. Select one or more domains.
2. Delegate read-only query work to `loreforge-domain`.
3. Synthesize the final answer with domain/page attribution.
4. Do not save cross-domain synthesis unless the user asks.

### Work Item

Use this path when the user asks to save current project work, a Jira/issue, an
MR/PR, a bugfix, a CI failure, implementation details, verification status, or a
work item under `Spaces/projects/`.

1. Select one primary domain for the project/system.
2. Delegate work-item shaping and bounded domain write guidance to
   `loreforge-work-item`.
3. Let the domain expert create or update the project/work-item Space under the
   selected domain.
4. Preserve diagrams or source artifacts under `Shared/Raw/` only when they add
   durable context.
5. Run post-write sync through `loreforge-config`.

### Card

1. Resolve wiki/domain and confirm write permission.
2. Delegate directly to `loreforge-card`.
3. Require the Card acceptance gate before reporting completion.
4. Run post-write sync through `loreforge-config`.

### MOC

1. Resolve wiki/domain and confirm write permission.
2. Delegate directly to `loreforge-moc`.
3. Require the MOC acceptance gate before reporting completion.
4. Run post-write sync through `loreforge-config`.

### Update

Select the domain, make a page-type decision, and delegate directly to the
leaf workflow: `loreforge-card` for Cards, `loreforge-moc` for Atlas/MOCs,
`loreforge-work-item` for project records, or `loreforge-domain` for
Sources/Spaces/domain repair. Ask before touching 10+ pages or multiple
domains.

### Lint

Delegate lint, audit, and check work to `loreforge-check`. If repairs
are needed, gate write-capable repair work and delegate page fixes to the
relevant leaf workflow: `loreforge-card`, `loreforge-moc`, or
`loreforge-domain` for generic domain repair.

### Import

Delegate source discovery and capture planning to `loreforge-import`. Use
domain routing for the captured material. Ask before converting any existing
repo or vault in place.

## Delegation Prompts

For Card work:

```text
Use loreforge-card.
Wiki root: <wiki-root>
Domain: <domain>
Write policy: <write-confirmed>
Request: <user request>
Source/provenance context: <raw package, source note, or none>
Target page: <existing or proposed Cards/<slug>.md>

Orient on SCHEMA.md, index.md, recent log.md, and relevant pages.
Make page_type_decision before writing.
Update only Domains/<domain>/Cards/, index.md, and log.md unless explicitly asked.
Run the Card acceptance gate before handoff.
Return: page_type_decision, files changed, acceptance checklist, unresolved conflicts, confidence.
```

For MOC work:

```text
Use loreforge-moc.
Wiki root: <wiki-root>
Domain: <domain>
Write policy: <write-confirmed>
View question: <problem, claim, project, decision, or comparison>
Request: <user request>
Target page: <existing or proposed Atlas/<slug>.md>

Orient on SCHEMA.md, index.md, recent log.md, and relevant Cards/Spaces/Sources.
Make page_type_decision before writing.
Update only Domains/<domain>/Atlas/, index.md, and log.md unless explicitly asked.
Run the MOC acceptance gate before handoff.
Return: page_type_decision, files changed, acceptance checklist, unresolved conflicts, confidence.
```

For generic domain work, use this bounded prompt with a subagent when useful,
or run it sequentially when subagents are unavailable:

```text
Use loreforge-domain.
Wiki root: <wiki-root>
Domain: <domain>
Operation: <query|ingest|update|initialize>
Write policy: <read-only|write-confirmed>
Request: <user request>

Stay inside Domains/<domain>/ for domain pages.
Use Shared/Raw/ only for raw source packages.
Orient on SCHEMA.md, index.md, recent log.md, and relevant pages.
If Write policy is read-only, do not create or update wiki files.
If Write policy is write-confirmed, update index.md and insert a newest-first log.md entry.
Return: answer or change summary, files changed, unresolved conflicts, confidence, and whether another domain should be consulted.
```

For multi-domain or multi-source work, start one subagent per selected domain or
domain batch when parallel expert review is useful and the host supports it.
Respect the caller's max concurrency if provided. Otherwise process selected
domains sequentially.

## Response Format

Before write operations with ambiguity, show a concise plan:

```text
Routing:
- operation: ingest
- wiki: <wiki-root>
- primary domain: <domain>
- secondary candidates: <domain-a>, <domain-b>
- reason: <short reason>
```

After delegated work, report:

- domains consulted
- domains written
- raw packages used
- files changed per domain
- sync result
- conflicts or low-confidence areas
- next useful action

For simple read-only queries and obvious single-domain writes, keep routing
details brief.

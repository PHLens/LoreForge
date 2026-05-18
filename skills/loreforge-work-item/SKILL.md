---
name: loreforge-work-item
description: Internal LoreForge workflow for turning project, Jira, issue, MR/PR, CI failure, implementation, or bugfix context into durable work-item records under domain Spaces/projects. Use when the user asks to record current work, summarize a feature/fix, update a project work item, or attach diagrams/artifacts to an existing work item. Keeps problem background, solution, bug diagnosis, verification, and status separate from raw source capture, paper ingest, and activity logs.
user-invocable: false
version: 0.1.0
---

# LoreForge Work Item

Work-item notes are durable project records, not activity logs. Use this
workflow when current engineering/project context should become reusable domain
knowledge under a LoreForge domain.

This skill owns the work-item-specific process:

- deciding whether project work belongs in the wiki
- choosing stable project/work-item placement
- shaping problem background, solution, bug diagnosis, verification, status,
  and follow-ups
- attaching diagrams or artifacts only where they support the explanation
- handing bounded domain writes to `loreforge-domain`

It does not replace:

- `loreforge` for user-facing routing, config, domain selection, write gates,
  and sync
- `loreforge-capture` for raw source preservation
- `loreforge-paper` for paper-specific ingest
- `loreforge-domain` for domain orientation, page writes, index/log updates,
  schema compliance, and validation

## When To Use

Use `loreforge-work-item` when the user asks to save or update a durable record
for:

- project work, feature work, Jira, issue, task, bugfix, CI failure, regression,
  MR, PR, branch, release note input, or implementation review
- "current work", "work item", "project note", "write this under
  Spaces/projects", or equivalent wording
- design/implementation/debug/verification context that should help future
  agents or humans resume the same project
- diagrams, screenshots, or generated artifacts that explain a work item

Do not use this workflow for raw CI log archives, full chat transcripts,
temporary task state, user preferences, daily notes, or one-off debugging
details that have no durable project value.

## Workflow

1. **Resolve context**
   - Use `loreforge` / `loreforge-config` to resolve wiki root, domain, and
     sync backend.
   - Inspect target domain `SCHEMA.md`, `index.md`, recent `log.md`, and
     relevant existing project/work-item pages before writing.
   - Reuse an existing work-item page when the project and issue/topic match.

2. **Choose placement**
   - Follow the domain schema if it already defines a project/work-item
     convention.
   - Otherwise prefer `Domains/<domain>/Spaces/projects/<project>/<work-item>.md`.
   - Put stable issue IDs in the filename when available, such as
     `pytorch-14461-backward-boundary.md`.
   - Use lowercase hyphenated paths. Treat the project directory as the
     product, repo, system, or work stream name, such as `torchdump`.

3. **Write durable synthesis**
   - Explain the problem and desired behavior before implementation details.
   - Record decisions, code locations, root causes, fixes, verification, and
     remaining risks.
   - For bugs, capture symptom, impact, root cause, fix, and verification.
   - Do not save chat transcripts, command-by-command chronology, raw logs, or
     every intermediate mistake.
   - Keep implementation facts concrete enough that a future agent can resume
     without rereading the whole conversation.

4. **Handle artifacts**
   - Use `Shared/Raw/<source-id>/` for diagrams, logs, screenshots, or source
     artifacts that need preservation outside the domain page.
   - A work-item raw package can use the issue ID as source-id, for example
     `Shared/Raw/pytorch-14461/`.
   - Attach diagrams or artifacts only in the section that explains them. Do
     not create an attachment dump at the end.
   - Source-backed claims should use body footnotes to raw manifests or domain
     source notes. Conversation-local or repo-local context does not need fake
     citations.

5. **Validate and sync**
   - Update `index.md` when creating or materially changing an indexable Space.
   - Insert one concise newest-first `log.md` entry; do not duplicate the page.
   - Run the native domain validator when available.
   - Run configured post-write sync through `loreforge-config`.

## Page Shape

Use only sections that have substance. Common sections:

- Context / Problem Background
- Desired Behavior / Scope
- Solution
- Implementation Details
- Bug Diagnosis And Fixes
- Verification
- Current Status
- Follow-ups / Risks

Prefer durable explanation over process narration. Do not write "I did X, then
I did Y" unless the sequence itself explains the root cause or risk.

Do not include editor/process narration such as:

- "this should be a work-item note"
- "I am adding this to the wiki"
- "the page should live in X"
- "I attached this because..."

If a placement or attachment decision matters for maintainers, put it in
`log.md`, not in the work-item page body.

Frontmatter follows the domain schema. Work-item pages are usually `type:
space`; tags should use the domain taxonomy and stay coarse, such as `project`
or a schema-defined equivalent.

## Link And Citation Style

- Use one or a small number of source footnotes for source-backed claims when a
  Jira, issue, MR, PR, design doc, CI log, or raw artifact is the dominant
  source. Avoid ending every paragraph with the same footnote unless the source
  boundary would otherwise become ambiguous.
- Weave concepts, systems, modules, files, failures, fixes, and related work
  items into prose with `[[wiki|readable alias]]` at the point where they are
  used.
- Relate the work item to existing Cards, Atlas pages, Spaces, and prior work
  items by naming the shared problem or solution pattern: boundary detection,
  replay determinism, backend comparison, serialization shape, concurrency,
  CI environment drift, sync behavior, schema migration, etc.
- Avoid standalone "related Cards" or "related pages" tables whose main purpose
  is bookkeeping. Tables are acceptable only when they carry real analysis,
  such as comparing symptoms, root causes, implementation options, or
  verification coverage.
- Prefer direct positive descriptions. Use "not X but Y" contrast only when it
  prevents a concrete misconception, and remove repeated contrastive phrasing
  before handoff.
- For cross-domain conceptual links, use explicit path-qualified wikilinks such
  as `[[Domains/gpu-arch-research/Cards/simt-core-pipeline|SIMT core
  pipeline]]` when the target exists in the same wiki.

## Domain Handoff Prompt

Use this bounded prompt when delegating the actual domain write:

```text
Use loreforge-domain.
Wiki root: <wiki-root>
Domain: <domain>
Operation: update
Write policy: write-confirmed
Work item: <project>/<issue-id-topic>
Request: Create or update a durable work-item record using loreforge-work-item rules.

Stay inside Domains/<domain>/ for domain pages.
Use Shared/Raw/ only for diagrams, logs, screenshots, or source artifacts that need preservation.
Orient on SCHEMA.md, index.md, recent log.md, existing project/work-item pages, and relevant Cards/Atlas/Spaces.
Write the page as a durable problem/solution/debug/verification record, not a chronology or chat transcript.
Use natural `[[wiki|alias]]` links for related concepts, systems, modules, failures, fixes, and similar work items.
Put attachments in the section where they support the explanation.
Update index.md when creating or materially changing an indexable Space.
Insert one concise newest-first log.md entry.
Return: page path, artifacts preserved, validation result, sync status, unresolved gaps, and whether another domain should be consulted.
```

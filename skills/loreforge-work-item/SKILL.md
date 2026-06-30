---
name: loreforge-work-item
description: Internal LoreForge workflow for turning project, Jira, issue, MR/PR, CI failure, implementation, or bugfix context into durable work-item records under root Spaces/projects. Use when the user asks to record current work, summarize a feature/fix, update a project work item, or attach diagrams/artifacts to an existing work item. Keeps problem background, solution, bug diagnosis, verification, and status separate from raw source capture, paper ingest, and activity logs.
user-invocable: false
version: 0.1.0
---

# LoreForge Work Item

Work-item notes are durable project records, not activity logs. Use this
workflow when current engineering/project context should become reusable wiki
knowledge under root `Spaces/`.

This skill owns the work-item-specific process:

- deciding whether project work belongs in the wiki
- choosing stable project/work-item placement
- shaping problem background, solution, bug diagnosis, verification, status,
  and follow-ups
- applying formal project-artifact language gates for proposals, research
  plans, literature surveys, experimental protocols, and project design notes
- attaching diagrams or artifacts only where they support the explanation
- writing bounded project records under `Spaces/projects/`

It does not replace:

- `loreforge` for user-facing routing, config, domain selection, write gates,
  and sync
- `loreforge-capture` for raw source preservation
- `loreforge-paper` for paper-specific ingest
- `loreforge-card` for separate reusable concepts discovered during the work
- `loreforge-moc` for separate project/problem views
- `loreforge-domain` for generic domain orientation, Source/Space repairs, and validation

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
- formal project artifacts under `Spaces/projects/`, including
  `proposal*.md`, `research-plan*.md`, `literature-survey*.md`, experimental
  protocols, and project design notes

Do not use this workflow for raw CI log archives, full chat transcripts,
temporary task state, user preferences, daily notes, or one-off debugging
details that have no durable project value.

## Workflow

1. **Resolve context**
   - Use `loreforge` / `loreforge-config` to resolve wiki root, domain, and
     sync backend.
   - Inspect `00_System/agent-policy.md`, `00_System/card-domains.md`,
     relevant existing `Spaces/` project/work-item pages, and relevant
     `Cards/<domain>/` pages before writing.
   - Reuse an existing work-item page when the project and issue/topic match.

2. **Choose placement**
   - Follow `00_System/wiki-layout.md` or a project-local convention if it
     already defines one.
   - Otherwise prefer `Spaces/projects/<project>/<work-item>.md`.
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
   - Use `Sources/Raw/<source-id>/` for diagrams, logs, screenshots, or source
     artifacts that need preservation outside the domain page.
   - A work-item raw package can use the issue ID as source-id, for example
     `Sources/Raw/pytorch-14461/`.
   - Attach diagrams or artifacts only in the section that explains them. Do
     not create an attachment dump at the end.
   - Source-backed claims should prefer inline wikilinks to wiki-local raw
     artifacts, manifests, or Source notes, using path-qualified links such as
     `[[Sources/Raw/<source-id>/manifest|readable source alias]]`. Use source
     footnotes only when paragraph-level provenance would otherwise be
     ambiguous. Conversation-local or repo-local context does not need fake
     citations.

5. **Validate and sync**
   - Follow the pre-write gate in `00_System/agent-policy.md`.
   - Write a transaction snapshot only when policy marks the operation high
     risk; do not create routine per-edit logs.
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

If a placement or attachment decision matters for maintainers, put it in
the final handoff or a high-risk transaction record, not in the work-item page
body.

## Formal Project Artifacts

Apply the `loreforge` Compiled Page Language Gate to every work-item or project
page before handoff. Project files such as `proposal*.md`, `research-plan*.md`,
`literature-survey*.md`, `experimental-protocol*.md`, and project design notes
also use the narrower rules below.

Required style:

- Write the artifact itself: research problem, motivation, related-work
  boundary, method, implementation plan, evaluation plan, scope, risks, and
  expected contribution.
- Literature surveys should compare mechanisms, assumptions, scope, IR level,
  backend coverage, artifact generation, and evaluation signals. They should
  not say "this page currently contains..." or promise future additions unless
  that appears under a substantive "Open Gaps" or "Survey Scope" section.
- Research plans should use milestone, artifact, experiment, and validation
  language. Avoid "Non-Goals" sections when they only restate obvious
  exclusions; use "Scope" or "Boundary" to define what the work covers.

Frontmatter follows the domain schema. Work-item pages are usually `type:
space`; tags should use the domain taxonomy and stay coarse. Use `project` by
default when the wiki taxonomy supports it; otherwise use the local
work-item equivalent. Pages under `Spaces/projects/` are indexable work-item
Spaces, but new pages should still include coarse tags when policy allows it.

## Link And Citation Style

- Prefer inline wikilinks to wiki-local Jira/issue/MR/PR/design-doc/CI-log raw
  artifacts, manifests, or Source notes, using path-qualified links such as
  `[[Sources/Raw/<source-id>/manifest|readable source alias]]`. Use source
  footnotes only when paragraph-level provenance would otherwise be ambiguous.
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
- For project artifacts, apply the stricter gate in "Formal Project Artifacts"
  before this general style rule.
- For cross-domain conceptual links, use explicit path-qualified wikilinks such
  as `[[Cards/cs/simt-core-pipeline|SIMT core pipeline]]` when the target
  exists in the same wiki.

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

Stay inside Spaces/ for work-item pages.
Use Sources/Raw/ only for diagrams, logs, screenshots, or source artifacts that need preservation.
Orient on 00_System/agent-policy.md, 00_System/card-domains.md, existing project/work-item pages, and relevant Cards/Atlas/Spaces.
Write the page as a durable problem/solution/debug/verification record, not a chronology or chat transcript.
For proposal, research-plan, literature-survey, experimental-protocol, or design-note files, apply the Formal Project Artifacts gate.
Use natural `[[wiki|alias]]` links for related concepts, systems, modules, failures, fixes, and similar work items.
Put attachments in the section where they support the explanation.
Follow the pre-write gate and rely on validator output after writing; create a transaction only when policy marks the operation high risk.
Return: page path, artifacts preserved, validation result, sync status, unresolved gaps, and whether another domain should be consulted.
```

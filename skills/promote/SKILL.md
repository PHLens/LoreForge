---
name: promote
description: Use when approved LoreForge staged packages should become stable wiki notes; supports batch promotion, domain index updates, staging archive, and wiki log entries.
user-invocable: true
---

# Promote

Promote staged material into stable LoreForge wiki knowledge.

This is the transaction boundary for stable wiki writes. `ingest` and `writeback` prepare staged material; `promote` performs the reviewed stable update.

## Trigger

`promote`, `promote staged note`, `promote writeback`, `晋升`, `发布到 wiki`

## Inputs

Acceptable inputs:

- staged ingest folder under `<ingest>/`
- staged writeback folder under `<writeback>/`
- specific staged source/card/map files
- a user-approved promotion plan

Prefer a staged package with `manifest.md`. A package may contain multiple candidate notes and deltas.

## Discovery

1. Locate the target wiki through `~/.config/loreforge/registry.toml`, a user-provided path, or the current directory if it contains `.loreforge/wiki.toml`.
2. Read `<wiki>/.loreforge/wiki.toml` and resolve configured paths. Fallbacks:
   - inbox: `10_Inbox`
   - ingest: `10_Inbox/ingest`
   - writeback: `10_Inbox/writeback`
   - domains: `20_Domains`
   - shared: `30_Shared`
   - archive: `40_Archive`
   - log_file: `00_System/Wiki Log.md`
3. Read the wiki `AGENTS.md`, vault map, relevant task view, target domain map, and target domain `+Wiki Index.md`.

## Hard Boundary

This skill must not:

- promote without an explicit user-approved plan
- create stable notes from raw unsummarized source material
- store agent-local experience in the wiki
- save full chat transcripts
- delete or rewrite unrelated stable notes
- commit or push git changes

It may:

- create stable notes from reviewed staged notes
- move staged files to stable destinations
- archive consumed staging folders after successful promotion
- apply small approved deltas to existing stable notes
- update the target domain `+Wiki Index.md`
- append one entry to the wiki log
- suggest running `lint` after promotion

## Batch Semantics

One promotion transaction can promote multiple candidate notes when they belong to the same staged package.

Use batch promotion for:

- one source that generated several concept cards
- one conversation that produced multiple reusable concepts
- a card plus related source note and index delta
- a MOC update plus related cards

Do not batch unrelated topics just because they were staged near the same time.

## Promotion Workflow

1. Read the staged package `manifest.md`. If missing, infer a plan from staged files only after telling the user the package is incomplete.
2. Determine target scope:
   - domain content: `<domains>/<Domain>/`
   - cross-domain method: `<shared>/Methods/`
   - cross-domain concept: `<shared>/Concepts/`
3. Read `candidate_notes`, `updates`, `source_type`, `provenance`, and `promotion_reason` from the manifest.
4. Check for existing related cards, source notes, MOCs, and index entries.
5. Build a promotion plan:
   - files to create or move
   - stable files to update
   - index entries to add or adjust
   - consumed staging folder to archive
   - wiki log entry to append
6. Show the plan and ask for confirmation before changing stable areas.
7. Apply the approved plan.
8. Set promoted notes to `status: stable` and add or update promotion metadata.
9. Update the target domain index.
10. Move consumed staging material to `<archive>/promoted/<YYYY-MM-DD>-<short-slug>/`, or mark it `status: promoted` if moving would break local references.
11. Append the wiki log entry.
12. Report created, updated, archived, skipped, and follow-up lint suggestions.

## Manifest Contract

`promote` expects this minimum manifest shape from `ingest` and `writeback`:

```markdown
---
type: <ingest|writeback>
source_type: <source type>
status: staged
domain: <Domain or Shared>
created: YYYY-MM-DD
provenance:
  - <source path/url/conversation>
candidate_notes:
  - path: Cards/<candidate-card>.md
    kind: card
updates:
  - path: +Wiki Index.md
    kind: index_delta
promotion_reason: <why this should become stable wiki knowledge>
---
# Package: <Title>
```

If `candidate_notes` contains multiple items, treat them as one batch and promote only the approved subset.

## Stable Destinations

| Staged kind | Stable destination |
|---|---|
| Source summary | `<domains>/<Domain>/Sources/` |
| Concept card | `<domains>/<Domain>/Cards/` |
| Topic map or synthesis | `<domains>/<Domain>/MOCs/` |
| Cross-domain method | `<shared>/Methods/` |
| Cross-domain concept | `<shared>/Concepts/` |

## Index Update Logic

Update the target domain `+Wiki Index.md` in the same promotion transaction.

Rules:

- Add stable notes only. Do not index captures or staged packages.
- Prefer small additive edits over rewriting the whole index.
- Keep entries compact enough for agents to scan quickly.
- Preserve human-written organization unless the user approves a restructure.
- Avoid duplicate entries. If a note already exists, update the existing entry.
- Include enough retrieval signal: title, kind, one-line meaning, aliases or key relations when useful.

Recommended entry shape:

```markdown
- [[Note Title]] - <kind>; <one-line reusable meaning>. aliases: <optional>; related: [[A]], [[B]]
```

Use local section names if the index already has them. If the index is empty, start with:

```markdown
## Cards

## Sources

## MOCs
```

## Log Logic

Append one entry to the wiki log for each approved promotion transaction.

Default log file:

```text
00_System/Wiki Log.md
```

Use `log_file` from `.loreforge/wiki.toml` if present.

Write logs for:

- promoted staged ingest material
- promoted writeback packages
- approved stable note edits made during promotion
- index updates caused by promotion

Do not write logs for:

- query
- capture
- incomplete staged drafts
- staged package creation already logged by `ingest` or `writeback`
- read-only lint
- git sync

Log entry format:

```markdown
## YYYY-MM-DD | promote | <Domain or Shared>

- staged_from:
  - `<staged path>`
- created:
  - [[New Note]] (`path/to/New Note.md`)
- updated:
  - [[Existing Note]] (`path/to/Existing Note.md`)
  - [[+Wiki Index]] (`20_Domains/<Domain>/+Wiki Index.md`)
- archived_to:
  - `40_Archive/promoted/<YYYY-MM-DD>-<short-slug>/`
- skipped:
  - `<item>` - <reason>
- reason:
  - <why this became stable wiki knowledge>
```

The log is a human-readable changelog, not a full audit trail. Git history remains the exact diff record.

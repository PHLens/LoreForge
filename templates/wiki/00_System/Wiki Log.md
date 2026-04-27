# Wiki Log

Human-readable timeline of meaningful wiki evolution.

This log records substantive knowledge operations, not every agent action. Git history remains the exact diff record.

## What To Log

Log:

- promoted staged ingest material
- promoted writeback packages
- approved stable note edits made during promotion
- index updates caused by promotion
- substantive staged ingest package creation
- substantive staged writeback package creation
- lint pass with meaningful findings

Do not log:

- ordinary query
- ordinary capture
- incomplete staged drafts
- read-only lint with no meaningful findings
- git sync

## Promotion Entry

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

## Staged Package Entry

```markdown
## YYYY-MM-DD | stage | <ingest|writeback> | <Domain or unknown>

- package:
  - `<ingest-or-writeback>/<YYYY-MM-DD>-<short-slug>/`
- source_type:
  - `<source type>`
- candidate_notes:
  - `Cards/<candidate-card>.md`
  - `Sources/<candidate-source>.md`
- reason:
  - <why this package may deserve promotion>
```

## Lint Findings Entry

```markdown
## YYYY-MM-DD | lint | <scope>

- findings:
  - <meaningful finding>
- follow_up:
  - <proposed maintenance action>
```

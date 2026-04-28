# Wiki Log

Human-readable timeline of meaningful wiki evolution.

This log records substantive knowledge operations, not every agent action. Git history remains the exact diff record.

## What To Log

Log:

- promoted staged ingest material
- promoted writeback packages
- approved stable note edits made during promotion
- card index updates caused by promotion
- lint pass with meaningful findings

Do not log:

- ordinary query
- incomplete staged drafts
- ordinary staged package creation
- read-only lint with no meaningful findings
- git sync

## Promotion Entry

```markdown
## YYYY-MM-DD | promote | <package-slug>

- staged_from:
  - `<staged path>`
- created:
  - [[New Note]] (`path/to/New Note.md`)
- updated:
  - [[+Wiki Index]] (`00_System/+Wiki Index.md`)
- archived_to:
  - `Archive/promoted/<YYYY-MM-DD>-<short-slug>/`
- skipped:
  - `<item>` - <reason>
- reason:
  - <why this became stable wiki knowledge>
```

## Lint Findings Entry

```markdown
## YYYY-MM-DD | lint | <scope>

- findings:
  - <meaningful finding>
- follow_up:
  - <proposed maintenance action>
```

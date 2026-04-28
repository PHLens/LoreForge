---
aliases:
tags:
  - system/log
up: "[[+Atlas]]"
---
# +Wiki Log

Append-only operation log. Do not edit historical entries.

## Entry Shapes

```markdown
## YYYY-MM-DD | stage | <package-slug>

- package:
  - `<staged path>`
- source_type:
  - `<source type>`
- candidate_notes:
  - `Cards/<candidate-card>.md`
- reason:
  - <why this package may deserve promotion>

## YYYY-MM-DD | promote | <package-slug>

- staged_from:
  - `<staged path>`
- created:
  - <new note path>
- updated:
  - `MOCs/Scope/+Wiki Index.md`
- archived_to:
  - `Archive/promoted/<YYYY-MM-DD>-<short-slug>/`
- reason:
  - <why this became stable wiki knowledge>
```

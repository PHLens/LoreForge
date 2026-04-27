---
name: capture
description: Use when the user says capture, save, bookmark, remember this source, or quickly store a URL/note/idea in LoreForge; thin alias for ingest mode=capture.
user-invocable: true
---

# Capture

`capture` is the quick-entry form of `ingest mode=capture`.

Use it to save a short, source-oriented note without deciding domain, final structure, or stable value.

## Trigger

`capture <content/url/summary>`

Equivalent:

```text
ingest mode=capture <content/url/summary>
```

## Discovery

1. Locate the target wiki through `~/.config/loreforge/registry.toml`.
2. If the user names a wiki, use that entry. Otherwise use the registry default.
3. Read `<wiki>/.loreforge/wiki.toml`.
4. Use `[paths].capture` from `wiki.toml`; fallback to `10_Inbox/capture`.
5. If no registry exists but the current directory contains `.loreforge/wiki.toml`, use the current directory.
6. If no wiki can be resolved, ask for a wiki name or path before writing.

## Format

File:

```text
<capture>/<YYYY-MM-DD>-<short-slug>.md
```

```markdown
---
aliases:
tags:
  - inbox
  - capture
url: <source_url>
date: YYYY-MM-DD
status: captured
---
# Title
## Summary
<Brief summary>
## Key Points
- Point 1
## References
- Source URL
```

## Rules

- Auto-create only inside the configured inbox. Inbox is staging.
- Keep the note short. Do not synthesize a full article unless the user asked for that.
- Do not process into concept cards; use `ingest mode=process` for that.
- Prefer capture when the material may be valuable but the correct domain or structure is unclear
- Do not store agent-local experience, preferences, or task state in the wiki; use `pamem` for that.
- Do not update the wiki log unless this capture is later processed into a staged package.
- Do not commit or push git changes.

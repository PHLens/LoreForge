---
name: lint
description: Use for LoreForge wiki health checks, structure validation, unresolved links, missing package manifests, domain index drift, metadata drift, and read-only lint reports.
user-invocable: true
---

# Lint Wiki

Read-only structural health check. No files are modified.

## Trigger

`lint wiki`, `lint`, `健康检查`

## Discovery

If the user names a wiki, resolve it through `~/.config/loreforge/registry.toml`. If no wiki is named, use the current directory when it contains `.loreforge/wiki.toml`; otherwise use the registry default.

## Execution

```bash
bash <skill-path>/lint/scripts/lint-wiki.sh [wiki_path]
```

If no path is given, run against the current directory.

## Check Items

1. **Discovery health** - required files such as `.loreforge/wiki.toml`, `AGENTS.md`, vault map, wiki log, and configured view files.
2. **Domain health** - each domain should have a domain map and `+Wiki Index.md`.
3. **Unresolved links** - `[[link]]` targets that do not exist as files, excluding common attachments.
4. **Duplicate or near-duplicate titles** - case/spacing variants across Markdown files.
5. **Staged material** - captured or staged notes still under the configured inbox, plus ingest/writeback packages missing `manifest.md`.
6. **Card discoverability** - cards with no inbound link, no domain index entry, and no `up:` field.
7. **Metadata drift** - empty tags, missing frontmatter on stable cards, and common malformed fields.

## Output

Structured report in chat: counts + examples per check item. No file writes.

## Boundary

This skill must not append logs, update indexes, reformat notes, commit, or push. If the user wants fixes, report a proposed patch plan first.

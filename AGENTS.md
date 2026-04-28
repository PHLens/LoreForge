# LoreForge Agent Rules

LoreForge is a framework repository for LLM-wiki style knowledge bases.

## Core Boundary

- LoreForge stores framework rules, templates, and skills.
- Actual professional knowledge lives in separate wiki instances created from these templates.
- Agent-local experience, preferences, and task state belong in `pamem`, not in LoreForge.

## When Working In This Repo

- Do not add domain knowledge as repository content unless it is an example template.
- Keep framework files generic and agent-agnostic.
- Prefer small Markdown files with clear ownership over large central documents.
- Keep repo-specific behavior in the concrete wiki repo, not in this framework repo.
- Keep generic reusable conventions under `docs/` or `templates/wiki/`.

## Knowledge Boundary

Use this split:

| Content | Destination |
|---|---|
| Agent-local workflow memory | `pamem` |
| User/workspace preference | `pamem` |
| Current task state | `pamem` |
| Professional concepts, source notes, curated knowledge | a LoreForge wiki instance |
| Framework schema, templates, views, skills | this repo |

## Change Policy

Auto-safe changes:

- Add generic docs or templates
- Clarify wording without changing semantics

Ask before:

- Renaming public directories
- Changing template schema
- Changing skill behavior that existing sessions may depend on

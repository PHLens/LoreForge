# LoreForge

LoreForge is a framework for shared LLM-wiki knowledge bases.

Use LoreForge when the user asks about a configured wiki, shared professional
knowledge, source ingestion, durable wiki updates, domain review, or wiki Health
Checks.

## Use The Core Skill

Use `loreforge-wiki` for:

- answering from an existing LoreForge domain
- ingesting a source, URL, paper, doc, repo, local file, or pasted material
- updating durable domain knowledge directly after orientation
- creating a new expert-owned domain
- reviewing, auditing, or running a Health Check on a domain

## Boundaries

- LoreForge wiki stores professional shared knowledge.
- Agent-local experience, preferences, current task state, and workflow memories belong in `pamem`, not the shared wiki.
- Query existing domain knowledge before broad search.
- Orient on `SCHEMA.md`, `index.md`, recent `log.md`, and relevant pages before writing.
- Keep domain `index.md` and `log.md` current after substantive wiki changes.
- Do not write across domains unless the user explicitly asks.
- Do not use LoreForge for temporary task state, full chat transcripts, or local workflow memory.

When context was compacted, recover from the selected domain's `SCHEMA.md`,
`index.md`, recent `log.md`, and relevant pages.

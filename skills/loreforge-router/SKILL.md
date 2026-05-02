---
name: loreforge-router
description: Use when a LoreForge request may involve an unknown domain, multiple domains, or cross-domain query/ingest coordination. Routes work to domain experts that use loreforge-wiki.
user-invocable: true
version: 0.1.0
---

# LoreForge Router

Route user requests to the right LoreForge domain experts.

Use this as the front door when the user does not name a domain, asks across
domains, or provides a source that may belong in more than one domain. The
router chooses target domains and delegates durable work to `loreforge-wiki`.

Always:

- resolve the active wiki before routing
- inspect available domains before choosing
- keep one expert-owned domain as the write boundary
- treat raw source packages as shared wiki-root `Shared/Raw/<source-id>/`
  data, with `Shared/SourceRecords/` kept only for legacy compatibility
- use `loreforge-wiki` for domain query, ingest, update, review, and Health Check
- report routing decisions and uncertainty clearly

Do not:

- write domain pages directly as the router
- merge multiple domains into one answer without domain attribution
- update multiple domains on a write unless the user asked or approved
- route editor state such as `.obsidian*`

## When This Skill Activates

Use this skill when the user or another agent asks to:

- ingest a source but does not name the target domain
- ingest a source that may span multiple domains
- query across domains
- ask "which domain should this go to?"
- coordinate multiple expert agents
- decide whether a new domain is needed

Do not use this skill when the user names one domain and the request is clearly
single-domain. Use `loreforge-wiki` directly.

## Resolve Wiki And Domains

Resolve the wiki root using the same priority as `loreforge-wiki`:

1. User-provided wiki path.
2. `WIKI_PATH`.
3. `WIKI_NAME` in `~/.config/loreforge/registry.toml`.
4. Registry default wiki.
5. `~/wiki`, but tell the user before writing there.

Then read:

1. `00_System/domains.md`
2. `00_System/index.md` if present
3. wiki-root `Shared/Raw/` when checking whether a source already exists
4. Candidate `Domains/<domain>/SCHEMA.md`
5. Candidate `Domains/<domain>/index.md` when more evidence is needed

Ignore `.obsidian*` directories. They are editor profile state.

## Classify The Request

Classify the operation before selecting domains:

- `query`: answer from wiki knowledge
- `ingest`: integrate a source, URL, file, repo, paper, or paste
- `update`: revise durable existing knowledge
- `review`: lint, audit, or Health Check
- `initialize`: create a new domain
- `migrate`: ingest an existing repo, vault, or folder as source material

If the operation is unclear, ask one concise question before writing.

## Select Domains

Build a short candidate list from:

- explicit domain names in the user request
- domain purpose in `00_System/domains.md`
- domain boundaries and out-of-scope rules in `SCHEMA.md`
- tags and section names in `SCHEMA.md`
- relevant entries in domain `index.md`
- source title, URL, filename, abstract, headings, and user intent

Use these routing rules:

- **Exact domain named:** route only there unless the user asks for cross-domain work.
- **Single strong match:** route there and state why.
- **Multiple read matches:** query all relevant domains, then synthesize with attribution.
- **Multiple write matches:** pick one primary target when possible. If durable
  writes belong in more than one domain, ask before writing multiple domains.
- **No suitable domain:** ask whether to initialize a new domain. If approved,
  delegate initialization to `loreforge-wiki`; do not create the domain directly
  as the router. Do not force off-domain material into the nearest domain.

For ingest, default to **one primary domain**. Multi-domain ingest is allowed
only when:

- the user explicitly asks for it, or
- the source has distinct durable value for multiple domains and the user
  approves the split.

For sources that matter to multiple domains, use one shared raw source package
in wiki-root `Shared/Raw/<source-id>/`. Each selected domain gets domain-owned
synthesis and an optional `Domains/<domain>/Sources/` domain Source note only
when that source-specific compiled note is useful.

## Delegation

For each selected domain, delegate to a domain expert using `loreforge-wiki`.

For multi-domain work, use subagents when parallel expert review is useful and
the host supports them. Otherwise process selected domains sequentially. When
using subagents, start one subagent per selected domain. Give each subagent or
sequential pass a bounded prompt:

Set `Write policy: read-only` for query operations. Use
`Write policy: write-confirmed` only when the router has selected an approved
write target.

```text
Use loreforge-wiki.
Wiki root: <wiki-root>
Domain: <domain>
Operation: <query|ingest|update|review|initialize|migrate>
Write policy: <read-only|write-confirmed>
Request: <user request>

Stay inside Domains/<domain>/ for domain pages. Use wiki-root
`Shared/Raw/<source-id>/` only for shared raw source packages. Treat
`Shared/SourceRecords/` as legacy compatibility only.
Orient on SCHEMA.md, index.md, recent log.md, and relevant pages.
If Write policy is read-only, do not create or update wiki files.
If Write policy is write-confirmed, update index.md and insert a newest-first
log.md entry.
Return: answer or change summary, files changed, unresolved conflicts,
confidence, and whether another domain should be consulted.
```

Use the same boundaries for subagent and sequential execution.

## Query Routing

For cross-domain query:

1. Query each selected domain read-only through `loreforge-wiki`.
2. Synthesize the final answer.
3. Attribute claims by domain and page.
4. Surface disagreements or gaps.
5. Do not write a cross-domain synthesis unless the user asks to save it.

When saving a cross-domain synthesis, ask where it belongs:

- one existing domain's `Atlas/`
- a new domain
- no durable write

## Ingest Routing

For ingest:

1. Inspect the source enough to route it.
2. Select a primary target domain.
3. If more domains may be relevant, list them as secondary candidates.
4. Delegate shared raw source capture and primary domain synthesis to
   `loreforge-wiki` for the target domain.
5. If multiple domains are approved, split the work into separate domain-bound
   synthesis passes that reuse the same wiki-root raw package. Do not reuse one
   domain's pages as another domain's source of truth.

For existing repos, vaults, or folders, route them as source material. Do not
adopt alternate layouts as long-term LoreForge structure unless the user
explicitly asks to convert in place.

## Response Format

Before write operations, show a concise routing plan:

```text
Routing:
- operation: ingest
- wiki: <wiki-root>
- primary domain: <domain>
- secondary candidates: <domain-a>, <domain-b>
- reason: <short reason>
```

After delegated work, report:

- domains consulted
- domains written
- files changed per domain
- conflicts or low-confidence areas
- next useful action

For simple read-only queries, keep the routing plan implicit unless there is
domain ambiguity.

---
name: loreforge-paper
description: Internal LoreForge workflow for paper-specific note updates and ingest. Use for arXiv, DOI, PDF, conference paper, preprint, or local paper requests that should be resolved through Zotero while keeping paper raw files outside the vault. Treats Zotero as the paper manifest/raw-file system, writes paper notes under `Domains/research/Spaces/papers/`, uses Zotero URI PDF jump links, and keeps claims, methods, evaluation, limits, related work links, and downstream domain handoff separate from ordinary single-source ingest.
user-invocable: false
version: 0.3.0
---

# LoreForge Paper

Paper ingest is a distinct workflow. Do not collapse it into generic
single-source ingest.

This skill owns the paper-specific process:

- paper identity resolution through Zotero metadata, citekey, DOI/arXiv ID,
  title, PDF filename, or user-provided context
- read-only access to Zotero-managed paper raw files outside the vault
- paper note shape under `Domains/research/Spaces/papers/<citekey>.md`
- contribution, mechanism, evaluation, and limit extraction
- related paper / similar problem links
- downstream handoff guidance to `loreforge-card`, `loreforge-moc`, or
  `loreforge-domain` after the paper note is updated

It does not replace:

- `loreforge` for user-facing routing, domain selection, write gates, and sync
- `loreforge-capture` for non-paper raw package preservation
- `loreforge-card` for reusable Card updates from the paper
- `loreforge-moc` for paper-derived relationship or proposal views
- `loreforge-domain` for domain orientation, Source/Space writes, index/log
  updates, and schema compliance

## When To Use

Use `loreforge-paper` when the source is a research paper or should be treated
as one:

- arXiv / OpenReview / DOI / ACM / IEEE / USENIX / conference PDF
- local paper PDF already managed by Zotero
- a paper-like technical report with authors, methods, evaluation, and claims
- user asks to "capture paper", "ingest paper", "what did this paper solve",
  "paper contribution", "related work", or "paper notes"

For ordinary articles, blogs, docs, transcripts, reports, local notes, or web
pages, use the main `loreforge` entrypoint so it can choose
`loreforge-card`, `loreforge-moc`, or a conservative Source/Space path.

## Workflow

1. **Resolve context**
   - Use `loreforge` / `loreforge-config` to resolve wiki root and sync
     backend.
   - Resolve the paper to exactly one Zotero item using the user-provided
     citekey, title, DOI/arXiv ID, PDF filename, Zotero URI, existing paper
     note frontmatter, or local Zotero metadata.
   - If the paper cannot be resolved to one Zotero item, stop and ask the user
     to add/import/select the paper in Zotero first. Do not create paper raw packages,
     copy PDFs into the vault, or fall back to `Shared/Raw/`.
   - The canonical note path is
     `Domains/research/Spaces/papers/<citekey>.md`. Inspect an existing note
     at that path before writing. Inspect target domain `SCHEMA.md`,
     `index.md`, recent `log.md`, and relevant pages only for read-only
     orientation or downstream handoff.
   - If `Domains/research/Spaces/papers/` does not exist, stop and ask for the
     `research` domain to be initialized or selected as the paper-note domain.
     Do not create a new domain or paper-note directory from this workflow.

2. **Read Zotero raw files**
   - Treat Zotero-managed PDF files, snapshots, and attachment directories as
     raw artifacts outside the vault. Agents may open, convert, quote within
     copyright limits, summarize, and cite page locations from PDFs, but must
     not modify, overwrite, rename, delete, copy, compress, OCR-in-place, or
     relocate them.
   - Do not create or reorganize `Shared/Zotero/`, `Shared/Raw/`, or any
     paper-attachment directory in the vault as part of the paper workflow.
   - If extraction tooling needs scratch output, keep it outside the wiki. Do
     not write extracted text, manifests, caches, screenshots, or helper files
     into the vault unless they are part of the Markdown paper note requested by
     the user.

3. **Route**
   - Paper notes live in the `research` domain by default:
     `Domains/research/Spaces/papers/`.
   - Select secondary domains only when they would need their own compiled
     synthesis; ask before writing multiple domains.
   - Domain routing in this skill is advisory. The paper workflow itself must
     write only Markdown paper notes under `Domains/research/Spaces/papers/`.

4. **Write the paper note**
   - Write Markdown note files only inside
     `Domains/research/Spaces/papers/`. Creating `<citekey>.md` is allowed
     when no note exists; otherwise update the existing same-citekey note
     unless the user names a different target.
   - Preserve existing frontmatter such as `citekey`, `title`, `aliases`,
     `authors`, `date`, `conference`, `link`, `zotero_link`, Zotero fields,
     tags, and library/item IDs. Fill missing fields only from Zotero metadata,
     the paper itself, DOI/arXiv metadata already available locally, or
     user-provided context.
   - Treat Zotero/exporter frontmatter and Zotero URIs as the paper manifest
     surface. Do not create, update, or backfill parallel LoreForge paper
     manifests with `source_id`, `content_hash`, `candidate_domains`,
     `compiled_pages`, or lifecycle state.
   - Put the PDF jump link in the note body as a Zotero URI, for example
     `[PDF](zotero://open-pdf/...)`. Do not link to or require a wiki-local PDF.
   - Do not write `manifest.md`, `origin.md`, `extracted/`, `original/`,
     `assets/`, raw packages, registries, or sibling paper notes as part of
     this workflow.
   - Add broadly reusable concepts to Cards only when the concept is durable
     beyond the paper and a separate downstream domain write has been
     explicitly requested or approved. Put proposal/current-argument synthesis
     in Atlas only through that separate handoff.

5. **Validate And Sync**
   - Check that the changed paths are only Markdown files under
     `Domains/research/Spaces/papers/`.
   - Validate paper-note format with the native domain validator when practical.
   - Run configured post-write sync through `loreforge-config`.
   - Report the Zotero item/citekey used, note files changed, PDF files read,
     validation/sync result, and unresolved confidence limits.

## Paper Storage Policy

Paper raw files are managed by Zotero, not by the LoreForge vault:

```text
Zotero item / attachments
  <paper PDF and other raw attachments>

LoreForge vault
  Domains/research/Spaces/papers/<citekey>.md
```

Do not copy paper PDFs, snapshots, or Zotero attachment directories into the
vault. Zotero owns paper manifest management, file storage, attachment sync,
and PDF opening. LoreForge stores only the durable paper note and Zotero
identifiers needed to reopen the paper.

The only wiki writes allowed by this workflow are Markdown paper notes under
`Domains/research/Spaces/papers/`. Notes should preserve Zotero or importer
frontmatter and then hold the durable paper analysis in the body. Use the paper
note template: Zotero metadata frontmatter followed by a `Summary` section with
problem, method, and improvement subsections, then strengths, weakness,
detailed comments, improvement ideas, and lessons learned. When creating the
first note, use `<citekey>.md` so the note is easy to scan and link.

For capture-only paper requests, update or create the paper note after the
Zotero item is resolved. If the PDF is absent, the citekey is ambiguous, or the
source is only a URL/DOI/arXiv link without a resolvable Zotero item, stop and
ask for Zotero to own the raw paper first.

Do not use `Shared/Raw/` for paper PDFs or paper notes. Do not use
`Shared/Raw/` for paper manifests or paper lifecycle metadata. `Shared/Raw/`
remains for non-paper clips, web pages, pasted text, logs, and other source
packages.

## Paper Page Shape

Use this paper note frontmatter and body shape:

```markdown
---
citekey: <citekey>
title: '<paper title>'
aliases: <short alias or list>
authors: <author list>
date: '<publication date>'
category: <research category>
keywords: []
conference: <venue>
link: <DOI/arXiv/landing page>
create_date: <Zotero note creation date>
zotero_link: <zotero://...>
zotero_folder: []
abstract: <paper abstract>
tags: []
$version: <Zotero note version>
$libraryID: <Zotero library id>
$itemKey: <Zotero item key>
---

# <paper title>

[PDF](zotero://open-pdf/...)

## Summary

### What's the problem?

### How does this paper solved it?

### What's the improvements?

## Strengths

## Weakness

## Detailed Comments

## Ideas for improvement(How Can I do better)

## Lessons learned
```

The sections should answer:

- What problem does the paper solve?
- What is the core mechanism or method?
- What assumptions and system/model context does it rely on?
- What are the main results or evaluation signals?
- What trade-offs, limits, and open questions remain?
- Which existing wiki concepts, papers, systems, or cases share a similar
  problem or solution pattern?
- How should this paper be reused later: as a method reference, cautionary
  case, evaluation baseline, related work, or project input?

Apply the `loreforge` Compiled Page Language Gate before handoff.

Do not include process narration about where the note was placed. If a
placement or routing decision matters for maintainers, report it in the final
handoff instead of writing `log.md`.

## Link And Citation Style

- Prefer inline wikilinks to wiki-local paper notes under
  `Domains/research/Spaces/papers/`, using the file stem and alias syntax when
  useful. Use source footnotes only when a multi-source paper note needs
  paragraph-level provenance disambiguation.
- Link PDFs with Zotero URIs, for example `[PDF](zotero://open-pdf/...)`.
  Never create, rewrite, relocate, or require wiki-local paper PDFs.
- Weave concepts, methods, principles, and mechanisms into prose with
  `[[wiki|readable alias]]` at the point where they are used.
- Relate the paper to existing papers, Cards, Atlas pages, and Spaces by naming
  the shared research problem or solution pattern: state movement, scheduling,
  locality, determinism, numerical reproducibility, resource allocation,
  debugging constraints, evaluation methodology, etc.
- Avoid standalone "related Cards" tables whose main purpose is bookkeeping.
  Tables are acceptable only when they carry real analysis, such as comparing
  assumptions, mechanisms, metrics, or failure modes.
- For cross-domain conceptual links, use explicit path-qualified wikilinks such
  as `[[Domains/research/Cards/simt-core-pipeline|SIMT core pipeline]]` when
  the target exists in the same wiki.

## Paper Note Handoff Prompt

Use this bounded prompt when delegating the actual paper-note update:

```text
Wiki root: <wiki-root>
Zotero item/citekey: <citekey>
Operation: paper-note
Write policy: write-confirmed
Writable paths: Markdown note files under Domains/research/Spaces/papers/ only
Read-only raw files: Zotero-managed PDFs and attachments outside the vault
Request: Compile this paper using loreforge-paper rules.

Do not create, move, rename, delete, copy, overwrite, OCR-in-place, or otherwise modify PDFs or attachment directories.
Do not write Shared/Raw/, Shared/Zotero/, manifest.md, origin.md, extracted files, paper registries, domain index.md, or domain log.md.
Read the existing paper note when present and read the Zotero-managed PDF as needed.
Use the paper note template for the body shape.
Write the paper note as durable paper knowledge, not editor narration.
Preserve existing citekey/Zotero frontmatter and only fill missing metadata from local paper evidence or Zotero metadata.
Use `[PDF](zotero://open-pdf/...)` for the PDF jump link.
Use natural `[[wiki|alias]]` links for related concepts and similar paper/problem cases.
Return: note files changed, PDF files read, validation/sync result, unresolved limits, and whether another domain needs a separate synthesis.
```

## Downstream Domain Handoff

If the user explicitly asks for Cards, Atlas views, Sources, Spaces, or
cross-domain synthesis, finish the paper-note update first and then hand off to
`loreforge-card`, `loreforge-moc`, or `loreforge-domain` as a separate write
operation. That downstream operation may write inside `Domains/<domain>/` under
its own skill contract, but it must treat Zotero-managed paper raw files as
read-only sources.

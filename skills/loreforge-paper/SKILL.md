---
name: loreforge-paper
description: Internal LoreForge workflow for paper-specific note updates and ingest. Use for arXiv, DOI, PDF, conference paper, preprint, or local paper requests when the source should resolve to an existing `Shared/Zotero/<citekey>/` paper bundle. Treats Zotero as the paper manifest/metadata system, keeps PDF access read-only, writes only paper notes in the selected citekey directory, and keeps claims, methods, evaluation, limits, related work links, and downstream domain handoff separate from ordinary single-source ingest.
user-invocable: false
version: 0.2.0
---

# LoreForge Paper

Paper ingest is a distinct workflow. Do not collapse it into generic
single-source ingest.

This skill owns the paper-specific process:

- paper note content and local paper identity resolution
- existing `Shared/Zotero/<citekey>/` bundle resolution
- read-only PDF handling
- paper note shape
- contribution, mechanism, evaluation, and limit extraction
- related paper / similar problem links
- downstream handoff guidance to `loreforge-card`, `loreforge-moc`, or
  `loreforge-domain` after the paper note is updated

It does not replace:

- `loreforge` for user-facing routing, domain selection, write gates, and sync
- `loreforge-capture` for non-paper raw package preservation
- `loreforge-card` for reusable Card updates from the paper
- `loreforge-moc` for paper-derived relationship or proposal views
- `loreforge-domain` for domain orientation, Source/Space writes, index/log updates, and schema compliance

## When To Use

Use `loreforge-paper` when the source is a research paper or should be treated
as one:

- arXiv / OpenReview / DOI / ACM / IEEE / USENIX / conference PDF
- local paper PDF or paper bundle
- a paper-like technical report with authors, methods, evaluation, and claims
- user asks to "capture paper", "ingest paper", "what did this paper solve",
  "paper contribution", "related work", or "paper notes"

For ordinary articles, blogs, docs, transcripts, reports, local notes, or web
pages, use the main `loreforge` entrypoint so it can choose
`loreforge-card`, `loreforge-moc`, or a conservative Source/Space path.

## Workflow

1. **Resolve context**
   - Use `loreforge` / `loreforge-config` to resolve wiki root and sync backend.
   - Resolve the paper to exactly one existing `Shared/Zotero/<citekey>/`
     directory using the user-provided citekey, path, title, DOI/arXiv ID,
     note frontmatter, PDF filename, or Zotero metadata already present in the
     bundle.
   - If no matching paper bundle exists, stop and ask the user to add or import
     the paper into `Shared/Zotero/<citekey>/` first. Do not create paper directories,
     move files, copy PDFs, or fall back to `Shared/Raw/`.
   - Use `Shared/Zotero/AlphaCuTransformationDrivenSynthesis2017/` as the
     concrete shape example: one raw PDF and a same-citekey Markdown note live
     in the citekey directory.
   - Inspect existing Markdown note files in the selected bundle before
     writing. Inspect target domain `SCHEMA.md`, `index.md`, recent `log.md`,
     and relevant pages only for read-only orientation or downstream handoff.

2. **Read the paper bundle**
   - Treat all PDF files in the selected paper directory as raw artifacts and
     read-only. Agents may open, convert, quote within copyright limits,
     summarize, and cite page locations from PDFs, but must not modify,
     overwrite, rename, delete, copy, compress, OCR-in-place, or relocate them.
   - Do not create, move, rename, delete, or otherwise reorganize any directory
     under `Shared/Zotero/`.
   - If extraction tooling needs scratch output, keep it outside the wiki. Do
     not write extracted text, manifests, caches, screenshots, or helper files
     into the paper directory unless they are part of a Markdown note requested
     by the user.

3. **Route**
   - Select one primary domain by paper substance and user intent.
   - List secondary domains only when they would need their own compiled
     synthesis; ask before writing multiple domains.
   - Domain routing in this skill is advisory. The paper workflow itself must
     write only paper notes under `Shared/Zotero/<citekey>/`.

4. **Write the paper note**
   - Write Markdown note files only inside the selected
     `Shared/Zotero/<citekey>/` directory. Creating `<citekey>.md` is allowed
     when the bundle has no note yet; otherwise update the existing same-citekey
     note unless the user names a different note in that directory.
   - Preserve existing frontmatter such as `citekey`, `title`, `aliases`,
     `authors`, `date`, `conference`, `link`, `zotero_link`, Zotero fields,
     tags, and library/item IDs. Fill missing fields only from the paper note,
     PDF title page, filename, DOI/arXiv metadata already available locally, or
     user-provided context.
   - Treat Zotero/exporter frontmatter and Zotero URIs as the paper manifest
     surface. Do not create, update, or backfill parallel LoreForge paper
     manifests with `source_id`, `content_hash`, `candidate_domains`,
     `compiled_pages`, or lifecycle state.
   - Do not write `manifest.md`, `origin.md`, `extracted/`, `original/`,
     `assets/`, `log.md`, domain pages, raw packages, registries, or sibling
     paper notes as part of this workflow.
   - Add broadly reusable concepts to Cards only when the concept is durable
     beyond the paper and a separate downstream domain write has been
     explicitly requested or approved. Put proposal/current-argument synthesis
     in Atlas only through that separate handoff.

5. **Validate And Sync**
   - Check that the changed paths are only Markdown files under the selected
     `Shared/Zotero/<citekey>/` directory.
   - Run the native domain validator only if a separate downstream domain write
     was explicitly performed outside this paper-note workflow.
   - Run configured post-write sync through `loreforge-config`.
   - Report the paper bundle used, note files changed, PDF files read,
     validation/sync result, and unresolved confidence limits.

## Paper Bundle Policy

Paper PDFs and notes live together in a citekey-named bundle:

```text
Shared/Zotero/<citekey>/
  <citekey> - <paper title>.pdf
  <citekey>.md
```

The directory must already exist. Do not create or rename the citekey directory
and do not move, rename, rewrite, deduplicate, or delete PDFs. The PDF is the
raw paper artifact; `loreforge-paper` may read it but must not touch it.

Zotero owns paper manifest management. The citekey directory, Zotero URI,
Zotero/exporter frontmatter, PDF filename, and optional Zotero-exported note
are the durable source record for papers. Do not mirror that state into
`Shared/Raw/<source-id>/manifest.md`, a paper registry, a raw package, or a
domain `Sources/` note just to satisfy LoreForge provenance bookkeeping.

The only wiki writes allowed by this workflow are Markdown note files inside
the selected `Shared/Zotero/<citekey>/` directory. Notes should preserve Zotero
or importer frontmatter and then hold the durable paper analysis in the body.
Use the paper note template: Zotero metadata frontmatter followed by a
`Summary` section with problem, method, and improvement subsections, then
strengths, weakness, detailed comments, improvement ideas, and lessons learned.
When creating the first note, use `<citekey>.md` so the bundle is easy to scan
and link.

For capture-only paper requests, update or create the paper note in the
existing bundle. If the PDF is absent, the citekey is ambiguous, or the source
is only a URL/DOI/arXiv link without a local bundle, stop and ask for the
bundle to be added first.

Do not use `Shared/Raw/` for paper PDFs, paper notes, paper manifests, or
paper lifecycle metadata. `Shared/Raw/` remains for non-paper clips, web pages,
pasted text, logs, and other source packages.

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

[[<citekey> - <paper title>.pdf|PDF]]

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

- Prefer inline wikilinks to wiki-local paper notes or PDFs under
  `Shared/Zotero/<citekey>/`, using the file stem and alias syntax when useful.
  Use source footnotes only when a multi-source paper note needs
  paragraph-level provenance disambiguation.
- Link PDFs only as existing artifacts, for example
  `[[Shared/Zotero/<citekey>/<pdf-file>.pdf|paper PDF]]`; never create,
  rewrite, or relocate the linked PDF.
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
  as `[[Domains/gpu-arch-research/Cards/simt-core-pipeline|SIMT core
  pipeline]]` when the target exists in the same wiki.

## Paper Note Handoff Prompt

Use this bounded prompt when delegating the actual paper-note update:

```text
Wiki root: <wiki-root>
Paper bundle: Shared/Zotero/<citekey>/
Operation: paper-note
Write policy: write-confirmed
Writable paths: Markdown note files under Shared/Zotero/<citekey>/ only
Read-only paths: every PDF and non-Markdown artifact in Shared/Zotero/<citekey>/
Request: Compile this paper using loreforge-paper rules.

Do not create, move, rename, delete, copy, overwrite, OCR-in-place, or otherwise modify directories or PDFs.
Do not write Shared/Raw/, manifest.md, origin.md, extracted files, paper registries, domain pages, index.md, or log.md.
Read the existing paper note and PDF. Use AlphaCuTransformationDrivenSynthesis2017
as the bundle-shape example when needed, and use the paper note template for
the body shape.
Write the paper note as durable paper knowledge, not editor narration.
Preserve existing citekey/Zotero frontmatter and only fill missing metadata from local paper evidence.
Use natural `[[wiki|alias]]` links for related concepts and similar paper/problem cases.
Return: note files changed, PDF files read, validation/sync result, unresolved limits, and whether another domain needs a separate synthesis.
```

## Downstream Domain Handoff

If the user explicitly asks for Cards, Atlas views, Sources, Spaces, or
cross-domain synthesis, finish the paper-note update first and then hand off to
`loreforge-card`, `loreforge-moc`, or `loreforge-domain` as a separate write
operation. That downstream operation may write inside `Domains/<domain>/` under
its own skill contract, but it must treat the paper bundle and PDFs as
read-only sources.

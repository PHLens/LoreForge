---
name: loreforge-paper
description: Internal LoreForge workflow for paper-specific capture and ingest. Use for arXiv, DOI, PDF, conference paper, preprint, or local paper requests when the desired output is a paper note, paper-derived Cards/Atlas updates, or reusable research synthesis. Keeps paper metadata, claims, methods, evaluation, limits, related work links, and domain handoff separate from ordinary single-source ingest.
user-invocable: false
version: 0.1.0
---

# LoreForge Paper

Paper ingest is a distinct workflow. Do not collapse it into generic
single-source ingest.

This skill owns the paper-specific process:

- paper identity and bibliographic metadata
- raw paper capture requirements and artifact-size policy
- paper note shape
- contribution, mechanism, evaluation, and limit extraction
- related paper / similar problem links
- handoff to `loreforge-card`, `loreforge-moc`, or `loreforge-domain` for
  bounded domain writes

It does not replace:

- `loreforge` for user-facing routing, domain selection, write gates, and sync
- `loreforge-capture` for raw package preservation
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
   - Inspect existing `Shared/Raw/` packages for the same arXiv ID, DOI, title, or PDF hash.
   - Inspect target domain `SCHEMA.md`, `index.md`, recent `log.md`, and relevant pages before writing.

2. **Capture**
   - If no raw package exists, delegate raw preservation to `loreforge-capture`.
   - Use the paper artifact policy below. A paper raw package must preserve
     bibliographic metadata, canonical URL, DOI/arXiv ID when available,
     agent-readable extracted text or structured notes, extraction method,
     content hash, and concrete limitations. It does not need to store a PDF
     binary by default.
   - Capture-only requests stop after raw package creation unless the user also asks for ingest.

3. **Route**
   - Select one primary domain by paper substance and user intent.
   - List secondary domains only when they would need their own compiled
     synthesis; ask before writing multiple domains.
   - Reuse the same raw package for every approved domain.

4. **Compile Paper Knowledge**
   - Create or update the paper page through the selected domain workflow.
     Reusable Cards go through `loreforge-card`; Atlas/MOC views go through
     `loreforge-moc`; Source/Space writes go through `loreforge-domain`.
   - Put source-specific paper notes in the page type/folder that the domain
     schema supports, commonly `Spaces/papers/` or `Sources/` when present.
     If the schema has no paper convention, prefer a source-specific Space or
     Source note and record the choice in `log.md`.
   - Add broadly reusable concepts to Cards only when the concept is durable
     beyond the paper. Put proposal/current-argument synthesis in Atlas.

5. **Validate And Sync**
   - Run the native domain validator for every written domain.
   - Run configured post-write sync through `loreforge-config`.
   - Report raw packages used, domain pages changed, validation, sync result,
     and unresolved confidence limits.

## Paper Artifact Policy

Paper capture is metadata-and-text first. Do not save every PDF into the wiki
by default; otherwise `Shared/Raw/` grows quickly and sync becomes expensive.

Required for paper raw packages:

- `manifest.md` with title, authors when available, venue/source, canonical URL,
  DOI/arXiv/OpenReview ID when available, `origin`, `content_hash`,
  `candidate_domains`, `compiled_pages`, `status`, artifacts, and limitations.
- `origin.md` with agent-readable paper text, abstract-plus-notes, or a
  structured extraction sufficient for the requested capture/ingest.
- Concrete extraction provenance: tool or method, retrieval date, source URL,
  and missing sections/figures/tables if extraction is incomplete.

Optional artifacts:

- Save `original/<paper>.pdf` only when the user explicitly asks to archive the
  PDF, the source is local/user-provided, the URL is unstable or access-gated,
  the paper is likely to disappear, figure/table fidelity is required, or
  exact page-level audit is part of the task.
- Save HTML snapshots, screenshots, or figure assets only when they materially
  improve reproducibility or later reuse.
- If a PDF is not saved, record the canonical URL and identifier in the
  manifest and list the omission in `limitations`, such as `PDF binary not
  archived; retrieve from canonical_url/arxiv_id if page-level audit is needed`.

When the user says only "capture paper" or "ingest paper", prefer the compact
policy unless they also ask to archive originals, preserve attachments, work
offline, or support exact visual/page audit.

## Paper Page Shape

A paper page should answer:

- What problem does the paper solve?
- What is the core mechanism or method?
- What assumptions and system/model context does it rely on?
- What are the main results or evaluation signals?
- What trade-offs, limits, and open questions remain?
- Which existing wiki concepts, papers, systems, or cases share a similar
  problem or solution pattern?
- How should this paper be reused later: as a method reference, cautionary
  case, evaluation baseline, related work, or project input?

Do not include editor/process narration such as:

- "this is more suitable as a paper note"
- "I am linking this to the wiki"
- "the page should live in X"
- "I did not create a Card because..."

If a placement decision matters for maintainers, put it in `log.md`, not in the
paper page body.

## Link And Citation Style

- Prefer inline wikilinks to wiki-local paper raw artifacts, manifests, or
  source notes, using the file stem and alias syntax when useful. Use source
  footnotes only when a multi-source paper page needs paragraph-level
  provenance disambiguation.
- Weave concepts, methods, principles, and mechanisms into prose with
  `[[wiki|readable alias]]` at the point where they are used.
- Relate the paper to existing papers, Cards, Atlas pages, and Spaces by naming
  the shared research problem or solution pattern: state movement, scheduling,
  locality, determinism, numerical reproducibility, resource allocation,
  debugging constraints, evaluation methodology, etc.
- Avoid standalone "related Cards" tables whose main purpose is bookkeeping.
  Tables are acceptable only when they carry real analysis, such as comparing
  assumptions, mechanisms, metrics, or failure modes.
- Prefer direct positive descriptions. Use "not X but Y" contrast only when it
  prevents a concrete misconception, and remove repeated contrastive phrasing
  before handoff.
- For cross-domain conceptual links, use explicit path-qualified wikilinks such
  as `[[Domains/gpu-arch-research/Cards/simt-core-pipeline|SIMT core
  pipeline]]` when the target exists in the same wiki.

## Domain Handoff Prompt

Use this bounded prompt when delegating the actual domain write:

```text
Use loreforge-card, loreforge-moc, or loreforge-domain as selected by the page-type decision.
Wiki root: <wiki-root>
Domain: <domain>
Operation: ingest
Write policy: write-confirmed
Paper raw package: Shared/Raw/<source-id>/
Request: Compile this paper using loreforge-paper rules.

Stay inside Domains/<domain>/ for domain pages.
Use Shared/Raw/ only for raw package metadata updates.
Orient on SCHEMA.md, index.md, recent log.md, relevant Cards/Atlas/Spaces, and the paper manifest/text.
Write the paper page as durable paper knowledge, not editor narration.
Use natural `[[wiki|alias]]` links for related concepts and similar paper/problem cases.
Update index.md only if the created/updated page is indexable by the domain schema.
Insert a newest-first log.md entry.
Return: pages changed, raw package updates, validation result, unresolved limits, and whether another domain needs a separate synthesis.
```

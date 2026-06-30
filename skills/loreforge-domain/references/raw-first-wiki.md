# Raw-First Wiki Model

## Canonical Layers

- `Sources/Raw/` is the source-of-truth layer for non-paper source packages:
  one raw source package per source under `Sources/Raw/<source-id>/`.
- `Sources/Papers/` holds Zotero-backed paper notes; Zotero owns the raw PDFs
  and paper metadata outside the vault.
- `Extras/Templates/` is the shared template layer.
- `Cards/<domain>/` holds reusable agent-maintained Cards.
- Root `Atlas/` holds human-facing MOC/view pages.
- Root `Spaces/` holds durable projects, people, tools, systems, and contexts.
- Root `Sources/` is optional outside `Raw/` and `Papers/` for source excerpts
  or source-specific lenses.
- `Calendar/dailynotes/` stays as dated personal notes and daily logs.

## Raw Package Shape

Capture derives a stable source ID and writes a folder such as
`Sources/Raw/<source-id>/` with:

- `origin.md` for the faithful clip/transcription
- `manifest.md` with:
  - title
  - canonical URL or source description
  - retrieval date
  - source hash
  - source type / extractor
  - compiled page pointers
  - links to original and extracted artifacts

Use `content_hash` or an equivalent hash field to decide whether the raw package
changed and whether downstream pages need recompilation.

## Batch Routing Rule

Multiple raw packages can be captured first and ingested incrementally later. A
main entrypoint or caller may group packages by candidate domain and fan out domain ingest
passes up to a requested max concurrency. Domain experts still own raw
normalization and bounded page writes, while centralized policy and validators
replace routine per-domain index/log edits.

## Ingest Rule

Start from the user's question or uncertainty, not from mechanical source
decomposition. Capture or refresh the raw package, inspect existing pages during
ingest, and then compile only the reusable conclusions that
reduce future work.

## Compilation Rule

Create or update Cards, Atlas pages, Spaces, and optional Source notes only
when the result will be reused. Compiled pages use plain internal wikilinks for
Card-to-Card concepts and path-qualified wikilinks for wiki-local raw
artifacts, raw manifests, paper notes, or source notes. Use source footnotes
only when paragraph-level provenance would otherwise be ambiguous. Do not use
YAML source links.

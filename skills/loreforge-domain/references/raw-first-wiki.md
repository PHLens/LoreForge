# Raw-First Wiki Model

## Canonical Layers

- `Shared/Raw/` is the source-of-truth layer: one raw source package per source
  under `Shared/Raw/<source-id>/`.
- `Shared/Templates/` is the shared template layer.
- `Domains/<domain>/Atlas/`, `Cards/`, and `Spaces/` hold compiled durable knowledge.
- `Domains/<domain>/Sources/` is optional and can hold source excerpts or source-specific lenses.
- `Calendar/dailynotes/` stays as dated personal notes and daily logs.

## Raw Package Shape

Capture derives a stable source ID and writes a folder such as
`Shared/Raw/<source-id>/` with:

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
normalization, page writes, index updates, and log entries for their domains.

## Ingest Rule

Start from the user's question or uncertainty, not from mechanical source
decomposition. Capture or refresh the raw package, inspect existing pages during
ingest, and then compile only the reusable conclusions that
reduce future work.

## Compilation Rule

Create or update Cards, Atlas pages, Spaces, and optional Source notes only when the result will be reused. Compiled pages prefer plain internal wikilinks to wiki-local raw artifacts, raw manifests, or source notes; use source footnotes only when paragraph-level provenance would otherwise be ambiguous. Do not use YAML source links.

# Raw-First Wiki Model

## Canonical Layers

- `Shared/Raw/` is the source-of-truth layer: flat raw clips before ingest and
  normalized `Shared/Raw/<source-id>/` packages after ingest.
- `Shared/Templates/` is the shared template layer.
- `Domains/<domain>/Atlas/`, `Cards/`, and `Spaces/` hold compiled durable knowledge.
- `Domains/<domain>/Sources/` is optional and can hold source excerpts or source-specific lenses.
- `Calendar/dailynotes/` stays as dated personal notes and daily logs.

## Raw Package Shape

Capture may leave flat raw clip files directly under `Shared/Raw/`. During
ingest, derive a stable source ID and normalize each selected clip into a
folder such as `Shared/Raw/<source-id>/` by adding:

- `origin.md` for the faithful clip/transcription
- `manifest.md` with:
  - title
  - canonical URL or source description
  - retrieval date
  - source hash
  - source type / extractor
  - compiled page pointers
  - links to original and extracted artifacts

Use `content_hash` or an equivalent hash field to decide whether the normalized
raw package changed and whether downstream pages need recompilation.

## Batch Routing Rule

Multiple raw clips can be captured first and ingested incrementally later. A
router or caller may group clips by candidate domain and fan out domain ingest
passes up to a requested max concurrency. Domain experts still own raw
normalization, page writes, index updates, and log entries for their domains.

## Ingest Rule

Start from the user's question or uncertainty, not from mechanical source
decomposition. Capture or refresh the raw clip, normalize it during ingest,
inspect existing pages, and then compile only the reusable conclusions that
reduce future work.

## Compilation Rule

Create or update Cards, Atlas pages, Spaces, and optional Source notes only when the result will be reused. Compiled pages cite raw manifests or source notes with body footnotes, not YAML source links.

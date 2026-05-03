# Raw-First Wiki Model

## Canonical Layers

- `Shared/Raw/<source-id>/` is the source-of-truth layer.
- `Shared/Templates/` is the shared template layer.
- `Domains/<domain>/Atlas/`, `Cards/`, and `Spaces/` hold compiled durable knowledge.
- `Calendar/dailynotes/` stays as dated personal notes and daily logs.

## Raw Package Shape

Each raw package should use a stable folder such as `Shared/Raw/<source-id>/` and include a `manifest.md` with:

- title
- canonical URL or source description
- retrieval date
- source hash
- source type / extractor
- compiled page pointers
- links to original and extracted artifacts

Use `content_hash` or an equivalent hash field to decide whether the raw package changed and whether downstream pages need recompilation.

## Ingest Rule

Start from the user's question or uncertainty, not from mechanical source decomposition. Capture or refresh the raw package, inspect existing pages, and then compile only the reusable conclusions that reduce future work.

## Compilation Rule

Create or update Cards, Atlas pages, and Spaces only when the result will be reused. Compiled pages cite raw manifests with body footnotes, not YAML source links.

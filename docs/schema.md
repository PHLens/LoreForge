# Schema

LoreForge wiki instances follow a layered structure.

## Layers

| Layer | Purpose |
|---|---|
| `sources` | Source-grounded notes and provenance |
| `cards` | Compiled atomic knowledge |
| `maps` | Navigation and synthesis |
| `system` | Schema, task views, indexes, promotion log, policies |

## Default Template

Use `templates/wiki/` as the generic starting point for a new wiki instance.

Adapter-specific templates may exist under `adapters/`.

## Discovery Files

LoreForge uses two discovery layers:

| File | Scope | Purpose |
|---|---|---|
| `~/.config/loreforge/registry.toml` | machine-local | Lists wiki instances, local paths, remotes, and defaults |
| `<wiki>/.loreforge/wiki.toml` | wiki-local | Describes the wiki schema, entry files, task views, and path conventions |

Agents should never guess wiki paths when a registry is available.

## Stable Promotion

Stable wiki writes should go through the `promote` skill.

Promotion is the transaction that:

1. creates or moves reviewed staged notes into stable locations
2. updates the target domain `+Wiki Index.md`
3. archives consumed staging material
4. appends one entry to `00_System/Wiki Log.md`

Do not index captures or staged packages. Do not log ordinary queries, ordinary captures, read-only lint with no meaningful findings, or git sync.

Processed `ingest` and `writeback` outputs should use a staged package with `manifest.md`. A package can contain multiple candidate notes when they came from the same source or conversation.

The wiki log is broader than promotion history: it may record substantive staged package creation and lint passes with meaningful findings, but should not record ordinary queries, ordinary captures, or sync operations.

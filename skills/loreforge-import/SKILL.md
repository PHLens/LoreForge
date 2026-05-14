---
name: loreforge-import
description: Internal LoreForge workflow for treating existing repos, Obsidian vaults, folders, and exports as source material and importing useful knowledge into native LoreForge domains.
user-invocable: false
version: 0.2.0
---

# LoreForge Import

Import useful material from an existing repo, vault, folder, or export without
adopting its layout as LoreForge structure.

Always:

- treat the source as read-only unless the user explicitly asks to convert in
  place
- resolve source aliases from `~/.config/loreforge/registry.toml`
- capture raw material into `Shared/Raw/` first
- use `loreforge` to select target domains
- use `loreforge-domain` domain experts for durable domain synthesis

## Workflow

1. Resolve the source path:
   - path named by the user, or
   - `[[sources]]` alias from the registry.
2. Resolve the target wiki with `loreforge-config`.
3. Inspect the source structure enough to identify candidate material.
4. Capture source material into `Shared/Raw/<source-id>/` raw packages.
5. Route captured packages by candidate domain.
6. Delegate each domain ingest to `loreforge-domain`.
7. Ensure each domain expert:
   - updates `Shared/Raw/<source-id>/origin.md` and `manifest.md`
   - writes optional domain `Sources/` excerpts only when useful
   - updates `Cards/`, `Atlas/`, `Spaces/`, `index.md`, and `log.md`

## Boundaries

Do not preserve alternate long-term layouts inside the LoreForge wiki. Do not
copy `.obsidian*`, build artifacts, caches, dependency folders, or editor state
as knowledge.

If the user asks to convert a source repo in place, state that this changes the
repo structure and get explicit confirmation before writing.

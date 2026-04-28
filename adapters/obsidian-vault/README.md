# Obsidian Vault Adapter

This adapter contains Obsidian-specific LoreForge conventions.

The framework core is type-first. This adapter preserves the existing `MOCs/Scope/` workflow by configuring adapter-specific index and log paths through `.loreforge/wiki.toml`.

## Contents

```text
template/   Obsidian vault files using MOCs/Scope conventions
```

Use this adapter when the target wiki instance is an Obsidian vault that expects files such as:

- `CLAUDE.md`
- `AGENTS.md`
- `MOCs/Scope/+Wiki Index.md`
- `MOCs/Scope/+Wiki Log.md`

The adapter config sets:

```toml
index_file = "MOCs/Scope/+Wiki Index.md"
log_file = "MOCs/Scope/+Wiki Log.md"
```

`Spaces/` may exist in a concrete Obsidian vault as a human workspace, but it is outside the LoreForge stable promotion contract.

Core operation skills live in the repository root `skills/` directory. If a core skill needs Obsidian-specific behavior, document that convention here instead of moving the whole skill into the adapter.

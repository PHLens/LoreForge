# Obsidian Vault Adapter

This adapter contains the first Obsidian-oriented LoreForge draft.

It is adapter-specific and should not define the framework core.

## Contents

```text
template/   Obsidian vault files using MOCs/Scope conventions
```

Use this adapter when the target wiki instance is an Obsidian vault that expects files such as:

- `CLAUDE.md`
- `AGENTS.md`
- `MOCs/Scope/+Wiki Index.md`
- `MOCs/Scope/+Wiki Log.md`

Core operation skills live in the repository root `skills/` directory. If a core skill needs Obsidian-specific behavior, document that convention here instead of moving the whole skill into the adapter.

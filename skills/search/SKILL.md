---
name: search
description: Use for lightweight filesystem and Markdown search over configured LoreForge binding read roots.
user-invocable: true
---

# Search Binding

Search is available for generic and native bindings.

## Trigger

Use for:

- `search binding`
- `search repo`
- `find in notes`
- lightweight lookup before ingest or writeback

## Discovery

1. Read `~/.config/loreforge/registry.toml`.
2. Resolve the named binding or the registry `default`.
3. Read `target_repo` and `read_roots`.
4. Search only inside configured read roots.

## Execution

Use `rg` first:

```bash
rg -n "<query>" <target_repo>/<read_root>
```

If `rg` is unavailable, use the fastest available local search command.

## Boundary

Search does not promise native query semantics. It does not require indexes, MOCs, source provenance, or native views.

For structured native retrieval, use `query` on a binding with `mode = "native"`.

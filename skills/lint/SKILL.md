---
name: lint
description: Use for LoreForge protocol lint on bindings and runtime packages, or explicit native lint on native repository structure.
user-invocable: true
---

# Lint Binding

Read-only health checks. No files are modified.

Protocol lint is the default for all bindings. Native lint is explicit and applies only to native bindings.

## Trigger

`lint`, `lint protocol`, `lint native`, `健康检查`

## Discovery

For protocol lint, resolve the binding through `~/.config/loreforge/registry.toml`. If no binding is named, use the registry `default`.

For native lint, run against the selected binding's `target_repo` or an explicit target repository path.

## Execution

Protocol lint is the default:

```bash
bash <skill-path>/lint/scripts/lint-protocol.sh [--registry <path>] [binding]
```

Native lint is explicit:

```bash
bash <skill-path>/lint/scripts/lint-native.sh <target_repo>
```

## Protocol Check Items

Protocol lint checks:

- registry syntax and binding resolution
- target repository existence
- runtime state readability and writability
- configured target path existence or creatability
- read root validity
- staged package manifest validity
- output target validity
- path traversal prevention
- writeback conflict detectability
- lock, cache, and report directory health

Protocol lint does not require native repository structure.

## Native Check Items

Native lint runs only for native bindings. It checks:

- native index, log, and views
- native template structure
- card, source, and MOC conventions
- provenance and index drift
- native package promotion rules

## Output

Return a structured report in chat: counts plus examples per check item. No file writes.

## Boundary

This skill must not append logs, update indexes, reformat notes, commit, or push. If the user wants fixes, report a proposed patch plan first.

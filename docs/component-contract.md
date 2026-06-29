# LoreForge Component Contract

This document defines the read-only surface external orchestrators can use to
inspect LoreForge readiness. Noesis may call this surface from `doctor` without
owning LoreForge config or wiki files.

## Ownership

LoreForge owns:

- `~/.config/loreforge/registry.toml`
- LoreForge wiki roots listed in that registry
- `Calendar/`, `Shared/`, and `Domains/` inside a wiki root
- domain validation through the shared Python `loreforge_validator` module
- sync helpers such as `skills/loreforge-domain/scripts/sync_rclone.sh`

Noesis or another orchestrator may own its own control-plane manifest, but
should not write `.loreforge/`, `~/.config/loreforge/`, or wiki contents during
doctor/status checks.

## Commands

The stable read-only CLI is:

```bash
loreforge <operation> --json
```

Operations:

- `status`: report registry availability, selected wiki, sync backend, and
  discovered domains.
- `validate`: run the shared validator for one domain or all
  domains.
- `init`: return an init plan and registry entry shape. This operation is
  intentionally proposal-only; it does not write files.
- `setup`: write the machine-local registry entry plus minimal wiki/domain
  skeleton for an external bootstrapper. This operation is a LoreForge-owned
  bootstrap path; it does not run capture, ingest, rclone sync, or git sync.

Examples:

```bash
loreforge status --wiki-name main --json
loreforge validate --wiki /path/to/wiki --domain ai-research --json
loreforge validate --wiki /path/to/wiki --all-domains --json
loreforge init --wiki /path/to/wiki --domain ai-research --sync rclone --remote wiki-webdav:LoreForgeWiki --json
loreforge setup --wiki /path/to/wiki --domain ai-research --sync local --json
```

The CLI is the external contract. Its current implementation delegates through a
Python component adapter under `skills/loreforge-domain/scripts/`, which imports
the shared `loreforge_validator` module; callers should not depend on either
internal path.

## JSON Shape

All operations return a JSON envelope:

```json
{
  "component": "loreforge",
  "contract_version": "0.1",
  "operation": "status",
  "ok": true,
  "issues": []
}
```

Issues use:

```json
{
  "code": "missing-wiki-root",
  "severity": "error",
  "path": "/path/to/wiki",
  "message": "selected wiki path does not exist"
}
```

`status` may include:

```json
{
  "registry": {
    "path": "~/.config/loreforge/registry.toml",
    "exists": true
  },
  "selected_wiki": {
    "name": "main",
    "path": "/path/to/wiki",
    "exists": true,
    "sync": "rclone",
    "remote": "wiki-webdav:LoreForgeWiki",
    "sync_bootstrapped": true,
    "default_domain": "ai-research",
    "domains": ["ai-research"]
  }
}
```

`validate` includes a `domains` array. Each domain has `name`, `path`, `ok`,
and validator `issues`.

`init` includes `writes: false`, an intended `registry_entry`, and an `actions`
plan. It remains the read-only planning surface.

`setup` includes `selected_wiki`, `domain`, `writes`, `preserved`, `sync`, and
`validation`. `writes` lists files/directories created or registry entries
updated. `sync.executed` is always `false` in the current contract; callers must
not assume rclone or git propagation ran.

## Doctor Semantics

Noesis doctor can treat this contract as follows:

- `status --json` is a read-only availability check.
- `validate --json` is a read-only health check for wiki/domain contents.
- `init --json` is a planning surface only. A non-LoreForge caller should use
  the returned plan to explain what needs to happen, then delegate real writes
  to LoreForge.
- `setup --json` is the write-capable bootstrap surface for external tools that
  have explicit user intent to initialize a LoreForge wiki/domain.
- Exit code `0` means `ok: true`; exit code `1` means at least one error issue.
- The read-only adapter never runs rclone pull/push, writes registry files,
  creates wiki folders, or fixes validator issues. The `setup` command can
  write registry/wiki/domain bootstrap files but still does not run sync,
  capture, ingest, or validator repairs.

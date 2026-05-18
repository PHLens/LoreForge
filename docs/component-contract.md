# LoreForge Component Contract

This document defines the read-only surface external orchestrators can use to
inspect LoreForge readiness. Noesis may call this surface from `doctor` without
owning LoreForge config or wiki files.

## Ownership

LoreForge owns:

- `~/.config/loreforge/registry.toml`
- LoreForge wiki roots listed in that registry
- `Calendar/`, `Shared/`, and `Domains/` inside a wiki root
- domain validation through `skills/loreforge-domain/scripts/validate_native_domain.py`
- sync helpers such as `skills/loreforge-domain/scripts/sync_rclone.sh`

Noesis or another orchestrator may own its own control-plane manifest, but
should not write `.loreforge/`, `~/.config/loreforge/`, or wiki contents during
doctor/status checks.

## Commands

The stable read-only adapter is:

```bash
python3 skills/loreforge-domain/scripts/loreforge_component.py <operation> --json
```

Operations:

- `status`: report registry availability, selected wiki, sync backend, and
  discovered domains.
- `validate`: run the existing native-domain validator for one domain or all
  domains.
- `init`: return an init plan and registry entry shape. This operation is
  intentionally proposal-only; it does not write files.

Examples:

```bash
python3 skills/loreforge-domain/scripts/loreforge_component.py status --wiki-name main --json
python3 skills/loreforge-domain/scripts/loreforge_component.py validate --wiki /path/to/wiki --domain ai-research --json
python3 skills/loreforge-domain/scripts/loreforge_component.py validate --wiki /path/to/wiki --all-domains --json
python3 skills/loreforge-domain/scripts/loreforge_component.py init --wiki /path/to/wiki --domain ai-research --sync rclone --remote wiki-webdav:LoreForgeWiki --json
```

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
plan. The actual LoreForge initialization flow remains owned by the LoreForge
skills and must handle user confirmation, wiki writes, and sync setup.

## Doctor Semantics

Noesis doctor can treat this contract as follows:

- `status --json` is a read-only availability check.
- `validate --json` is a read-only health check for wiki/domain contents.
- `init --json` is a planning surface only. A non-LoreForge caller should use
  the returned plan to explain what needs to happen, then delegate real writes
  to LoreForge.
- Exit code `0` means `ok: true`; exit code `1` means at least one error issue.
- The adapter never runs rclone pull/push, writes registry files, creates wiki
  folders, or fixes validator issues.

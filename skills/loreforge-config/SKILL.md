---
name: loreforge-config
description: Internal LoreForge workflow for resolving wiki location, initializing config, choosing sync backends, and running post-write sync. Use when LoreForge needs init/config/registry/sync handling before or after wiki edits.
user-invocable: false
version: 0.2.0
---

# LoreForge Config

Resolve where LoreForge should write and how durable wiki edits should sync.
This is an internal workflow used by the LoreForge main entrypoint and domain experts.

Always:

- keep config machine-local
- treat `~/.config/loreforge/registry.toml` as discovery/sync config only
- never store notes, summaries, user preferences, task state, or agent memory in
  the registry
- run the configured post-write sync after agent-owned wiki edits

## Resolve Wiki And Domain

Use this discovery order for the wiki root:

1. User-provided wiki path.
2. `WIKI_PATH`.
3. `WIKI_NAME` lookup in `~/.config/loreforge/registry.toml`.
4. Registry `default` wiki.
5. `~/wiki`, but tell the user before writing there.

Use this discovery order for the domain:

1. User-provided domain.
2. `DOMAIN_NAME`.
3. Selected registry wiki's `default_domain`.
4. If multiple domains exist and the caller is about to write, ask or return
   control to the main entrypoint for domain selection.

Registry example:

```toml
default = "main"

[[wikis]]
name = "main"
path = "/path/to/loreforge-wiki"
description = "Personal LoreForge wiki"
sync = "local" # local | webdav | git | scp
default_domain = "ai-research"
remote = ""
sync_bootstrapped = false

[[sources]]
name = "old-obsidian"
kind = "obsidian-vault"
path = "/path/to/source-vault"
default_target_wiki = "main"
default_target_domain = "ai-research"
```

`[[wikis]]` entries are writable LoreForge wiki roots. `[[sources]]` entries are
read-only aliases for repeated imports from existing repos, vaults, or
folders.

## Initialize Config

When creating a new wiki or adding sync to an existing wiki:

1. Ask for or infer the backend: `webdav`, `git`, `scp`, or explicit `local`.
2. For `webdav`, require an `rclone` `remote:path` target and whether bootstrap
   sync has already run.
3. For `git`, require or discover the remote repo URL.
4. For `scp`, require an `scp` target such as `user@host:/path/to/wiki` and
   confirm the remote path is a publish/backup target that local writes may
   overwrite.
5. For `local`, warn that no remote sync protects the wiki.
6. Write or update the machine-local registry entry.

Do not require example paths to be real. Keep docs and examples generic.

## Post-Write Sync

After any agent-owned wiki edit:

- `webdav`: run `skills/loreforge-domain/scripts/sync_webdav.sh` with the wiki
  path and configured `remote:path`. Use bootstrap/resync mode only when the
  local copy should win on the first sync.
- `git`: run `git add`, make a focused commit in the wiki repo, and push.
- `scp`: run `skills/loreforge-domain/scripts/sync_scp.sh` with the wiki path
  and configured `user@host:/path` target. This is a one-way local-to-remote
  publish flow; it does not merge remote-only edits.
- `local`: report that the wiki remains local-only, no remote sync ran, and
  repeat the data-loss warning.

If sync fails, report the failure and leave the local edits intact.

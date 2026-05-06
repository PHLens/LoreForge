# Configuration

LoreForge can use explicit paths, environment variables, or local config files.
The core `loreforge-wiki` skill should prefer a user-provided domain path, then
`WIKI_PATH`, then `~/wiki`.

For LoreForge instances that use `~/wiki` as the local working copy and sync
through Nutstore/WebDAV, keep the local checkout in that default directory and
follow the configured sync command. The first sync on a fresh machine may
require a different bootstrap or resync command than the normal steady-state
sync.

## Local Registry

Path:

```text
~/.config/loreforge/registry.toml
```

Purpose:

- machine-local discovery
- maps wiki names to local paths
- records optional sync backend hints
- defines a default wiki

Template:

```text
templates/config/registry.toml
```

Example:

```toml
default = "cs"

[[wikis]]
name = "cs"
path = "/home/phlens/wiki"
description = "Computer science, GPU, ML systems, PyTorch"
sync = "webdav"
remote = "nustore:LoreForgeWiki"
default_domain = "investment"
sync_bootstrapped = true
```

The registry is not a knowledge store. Do not put notes, findings, summaries, or agent memory in it.

Fields:

- `sync`: one of `webdav`, `git`, or `local`.
- `remote`: for `webdav`, an `rclone` `remote:path`; for `git`, a repo URL;
  for `local`, leave empty.
- `default_domain`: optional default domain when a user names only the wiki.
- `sync_bootstrapped`: machine-local flag that says the first sync/bootstrap
  step has already been handled on this machine.

## Discovery Flow

1. Use the user-provided wiki/domain path, if given.
2. Otherwise use `WIKI_PATH` and the requested domain name.
3. Otherwise read `~/.config/loreforge/registry.toml`, if available.
4. Otherwise fall back to `~/wiki`.
5. Enter `Domains/<domain>/`.
6. Orient on `SCHEMA.md`, `index.md`, recent `log.md`, and relevant pages.

Wiki-local metadata files are optional. The active core workflow is defined by
the selected domain's files, not by a copied template.

## Sync Backend Setup

Every new wiki initialization should confirm a sync backend before the first
durable write. Existing wikis can add or change sync behavior later by updating
the registry entry and, when available, a wiki-local config file such as
`00_System/loreforge.toml`.

Preferred mode:

```text
Remote backend -> local clone -> local read/search/write -> documented sync
```

Agents should not query GitHub directly for every answer.

Supported backends:

- `webdav`: user configures `rclone config`, then provides an `rclone`
  `remote:path`, for example `nustore:LoreForgeWiki`. The first sync on a new
  machine may need a bootstrap or `--resync` flow; normal repeat sync should use
  the recorded `rclone bisync` command.
- `git`: user provides a remote repo URL. Initialize or clone the wiki as a git
  working copy, set the remote, then run `git add`, `git commit`, and `git push`
  after wiki edits.
- `local`: no remote sync. This is allowed only after warning the user that the
  wiki is not linked to remote persistence and local machine loss can lose data.

Wiki-local config example:

```toml
[sync]
backend = "webdav"
remote = "nustore:LoreForgeWiki"
sync_bootstrapped = true
```

For `git`, `remote` is the repo URL. For `local`, `remote` is empty and
`sync_bootstrapped` should be `false`.

Exact WebDAV commands:

```bash
# steady-state sync
rclone bisync ~/wiki nustore:LoreForgeWiki \
  --create-empty-src-dirs --resilient --recover --max-lock 2m \
  --size-only --conflict-resolve path1 --conflict-loser delete \
  -P -v

# first sync or resync when the local copy should win
rclone bisync ~/wiki nustore:LoreForgeWiki \
  --create-empty-src-dirs --resilient --recover --max-lock 2m \
  --size-only --conflict-resolve path1 --conflict-loser delete \
  --resync -P -v
```

## Post-Write Sync Contract

After any agent-owned wiki edit, run the configured backend flow before
reporting completion:

- `webdav`: run the documented `rclone bisync` command for the wiki path and
  configured `remote:path`. If `sync_bootstrapped` is false, use the `--resync`
  form above after confirming the local wiki should win the first bootstrap.
- `git`: run `git add`, create a focused commit, and push to the configured
  remote.
- `local`: do not run sync; report that the wiki remains local-only and repeat
  the data-loss warning.

When adding sync to an existing wiki, update config first, run or confirm the
backend's first sync, then return to the normal post-write flow for future
changes.

## Registration

Create or update registry entries manually until a smaller domain-management
helper is justified.

First-time manual setup:

```bash
mkdir -p ~/.config/loreforge
cp templates/config/registry.toml ~/.config/loreforge/registry.toml
```

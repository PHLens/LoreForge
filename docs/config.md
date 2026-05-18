# Configuration

LoreForge can use explicit paths, environment variables, or local config files.
The main entrypoint and `loreforge-config` should prefer a user-provided wiki path,
then `WIKI_PATH`, then `~/wiki`.

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

- `sync`: one of `webdav`, `git`, `scp`, or `local`.
- `remote`: for `webdav`, an `rclone` `remote:path`; for `git`, a repo URL;
  for `scp`, a `user@host:/path/to/wiki` target; for `local`, leave empty.
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
the machine-local registry entry for that machine.

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
- `scp`: user provides a remote target such as `user@example.com:/srv/wiki`.
  The helper creates the remote directory if needed and copies the local wiki
  contents there. This is one-way local-to-remote publishing and does not merge
  remote-only edits.
- `local`: no remote sync. This is allowed only after warning the user that the
  wiki is not linked to remote persistence and local machine loss can lose data.

For `git`, `remote` is the repo URL. For `scp`, `remote` is the SCP target.
For `local`, `remote` is empty and `sync_bootstrapped` should be `false`.

WebDAV command helper:

```bash
bash skills/loreforge-domain/scripts/sync_webdav.sh --wiki ~/wiki --remote nustore:LoreForgeWiki
bash skills/loreforge-domain/scripts/sync_webdav.sh --wiki ~/wiki --remote nustore:LoreForgeWiki --resync
```

The helper owns the exact `rclone bisync` argv. Use the first form for normal
steady-state sync and the second form for first sync or recovery when the local
wiki should win.

SCP command helper:

```bash
bash skills/loreforge-domain/scripts/sync_scp.sh --wiki ~/wiki --remote user@example.com:/srv/wiki
```

The helper owns the exact `ssh` and `scp` argv. Use this only when the remote
path is a backup or publish target for the local wiki.

## Post-Write Sync Contract

After any agent-owned wiki edit, run the configured backend flow before
reporting completion:

- `webdav`: run `skills/loreforge-domain/scripts/sync_webdav.sh` for the wiki
  path and configured `remote:path`. If `sync_bootstrapped` is false, use the
  helper's bootstrap/resync mode after confirming the local wiki should win the
  first bootstrap.
- `git`: run `git add`, create a focused commit, and push to the configured
  remote.
- `scp`: run `skills/loreforge-domain/scripts/sync_scp.sh` for the wiki path
  and configured `user@host:/path` target.
- `local`: do not run sync; report that the wiki remains local-only and repeat
  the data-loss warning.

When adding sync to an existing wiki, update config first, run or confirm the
backend's first sync, then return to the normal post-write flow for future
changes.

## Registration

Create or update registry entries through `loreforge-config`.

First-time manual setup:

```bash
mkdir -p ~/.config/loreforge
cp templates/config/registry.toml ~/.config/loreforge/registry.toml
```

# Configuration

LoreForge can use explicit paths, environment variables, or local config files.
The main entrypoint and `loreforge-config` should prefer a user-provided wiki path,
then `WIKI_PATH`, then `~/wiki`.

For LoreForge instances that use `~/wiki` as the local working copy and sync
through rclone, keep the local checkout in that default directory and follow
the configured sync command. The first sync on a fresh machine may require a
bootstrap command only after confirming the local wiki should seed the remote.

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
sync = "rclone"
remote = "wiki-webdav:LoreForgeWiki"
default_domain = "investment"
sync_bootstrapped = true
```

The registry is not a knowledge store. Do not put notes, findings, summaries, or agent memory in it.

Fields:

- `sync`: one of `rclone`, `git`, or `local`.
- `remote`: for `rclone`, an `rclone` `remote:path`; for `git`, a repo URL;
  for `local`, leave empty.
- `default_domain`: optional default domain when a user names only the wiki.
- `sync_bootstrapped`: machine-local flag that says the first sync/bootstrap
  step has already been handled on this machine.

## Discovery Flow

1. Use the user-provided wiki/domain path, if given.
2. Otherwise use `WIKI_PATH` and the requested domain name.
3. Otherwise read `~/.config/loreforge/registry.toml`, if available.
4. Otherwise fall back to `~/wiki`.
5. Enter `Cards/<domain>/` when a Card domain is selected.
6. Orient on `00_System/card-domains.md`, `00_System/card-policy.md`,
   `00_System/agent-policy.md`, optional `00_System/card-index.json`, and
   relevant Cards, Atlas views, Sources, and Spaces.

Wiki-local metadata files are optional except for the core `00_System/`
policies created by setup. The active core workflow is defined by centralized
policy plus selected Markdown pages, not by copied per-domain templates.

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

- `rclone`: user configures `rclone config`, then provides an `rclone`
  `remote:path`, for example `wiki-webdav:LoreForgeWiki` or
  `wiki-sftp:LoreForgeWiki`. Normal reads and writes are remote-first: pull the
  remote before editing, then push local edits back. The first sync on a new
  machine may need an explicit bootstrap flow after confirming the local wiki
  should seed the remote.
- `git`: user provides a remote repo URL. Initialize or clone the wiki as a git
  working copy, set the remote, then run `git add`, `git commit`, and `git push`
  after wiki edits.
- `local`: no remote sync. This is allowed only after warning the user that the
  wiki is not linked to remote persistence and local machine loss can lose data.

For `git`, `remote` is the repo URL. For `rclone`, `remote` is the rclone target.
For `local`, `remote` is empty and `sync_bootstrapped` should be `false`.

rclone command helper:

```bash
bash skills/loreforge-domain/scripts/sync_rclone.sh --wiki ~/wiki --remote wiki-webdav:LoreForgeWiki --mode pull
bash skills/loreforge-domain/scripts/sync_rclone.sh --wiki ~/wiki --remote wiki-webdav:LoreForgeWiki --mode push
bash skills/loreforge-domain/scripts/sync_rclone.sh --wiki ~/wiki --remote wiki-sftp:LoreForgeWiki --mode bootstrap
```

The helper owns the exact `rclone sync` argv. Use `--mode pull` before reading
or editing a rclone-backed wiki, `--mode push` after successful local edits, and
`--mode bootstrap` only for first sync or recovery after confirming the local
wiki should seed the remote.

## Post-Write Sync Contract

After any agent-owned wiki edit, run the configured backend flow before
reporting completion:

- `rclone`: run `skills/loreforge-domain/scripts/sync_rclone.sh` for the wiki
  path and configured `remote:path` with `--mode pull` before editing and
  `--mode push` after editing. If `sync_bootstrapped` is false, use
  `--mode bootstrap` only after confirming the local wiki should seed the
  remote.
- `git`: run `git add`, create a focused commit, and push to the configured
  remote.
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

External bootstrapper setup:

```bash
loreforge setup --wiki /path/to/wiki --domain ai-research --sync local --json
```

`loreforge setup` creates or updates the machine-local registry entry and
minimal wiki/domain skeleton. It is the write-capable component CLI for setup
flows such as Noesis umbrella bootstrap. It does not run rclone or git sync;
those remain explicit post-setup actions.

## External Doctor Surface

External orchestrators should use the read-only component adapter for
availability and validation checks:

```bash
loreforge status --json
loreforge validate --wiki /path/to/wiki --all-domains --json
```

See `docs/component-contract.md` for the full JSON contract. This adapter does
not write config, modify wiki files, run sync, or fix validation issues.

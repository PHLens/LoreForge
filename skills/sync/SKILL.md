---
name: sync
description: Use when syncing a LoreForge wiki clone with Git: inspect status, pull safely, review diffs, commit approved wiki changes, or push to the configured remote.
user-invocable: true
---

# Sync LoreForge Wiki

Synchronize a LoreForge wiki instance with its configured Git remote.

## Purpose

GitHub or another Git remote is the persistence and cross-machine sync backend.

Agents operate on local clones. This skill helps locate the clone, inspect state, pull safely, and prepare commits or pushes when approved.

## Hard Boundary

This skill must not:

- use GitHub as the query backend
- commit without showing the diff
- push without explicit approval
- merge with conflicts automatically
- rewrite history
- run destructive cleanup
- sync agent-local `pamem` memory

It may:

- locate a wiki via the LoreForge registry
- clone a configured remote when the local path is missing and the user approves
- run `git status`
- run `git pull --ff-only`
- show diffs after local changes
- create a commit when the user approves
- push when the user approves

## Discovery

Default registry:

```text
~/.config/loreforge/registry.toml
```

Wiki metadata:

```text
<wiki>/.loreforge/wiki.toml
```

Use the registry entry named by the user. If no wiki is named, use the registry default.

## Workflow

### 1. Locate Wiki

1. Read `~/.config/loreforge/registry.toml`.
2. Resolve the target wiki.
3. Check the configured local `path`.
4. If the path is missing and `remote` exists, ask before cloning.

### 2. Inspect State

Inside the local wiki clone:

```bash
git status --short
git branch --show-current
git remote -v
```

Report:

- current branch
- remote URL
- clean or dirty state
- untracked files

### 3. Pull Safely

If the worktree is clean, pull with:

```bash
git pull --ff-only
```

If the worktree is dirty, do not pull automatically. Ask whether to inspect, commit, stash, or skip.

### 4. Commit Local Changes

Before committing:

```bash
git diff --stat
git diff
```

Summarize changed files and ask for approval.

If approved:

```bash
git add <approved files>
git commit -m "<message>"
```

Use a concise message such as:

```text
docs: update wiki knowledge
```

### 5. Push

Before pushing:

```bash
git status -sb
```

Push only after explicit approval:

```bash
git push
```

## Conflict Handling

If `git pull --ff-only` fails:

- stop
- report the error
- do not merge automatically
- ask for user direction

If a push is rejected:

- stop
- report that the remote has new commits
- recommend pulling with conflict review

## Output

Always report:

- wiki name and path
- branch and remote
- clean/dirty state
- whether pull/commit/push happened
- any required user decision

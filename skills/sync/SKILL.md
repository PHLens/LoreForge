---
name: sync
description: Use when syncing a LoreForge binding target_repo with Git: inspect status, pull safely, review diffs, commit approved target changes, or push.
user-invocable: true
---

# Sync Target Repo

Sync operates on `target_repo` Git repositories. Runtime state under `state_dir` is local workflow state and is not synced by this skill.

GitHub or another Git remote is the persistence and cross-machine sync backend for user-owned target repositories. Agents operate on local clones.

## Hard Boundary

This skill must not:

- use GitHub as the query backend
- sync runtime state under `state_dir`
- commit without showing the diff
- push without explicit approval
- merge with conflicts automatically
- rewrite history
- run destructive cleanup
- sync agent-local `pamem` memory

It may:

- locate a binding via the LoreForge registry
- clone a configured remote when the local `target_repo` is missing and the user approves
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

Use the binding named by the user. If no binding is named, use the registry default.

## Workflow

### 1. Locate Target Repo

1. Read `~/.config/loreforge/registry.toml`.
2. Resolve the target binding.
3. Read the configured `target_repo`.
4. If `target_repo` is missing and `remote` exists, ask before cloning.
5. Do not operate on `state_dir` for sync.

### 2. Inspect State

Inside `target_repo`:

```bash
git status --short
git branch --show-current
git remote -v
```

Report:

- binding name
- target repository path
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
docs: update knowledge
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

- binding name and `target_repo`
- branch and remote
- clean or dirty state
- whether pull, commit, or push happened
- confirmation that `state_dir` was not synced
- any required user decision

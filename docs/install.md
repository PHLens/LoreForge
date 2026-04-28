# Install

LoreForge has two setup flows:

1. Bind an existing user-owned repository.
2. Create an optional native starter repository.

The first flow is the default. It keeps the target repository's existing layout and stores LoreForge workflow state outside the repo.

## Bind An Existing Repository

In an agent session, use the user-facing setup operation:

```text
setup binding name=notes path=/path/to/notes
```

The deterministic helper behind that flow is:

```bash
bash scripts/setup-binding.sh notes /path/to/notes \
  --target "notes=docs:General notes" \
  --target "sources=references:Source-grounded notes" \
  --default-target notes
```

Use `--read-root` and repeatable `--target "name=path:description"` options to match the repository's existing layout. The helper creates LoreForge runtime state and writes a `[[bindings]]` entry in the local registry.

Generic setup does not create these paths in the target repository:

- `.loreforge/`
- `00_System/`
- `10_Inbox/`
- `Cards/`
- `Sources/`
- `MOCs/`

It may create the target directory itself if the directory is missing, but it should not add LoreForge structure inside a generic target repo.

## Create A Native Starter Repository

Use the native starter only when the target should adopt LoreForge's high-structure profile for native query, promote, and native lint:

```text
setup binding name=cs path=/path/to/cs-native --mode native --init-native-template
```

The helper command is:

```bash
bash scripts/setup-binding.sh cs /path/to/cs-native \
  --mode native \
  --init-native-template \
  --target "cards=Cards:Native cards" \
  --target "sources=Sources:Native source notes" \
  --default-target cards
```

Native starter creation copies `templates/wiki/` into a missing or empty target path, initializes runtime state, and registers the binding as `mode = "native"`. This is optional; it is not the default shape for all LoreForge usage.

## Configure Local Discovery

Bindings are stored in:

```text
~/.config/loreforge/registry.toml
```

You can start from the template:

```bash
mkdir -p ~/.config/loreforge
cp templates/config/registry.toml ~/.config/loreforge/registry.toml
```

Most users should let `setup` update this file. Use `register` only for low-level registry maintenance when you already know the exact binding fields.

See [docs/config.md](config.md) for the full registry model.

## Use With pamem

Store agent-local workflow memory, preferences, and task state in `pamem` when useful.

Do not store professional knowledge, source notes, or durable target repo content in `pamem`.

## Install Skills

Operation skills live in:

```text
skills/
```

Core operation skills:

- `loreforge-router`
- `setup`
- `ingest`
- `writeback`
- `search`
- `lint`
- `register`
- `sync`

Native profile skills:

- `query`
- `promote`

Install them into the target agent environment using that environment's skill installation mechanism.

## Install As Plugin

LoreForge can also be installed as a plugin.

Codex plugin metadata:

```text
.codex-plugin/plugin.json
```

Claude plugin metadata:

```text
.claude-plugin/plugin.json
.claude-plugin/marketplace.json
.claude/CLAUDE.md
```

The plugin contains routing rules and skills only. Durable knowledge stays in bound user target repositories, while workflow packages and reports stay in LoreForge runtime state.

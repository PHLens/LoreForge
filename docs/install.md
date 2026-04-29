# Install

LoreForge has two parts:

1. Framework repo: this repository.
2. Wiki instance: a separate repository or vault maintained by the `loreforge-wiki` skill.

## Create A Wiki Instance

Create a wiki root and one domain:

```bash
mkdir -p /path/to/my-wiki/00_System
mkdir -p /path/to/my-wiki/Domains/my-domain/{Atlas,Cards,Sources,Spaces,Extras}
touch /path/to/my-wiki/Domains/my-domain/SCHEMA.md
touch /path/to/my-wiki/Domains/my-domain/index.md
touch /path/to/my-wiki/Domains/my-domain/log.md
```

You can also ask an agent with the `loreforge-wiki` skill to initialize the
domain. It should create:

- `SCHEMA.md`
- `index.md`
- `log.md`
- `Atlas/`
- `Cards/`
- `Sources/`
- `Spaces/`
- `Extras/`

## Use With pamem

Store the wiki instance path in the agent workspace memory if useful.

Do not store wiki knowledge in pamem.

## Configure Location

Set `WIKI_PATH` when you want agents to find the wiki without guessing:

```bash
export WIKI_PATH=/path/to/my-wiki
```

If unset, `loreforge-wiki` falls back to `~/wiki`.

## Install Core Skills

Core operation skills live in:

```text
skills/
```

Current core skill:

- `loreforge-wiki`

Install it into the target agent environment using that environment's skill installation mechanism.

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

The plugin contains framework guidance and skills only. Actual wiki knowledge
stays in separate wiki instances.

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

export class SetupError extends Error {}

const SYNC_BACKENDS = ['local', 'rclone', 'git'];

export function printSetupUsage() {
  console.log(`Usage: loreforge setup --wiki <path> --domain <name> [--wiki-name <name>] [--registry <path>] [--sync local|rclone|git] [--remote <remote>] [--sync-bootstrapped] [--description <text>] [--language <name>] [--force] [--json]

Set up a local LoreForge wiki, domain skeleton, and machine-local registry
entry for external bootstrappers. This command writes only LoreForge-owned
registry/wiki bootstrap files. It does not run rclone/git synchronization,
capture sources, ingest content, or rewrite existing pages unless --force is
passed for the registry entry.`);
}

export function runSetupCommand(tokens) {
  const args = parseSetupArgs(tokens);
  const wiki = path.resolve(expandHome(args.wiki));
  const registry = path.resolve(expandHome(args.registry));
  const writes = [];
  const preserved = [];

  if ((args.sync === 'rclone' || args.sync === 'git') && !args.remote) {
    throw new SetupError(`${args.sync} setup requires --remote`);
  }

  const registryData = readRegistry(registry);
  upsertRegistry(registryData, {
    name: args.wikiName,
    path: wiki,
    description: args.description,
    sync: args.sync,
    remote: args.remote,
    default_domain: args.domain,
    sync_bootstrapped: args.syncBootstrapped,
  }, { force: args.force });

  mkdirp(wiki, writes);
  ensureSystemFiles(wiki, args, writes, preserved);
  ensureSharedFiles(wiki, writes, preserved);
  const domainRoot = ensureDomain(wiki, args, writes);

  const validation = validateDomain(domainRoot);
  if (validation.ok) {
    writeRegistry(registry, registryData, writes);
  }

  const report = {
    component: 'loreforge',
    contract_version: '0.1',
    operation: 'setup',
    ok: validation.ok,
    registry: {
      path: registry,
      default: registryData.default,
    },
    selected_wiki: {
      name: args.wikiName,
      path: wiki,
      sync: args.sync,
      remote: args.remote,
      sync_bootstrapped: args.syncBootstrapped,
      default_domain: args.domain,
    },
    domain: {
      name: args.domain,
      path: domainRoot,
      default_language: args.language,
    },
    writes,
    preserved,
    sync: {
      executed: false,
      reason: 'setup does not run rclone/git synchronization',
    },
    validation,
  };

  if (args.json) {
    console.log(JSON.stringify(report, null, 2));
  } else {
    console.log(`LoreForge setup: ${report.ok ? 'ok' : 'issues'}`);
    console.log(`Wiki: ${wiki}`);
    console.log(`Domain: ${args.domain}`);
    console.log(`Registry: ${registry}`);
    for (const issue of validation.issues) {
      console.log(`${issue.code}: ${issue.path}: ${issue.message}`);
    }
  }
  return report.ok ? 0 : 1;
}

function parseSetupArgs(tokens) {
  const args = {
    wiki: '',
    domain: '',
    wikiName: 'main',
    registry: path.join(os.homedir(), '.config', 'loreforge', 'registry.toml'),
    sync: 'local',
    remote: '',
    syncBootstrapped: false,
    description: 'LoreForge wiki',
    language: 'zh',
    force: false,
    json: false,
  };

  for (let index = 0; index < tokens.length; index += 1) {
    const token = tokens[index];
    if (token === '-h' || token === '--help') {
      printSetupUsage();
      process.exit(0);
    }
    if (token === '--sync-bootstrapped') {
      args.syncBootstrapped = true;
      continue;
    }
    if (token === '--force') {
      args.force = true;
      continue;
    }
    if (token === '--json') {
      args.json = true;
      continue;
    }
    const option = parseValueOption(token, tokens, index);
    if (option) {
      index = option.index;
      switch (option.name) {
        case '--wiki':
          args.wiki = option.value;
          break;
        case '--domain':
          args.domain = option.value;
          break;
        case '--wiki-name':
          args.wikiName = option.value;
          break;
        case '--registry':
          args.registry = option.value;
          break;
        case '--sync':
          args.sync = option.value;
          break;
        case '--remote':
          args.remote = option.value;
          break;
        case '--description':
          args.description = option.value;
          break;
        case '--language':
          args.language = option.value;
          break;
        default:
          break;
      }
      continue;
    }
    throw new SetupError(`unknown setup argument: ${token}`);
  }

  if (!args.wiki) throw new SetupError('loreforge setup requires --wiki <path>');
  if (!args.domain) throw new SetupError('loreforge setup requires --domain <name>');
  validateDomainName(args.domain);
  if (!SYNC_BACKENDS.includes(args.sync)) throw new SetupError(`unsupported sync backend: ${args.sync}`);
  return args;
}

function validateDomainName(name) {
  if (!/^[A-Za-z0-9][A-Za-z0-9_-]*$/.test(name)) {
    throw new SetupError('domain name must be a slug containing only letters, numbers, underscores, and hyphens');
  }
}

function parseValueOption(token, tokens, index) {
  const names = ['--wiki', '--domain', '--wiki-name', '--registry', '--sync', '--remote', '--description', '--language'];
  for (const name of names) {
    if (token === name) {
      if (index + 1 >= tokens.length) throw new SetupError(`missing value for ${name}`);
      return { name, value: tokens[index + 1], index: index + 1 };
    }
    if (token.startsWith(`${name}=`)) {
      return { name, value: token.slice(name.length + 1), index };
    }
  }
  return null;
}

function expandHome(value) {
  if (value === '~') return os.homedir();
  if (value.startsWith('~/')) return path.join(os.homedir(), value.slice(2));
  return value;
}

function mkdirp(dir, writes) {
  if (fs.existsSync(dir)) return;
  fs.mkdirSync(dir, { recursive: true });
  writes.push({ kind: 'directory', path: dir });
}

function writeIfMissing(file, content, writes, preserved) {
  if (fs.existsSync(file)) {
    preserved.push({ kind: 'file', path: file });
    return;
  }
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, content);
  writes.push({ kind: 'file', path: file });
}

function appendIfMissing(file, hasEntry, initialContent, appendContent, writes, preserved) {
  if (!fs.existsSync(file)) {
    writeIfMissing(file, initialContent, writes, preserved);
    return;
  }
  const existing = fs.readFileSync(file, 'utf8');
  if (hasEntry(existing)) {
    preserved.push({ kind: 'file', path: file });
    return;
  }
  const prefix = existing.endsWith('\n') ? existing : `${existing}\n`;
  fs.writeFileSync(file, `${prefix}${appendContent}`);
  writes.push({ kind: 'file', path: file });
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function hasDomainRow(text, domain) {
  return new RegExp(`^\\|\\s*${escapeRegExp(domain)}\\s*\\|`, 'm').test(text);
}

function hasCardDomainSection(text, domain) {
  return new RegExp(`^##\\s+${escapeRegExp(domain)}\\s*$`, 'm').test(text);
}

function ensureSystemFiles(wiki, args, writes, preserved) {
  mkdirp(path.join(wiki, '00_System'), writes);
  writeIfMissing(path.join(wiki, '00_System', 'index.md'), '# Wiki Index\n\n- Layout: [[wiki-layout]]\n- Card domains: [[domains]]\n- Card policy: [[card-policy]]\n- Agent policy: [[agent-policy]]\n- Card domain details: [[card-domains]]\n', writes, preserved);
  writeIfMissing(path.join(wiki, '00_System', 'wiki-layout.md'), wikiLayout(), writes, preserved);
  writeIfMissing(path.join(wiki, '00_System', 'card-policy.md'), cardPolicy(), writes, preserved);
  writeIfMissing(path.join(wiki, '00_System', 'agent-policy.md'), agentPolicy(), writes, preserved);
  appendIfMissing(
    path.join(wiki, '00_System', 'domains.md'),
    (existing) => hasDomainRow(existing, args.domain),
    domainsIndex(args),
    domainsIndexEntry(args),
    writes,
    preserved,
  );
  appendIfMissing(
    path.join(wiki, '00_System', 'card-domains.md'),
    (existing) => hasCardDomainSection(existing, args.domain),
    cardDomains(args),
    cardDomainSection(args),
    writes,
    preserved,
  );
}

function ensureSharedFiles(wiki, writes, preserved) {
  for (const dir of [
    path.join(wiki, 'Atlas'),
    path.join(wiki, 'Calendar', 'dailynotes'),
    path.join(wiki, 'Calendar', 'weeklynotes'),
    path.join(wiki, 'Sources', 'Clippings'),
    path.join(wiki, 'Sources', 'Papers'),
    path.join(wiki, 'Sources', 'Raw'),
    path.join(wiki, 'Spaces'),
    path.join(wiki, 'Extras', 'Excalidraw'),
    path.join(wiki, 'Extras', 'Img'),
    path.join(wiki, 'Extras', 'Templates'),
    path.join(wiki, 'z-Legacy'),
  ]) {
    mkdirp(dir, writes);
  }
  writeIfMissing(path.join(wiki, 'Extras', 'Templates', 'weekly.md'), weeklyTemplate(), writes, preserved);
}

function ensureDomain(wiki, args, writes) {
  const domain = path.join(wiki, 'Cards', args.domain);
  mkdirp(domain, writes);
  return domain;
}

function readRegistry(file) {
  if (!fs.existsSync(file)) return { default: '', wikis: [] };
  return parseRegistry(fs.readFileSync(file, 'utf8'));
}

function upsertRegistry(registry, entry, { force }) {
  registry.default ||= entry.name;
  registry.wikis ||= [];
  const existing = registry.wikis.find((item) => item.name === entry.name);
  if (!existing) {
    registry.wikis.push(entry);
    return;
  }
  if (sameRegistryEntry(existing, entry)) return;
  if (!force) {
    throw new SetupError(`registry wiki entry already exists: ${entry.name}; use --force to replace it`);
  }
  Object.assign(existing, entry);
  registry.default = entry.name;
}

function writeRegistry(file, registry, writes) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, serializeRegistry(registry));
  writes.push({ kind: 'registry', path: file });
}

function parseRegistry(text) {
  const registry = { default: '', wikis: [], sources: [] };
  let current = null;
  for (const raw of text.split(/\r?\n/)) {
    const line = raw.replace(/[ \t]*#.*/, '').trim();
    if (!line) continue;
    if (line === '[[wikis]]') {
      current = {};
      registry.wikis.push(current);
      continue;
    }
    if (line === '[[sources]]') {
      current = {};
      registry.sources.push(current);
      continue;
    }
    const match = line.match(/^([A-Za-z0-9_-]+)\s*=\s*(.*)$/);
    if (!match) continue;
    const [, key, rawValue] = match;
    const value = parseTomlValue(rawValue);
    if (current) current[key] = value;
    else if (key === 'default') registry.default = String(value);
  }
  return registry;
}

function parseTomlValue(raw) {
  const value = raw.trim();
  if (value === 'true') return true;
  if (value === 'false') return false;
  if (value.startsWith('"') && value.endsWith('"')) return value.slice(1, -1).replace(/\\"/g, '"').replace(/\\\\/g, '\\');
  return value;
}

function serializeRegistry(registry) {
  const lines = [`default = ${tomlString(registry.default || registry.wikis[0]?.name || 'main')}`, ''];
  for (const wiki of registry.wikis || []) {
    lines.push(...serializeTable('wikis', wiki, ['name', 'path', 'description', 'sync', 'remote', 'default_domain', 'sync_bootstrapped']), '');
  }
  for (const source of registry.sources || []) {
    lines.push(...serializeTable('sources', source, ['name', 'kind', 'path', 'default_target_wiki', 'default_target_domain']), '');
  }
  return `${lines.join('\n').trimEnd()}\n`;
}

function serializeTable(name, data, preferredKeys) {
  const lines = [`[[${name}]]`];
  const emitted = new Set();
  for (const key of preferredKeys) {
    if (data[key] === undefined) continue;
    lines.push(serializeField(key, data[key]));
    emitted.add(key);
  }
  for (const [key, value] of Object.entries(data)) {
    if (emitted.has(key)) continue;
    lines.push(serializeField(key, value));
  }
  return lines;
}

function serializeField(key, value) {
  if (typeof value === 'boolean') return `${key} = ${value ? 'true' : 'false'}`;
  return `${key} = ${tomlString(String(value ?? ''))}`;
}

function sameRegistryEntry(left, right) {
  for (const key of ['path', 'sync', 'remote', 'default_domain', 'sync_bootstrapped']) {
    if (left[key] !== right[key]) return false;
  }
  return true;
}

function tomlString(value) {
  return `"${value.replaceAll('\\', '\\\\').replaceAll('"', '\\"')}"`;
}

function validateDomain(domainRoot) {
  const script = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'skills', 'loreforge-domain', 'scripts', 'validate_native_domain.py');
  const result = spawnSync('python3', [script, domainRoot], { encoding: 'utf8' });
  const issues = [];
  for (const line of result.stdout.split(/\r?\n/)) {
    const match = line.match(/^([^:]+):\s*([^:]+):\s*(.*)$/);
    if (match) issues.push({ code: match[1], path: match[2], message: match[3] });
  }
  return {
    ok: result.status === 0,
    issues,
  };
}

function today() {
  return new Date().toISOString().slice(0, 10);
}

function wikiLayout() {
  return `# Wiki Layout

This vault is organized by responsibility and write authority.

## Root Directories

| Path | Purpose |
|---|---|
| \`00_System/\` | Wiki contracts, Card domain registry, Card policy, and agent policy |
| \`Atlas/\` | Human-facing maps, MOCs, reading paths, and synthesis |
| \`Calendar/\` | Daily and weekly notes |
| \`Cards/\` | Stable reusable knowledge Cards, partitioned by Card domain |
| \`Sources/\` | Source notes, raw source packages, clippings, and Zotero-linked paper notes |
| \`Spaces/\` | Projects, work contexts, people, GTD, and other operational material |
| \`Extras/\` | Images, templates, Excalidraw files, and non-knowledge assets |
| \`z-Legacy/\` | Read-only legacy migration staging |

## Cards

Cards live directly under \`Cards/<domain>/<slug>.md\`. Domain schemas, indexes, and logs are centralized under \`00_System/\`; do not create \`SCHEMA.md\`, \`index.md\`, or \`log.md\` inside Card domain directories.

## Sources

\`Sources/Raw/<source-id>/\` stores normalized non-paper raw packages. \`Sources/Papers/<citekey>.md\` stores paper notes with Zotero PDF jump links. Zotero owns paper PDFs and raw attachments outside the vault.
`;
}

function domainsIndex(args) {
  return `# Card Domains

| Domain | Directory | Purpose | Default Language | Status |
|---|---|---|---|---|
| ${args.domain} | \`Cards/${args.domain}/\` | ${args.description} | ${args.language} | active |
`;
}

function domainsIndexEntry(args) {
  return `| ${args.domain} | \`Cards/${args.domain}/\` | ${args.description} | ${args.language} | active |
`;
}

function weeklyTemplate() {
  return `---
date: "{{date:gggg-[W]ww}}"
type: weekly
tags:
  - weekly
---

# {{title}}

## Focus

## This Week

- [ ]

## Daily Notes

- [[{{monday:YYYY-MM-DD}}|Mon]]
- [[{{tuesday:YYYY-MM-DD}}|Tue]]
- [[{{wednesday:YYYY-MM-DD}}|Wed]]
- [[{{thursday:YYYY-MM-DD}}|Thu]]
- [[{{friday:YYYY-MM-DD}}|Fri]]
- [[{{saturday:YYYY-MM-DD}}|Sat]]
- [[{{sunday:YYYY-MM-DD}}|Sun]]

## Risks / Blockers

-

## Decisions

-

## Review

- Done:
- Carry forward:
`;
}

function schemaTemplate(args) {
  return cardDomains(args);
}

function cardPolicy() {
  return `# Card Policy

Cards are stable reusable knowledge objects. They describe durable concepts, mechanisms, methods, tradeoffs, comparisons, decision frameworks, and evidence-backed reusable patterns.

Cards live directly under:

\`\`\`text
Cards/<domain>/<slug>.md
\`\`\`

Do not create nested \`Cards/<domain>/Cards/\` directories. Do not place domain \`SCHEMA.md\`, \`index.md\`, or \`log.md\` files inside \`Cards/<domain>/\`.

Every Card should start with YAML frontmatter:

\`\`\`yaml
---
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: card
domain: ${'${domain}'}
aliases: []
tags: []
status: active
confidence: medium
contested: false
contradictions: []
summary: One-sentence machine-readable summary.
---
\`\`\`

Prefer inline path-qualified wikilinks for source provenance, for example \`[[Sources/Raw/<source-id>/manifest|readable source alias]]\` or \`[[Sources/Papers/<citekey>|paper alias]]\`. Use source footnotes only when paragraph-level provenance would otherwise be ambiguous. Do not use YAML \`sources:\` as the primary provenance mechanism.

Manual per-domain \`index.md\` files are deprecated. A generated \`00_System/card-index.json\` may be used as an agent cache. Card Markdown frontmatter remains the source of truth.
`;
}

function cardDomains(args) {
  return `# Card Domain Details

This file defines Card domain boundaries and tag taxonomies. It replaces per-domain \`Cards/<domain>/SCHEMA.md\` files.

## Global Rules

- Every Card must follow \`card-policy.md\`.
- Every Card must live under exactly one primary domain directory.
- Use \`related_domains\` in frontmatter for cross-domain relevance instead of duplicating files.
- Tags are domain-internal classification labels, not free-form keywords.

## ${args.domain}

${args.description}

Out of scope by default:

- Agent-local workflow memory, preferences, and temporary task state.

Tag taxonomy:

- wiki, source, concept, map, person, entity, tool, project
`;
}

function cardDomainSection(args) {
  return `
## ${args.domain}

${args.description}

Out of scope by default:

- Agent-local workflow memory, preferences, and temporary task state.

Tag taxonomy:

- wiki, source, concept, map, person, entity, tool, project
`;
}

function agentPolicy() {
  return `# Agent Policy

This file defines default agent write boundaries for the vault.

## Default Write Boundaries

For ordinary Card work, agents may write only:

\`\`\`text
Cards/<assigned-domain>/*.md
\`\`\`

Agents must not write these paths unless the user explicitly asks:

\`\`\`text
Atlas/
Calendar/
Sources/
Spaces/
Extras/
z-Legacy/
.obsidian*
\`\`\`

## Pre-Write Gate

Before writing, agents should classify the operation and set an explicit write gate with allowed paths, forbidden paths, maximum changed files, create/move/delete permissions, and transaction requirement.

Routine single-Card edits should not create transaction directories. High-risk move/delete/rename and bulk migration work should use rollback patches or move maps and keep transactions only for a short retention window.
`;
}

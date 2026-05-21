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
  writeRegistry(registry, registryData, writes);

  mkdirp(wiki, writes);
  ensureSystemFiles(wiki, args.domain, writes, preserved);
  ensureSharedFiles(wiki, writes, preserved);
  const domainRoot = ensureDomain(wiki, args, writes, preserved);

  const validation = validateDomain(domainRoot);
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
  if (!SYNC_BACKENDS.includes(args.sync)) throw new SetupError(`unsupported sync backend: ${args.sync}`);
  return args;
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

function ensureSystemFiles(wiki, domain, writes, preserved) {
  mkdirp(path.join(wiki, '00_System'), writes);
  writeIfMissing(path.join(wiki, '00_System', 'index.md'), '# Wiki Index\n\n- Layout: [[wiki-layout]]\n- Domains: [[domains]]\n', writes, preserved);
  writeIfMissing(path.join(wiki, '00_System', 'wiki-layout.md'), wikiLayout(), writes, preserved);
  writeIfMissing(path.join(wiki, '00_System', 'domains.md'), domainsIndex(domain), writes, preserved);
}

function ensureSharedFiles(wiki, writes, preserved) {
  for (const dir of [
    path.join(wiki, 'Calendar', 'dailynotes'),
    path.join(wiki, 'Calendar', 'weeklynotes'),
    path.join(wiki, 'Shared', 'Raw'),
    path.join(wiki, 'Shared', 'Templates'),
  ]) {
    mkdirp(dir, writes);
  }
  writeIfMissing(path.join(wiki, 'Shared', 'Templates', 'weekly.md'), weeklyTemplate(), writes, preserved);
}

function ensureDomain(wiki, args, writes, preserved) {
  const domain = path.join(wiki, 'Domains', args.domain);
  for (const dir of ['Atlas', 'Cards', 'Spaces']) {
    mkdirp(path.join(domain, dir), writes);
  }
  writeIfMissing(path.join(domain, 'SCHEMA.md'), schemaTemplate(args), writes, preserved);
  writeIfMissing(path.join(domain, 'index.md'), domainIndex(), writes, preserved);
  writeIfMissing(path.join(domain, 'log.md'), domainLog(args), writes, preserved);
  ensureDomainRow(path.join(wiki, '00_System', 'domains.md'), args.domain, args.description, args.language, writes);
  return domain;
}

function ensureDomainRow(file, domain, description, language, writes) {
  const row = `| ${domain} | ${description} | ${language} | loreforge-domain | active |`;
  const text = fs.readFileSync(file, 'utf8');
  if (text.split(/\r?\n/).some((line) => line.startsWith(`| ${domain} |`))) return;
  const next = text.replace(/\s*$/, `\n${row}\n`);
  fs.writeFileSync(file, next);
  writes.push({ kind: 'file-update', path: file, reason: 'domain row added' });
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

Canonical shared layer:

- \`Calendar/dailynotes/\` and \`Calendar/weeklynotes/\` for dated personal notes and planning
- \`Shared/Raw/<source-id>/\` for raw source packages and attachments
- \`Shared/Templates/\` for reusable templates

Domain layer:

- \`Domains/<domain>/Atlas/\`, \`Cards/\`, \`Sources/\`, and \`Spaces/\` for compiled durable knowledge

Capture writes raw source packages into \`Shared/Raw/<source-id>/\` and stops there. Ingest updates those packages and compiles durable synthesis into \`Atlas/\`, \`Cards/\`, and \`Spaces/\`. Optional domain source excerpts live in \`Sources/\`.
`;
}

function domainsIndex(domain) {
  return `# Domains

| Domain | Purpose | Default Language | Expert | Status |
|---|---|---|---|---|
| ${domain} | LoreForge domain | zh | loreforge-domain | active |
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
  return `# Schema

## Domain
${args.description}

## Language Policy
- Raw packages preserve the source language by default. Optional domain Source notes preserve it too.
- Extracted Cards, Atlas pages, and Spaces use this domain's configured default note language: \`${args.language}\`.
- Do not translate source material unless the user asks for translation or bilingual notes.

## Conventions
- File names: lowercase, hyphens, no spaces.
- Every wiki page starts with YAML frontmatter.
- Use semantic \`[[wikilinks]]\` between pages.
- Update \`index.md\` when stable indexable pages are created.
- Insert a newest-first \`log.md\` entry for substantive actions.

## Tag Taxonomy
- Core: wiki, source, concept, map
- Spaces: person, entity, tool, project
`;
}

function domainIndex() {
  return `# Domain Index

> Mechanical inventory. Every active Markdown page under Atlas, Cards, Sources, and indexable Spaces should appear here with a one-line summary.
> Index Spaces only when tagged \`person\`, \`entity\`, \`tool\`, or \`project\`.
> Last updated: ${today()} | Total pages: 0

## Atlas

## Cards

## Sources

## Spaces
`;
}

function domainLog(args) {
  return `# Domain Log

> Reverse chronological audit trail. Newest entries go first.
> Insert each new entry directly below this instruction block.
> Format: \`## YYYY-MM-DD | <action> | <subject>\`
> Actions: create, query, ingest, update, lint, archive, delete

## ${today()} | create | Domain initialized
- domain: ${args.domain}
- default_note_language: ${args.language}
- files: SCHEMA.md, index.md, log.md
`;
}

import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';


const REPO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const CLI = path.join(REPO_ROOT, 'bin', 'loreforge');


function runLoreForge(args, { check = true } = {}) {
  const result = spawnSync(process.execPath, [CLI, ...args], {
    cwd: REPO_ROOT,
    encoding: 'utf8',
  });
  if (check && result.status !== 0) {
    assert.fail(`loreforge failed with ${result.status}\nSTDOUT:\n${result.stdout}\nSTDERR:\n${result.stderr}`);
  }
  return result;
}


function tempRoot(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'loreforge-cli-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  return root;
}


function write(file, text) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, text);
}


function seedDomain(wiki, domain = 'ai-research') {
  const domainRoot = path.join(wiki, 'Domains', domain);
  write(path.join(domainRoot, 'SCHEMA.md'), '# AI Research\n\n## Tag Taxonomy\n- topic: agent\n');
  write(path.join(domainRoot, 'index.md'), '# Index\n');
  write(path.join(domainRoot, 'log.md'), '# Log\n');
  fs.mkdirSync(path.join(domainRoot, 'Atlas'), { recursive: true });
  fs.mkdirSync(path.join(domainRoot, 'Cards'), { recursive: true });
  fs.mkdirSync(path.join(domainRoot, 'Spaces'), { recursive: true });
  fs.mkdirSync(path.join(wiki, 'Shared', 'Raw'), { recursive: true });
}


test('status command returns component envelope', (t) => {
  const root = tempRoot(t);
  const wiki = path.join(root, 'wiki');
  seedDomain(wiki);

  const result = runLoreForge(['status', '--wiki', wiki, '--json']);
  const payload = JSON.parse(result.stdout);

  assert.equal(payload.component, 'loreforge');
  assert.equal(payload.operation, 'status');
  assert.equal(payload.ok, true);
  assert.equal(payload.selected_wiki.path, wiki);
});


test('validate command delegates to native domain validator', (t) => {
  const root = tempRoot(t);
  const wiki = path.join(root, 'wiki');
  seedDomain(wiki);

  const result = runLoreForge(['validate', '--wiki', wiki, '--domain', 'ai-research', '--json']);
  const payload = JSON.parse(result.stdout);

  assert.equal(payload.component, 'loreforge');
  assert.equal(payload.operation, 'validate');
  assert.equal(payload.ok, true);
  assert.equal(payload.domains[0].ok, true);
});


test('init command is a read-only plan', (t) => {
  const root = tempRoot(t);
  const wiki = path.join(root, 'planned-wiki');

  const result = runLoreForge([
    'init',
    '--wiki',
    wiki,
    '--domain',
    'ai-research',
    '--sync',
    'rclone',
    '--remote',
    'wiki-webdav:LoreForgeWiki',
    '--json',
  ]);
  const payload = JSON.parse(result.stdout);

  assert.equal(payload.component, 'loreforge');
  assert.equal(payload.operation, 'init');
  assert.equal(payload.ok, true);
  assert.equal(payload.writes, false);
  assert.equal(fs.existsSync(wiki), false);
});


test('setup command bootstraps registry, wiki, and domain skeleton', (t) => {
  const root = tempRoot(t);
  const wiki = path.join(root, 'wiki');
  const registry = path.join(root, 'registry.toml');

  const result = runLoreForge([
    'setup',
    '--wiki',
    wiki,
    '--domain',
    'ai-research',
    '--registry',
    registry,
    '--description',
    'AI research notes',
    '--language',
    'zh',
    '--json',
  ]);
  const payload = JSON.parse(result.stdout);

  assert.equal(payload.component, 'loreforge');
  assert.equal(payload.operation, 'setup');
  assert.equal(payload.ok, true);
  assert.equal(payload.selected_wiki.path, wiki);
  assert.equal(payload.domain.name, 'ai-research');
  assert.equal(payload.validation.ok, true);
  assert.equal(fs.existsSync(registry), true);
  assert.equal(fs.existsSync(path.join(wiki, '00_System', 'index.md')), true);
  assert.equal(fs.existsSync(path.join(wiki, 'Shared', 'Templates', 'weekly.md')), true);
  assert.equal(fs.existsSync(path.join(wiki, 'Shared', 'Templates', 'card.md')), true);
  assert.equal(fs.existsSync(path.join(wiki, 'Shared', 'Templates', 'moc.md')), true);
  assert.equal(fs.existsSync(path.join(wiki, 'Shared', 'Templates', 'relationship.md')), true);
  assert.match(fs.readFileSync(path.join(wiki, 'Shared', 'Templates', 'card.md'), 'utf8'), /type: concept/);
  assert.match(fs.readFileSync(path.join(wiki, 'Shared', 'Templates', 'moc.md'), 'utf8'), /type: map/);
  assert.match(fs.readFileSync(path.join(wiki, 'Shared', 'Templates', 'relationship.md'), 'utf8'), /Relationship Title/);
  assert.equal(fs.existsSync(path.join(wiki, 'Domains', 'ai-research', 'SCHEMA.md')), true);
  assert.match(fs.readFileSync(registry, 'utf8'), /default_domain = "ai-research"/);

  const customizedCard = path.join(wiki, 'Shared', 'Templates', 'card.md');
  fs.writeFileSync(customizedCard, 'custom card template\n');

  const rerun = runLoreForge([
    'setup',
    '--wiki',
    wiki,
    '--domain',
    'ai-research',
    '--registry',
    registry,
    '--description',
    'Different description should not matter without --force when core binding is identical',
    '--language',
    'zh',
    '--json',
  ]);
  assert.equal(JSON.parse(rerun.stdout).ok, true);
  assert.equal(fs.readFileSync(customizedCard, 'utf8'), 'custom card template\n');
});


test('setup preserves source registry entries', (t) => {
  const root = tempRoot(t);
  const wiki = path.join(root, 'wiki');
  const registry = path.join(root, 'registry.toml');
  write(registry, `default = "main"

[[sources]]
name = "old-vault"
kind = "obsidian-vault"
path = "/tmp/old-vault"
default_target_wiki = "main"
default_target_domain = "ai-research"
`);

  runLoreForge([
    'setup',
    '--wiki',
    wiki,
    '--domain',
    'ai-research',
    '--registry',
    registry,
    '--json',
  ]);

  const registryText = fs.readFileSync(registry, 'utf8');
  assert.match(registryText, /\[\[sources\]\]/);
  assert.match(registryText, /name = "old-vault"/);
});


test('help and version are available', () => {
  assert.match(runLoreForge(['--help']).stdout, /Usage: loreforge/);
  assert.match(runLoreForge(['help', 'validate']).stdout, /Usage: loreforge validate/);
  assert.match(runLoreForge(['setup', '--help']).stdout, /Usage: loreforge setup/);
  assert.match(runLoreForge(['help', 'setup']).stdout, /Usage: loreforge setup/);
  assert.match(runLoreForge(['--version']).stdout.trim(), /^\d+\.\d+\.\d+$/);
});

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


test('help and version are available', () => {
  assert.match(runLoreForge(['--help']).stdout, /Usage: loreforge/);
  assert.match(runLoreForge(['help', 'validate']).stdout, /Usage: loreforge validate/);
  assert.match(runLoreForge(['--version']).stdout.trim(), /^\d+\.\d+\.\d+$/);
});

import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { printSetupUsage, runSetupCommand, SetupError } from './setup.mjs';


const REPO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const COMPONENT_SCRIPT = path.join(REPO_ROOT, 'skills', 'loreforge-domain', 'scripts', 'loreforge_component.py');
const PACKAGE_JSON = path.join(REPO_ROOT, 'package.json');
const COMPONENT_COMMANDS = new Set(['status', 'validate', 'init']);


const TOP_USAGE = `Usage: loreforge <command> [args]

Commands:
  status                        Report LoreForge registry and wiki availability.
  validate                      Validate one or all LoreForge domains.
  init                          Print a read-only LoreForge init plan.
  setup                         Bootstrap registry, wiki, and domain skeleton.
  help [command]                Show command help.

Options:
  -h, --help                    Show this help message.
  --version                     Show package version.

Examples:
  loreforge status --json
  loreforge status --wiki-name main --json
  loreforge validate --wiki /path/to/wiki --all-domains --json
  loreforge init --wiki /path/to/wiki --domain ai-research --json
  loreforge setup --wiki /path/to/wiki --domain ai-research --json`;


const COMMAND_USAGE = {
  status: `Usage: loreforge status [--registry <path>] [--wiki-name <name>] [--wiki <path>] [--json]

Read-only availability check for the LoreForge registry and selected wiki.`,
  validate: `Usage: loreforge validate [--registry <path>] [--wiki-name <name>] [--wiki <path>] [--domain <name>|--all-domains] [--json]

Read-only validation check for one or all LoreForge domains.`,
  init: `Usage: loreforge init --wiki <path> --domain <name> [--wiki-name <name>] [--sync local|rclone|git] [--remote <remote>] [--sync-bootstrapped] [--json]

Print a proposal-only init plan. This command does not write registry files,
wiki folders, sync state, or notes.`,
};


class UsageError extends Error {}


export function main(argv = process.argv.slice(2)) {
  try {
    if (argv.length === 0 || argv[0] === '-h' || argv[0] === '--help') {
      console.log(TOP_USAGE);
      return 0;
    }
    if (argv[0] === '--version') {
      console.log(packageVersion());
      return 0;
    }
    if (argv[0] === 'help') {
      return printHelp(argv.slice(1));
    }

    const [command, ...rest] = argv;
    if (command === 'setup') {
      if (hasHelpFlag(rest)) {
        printSetupUsage();
        return 0;
      }
      return runSetupCommand(rest);
    }
    if (!COMPONENT_COMMANDS.has(command)) {
      throw new UsageError(`unknown command: ${command}`);
    }
    if (hasHelpFlag(rest)) {
      console.log(COMMAND_USAGE[command]);
      return 0;
    }
    return runComponent(command, rest);
  } catch (error) {
    if (error instanceof UsageError) {
      console.error(`error: ${error.message}`);
      return 1;
    }
    if (error instanceof SetupError) {
      console.error(`error: ${error.message}`);
      return 1;
    }
    throw error;
  }
}


function printHelp(topics) {
  if (topics.length === 0) {
    console.log(TOP_USAGE);
    return 0;
  }
  if (topics.length === 1 && topics[0] === 'setup') {
    printSetupUsage();
    return 0;
  }
  if (topics.length > 1 || !COMMAND_USAGE[topics[0]]) {
    throw new UsageError(`unknown help topic: ${topics.join(' ')}`);
  }
  console.log(COMMAND_USAGE[topics[0]]);
  return 0;
}


function runComponent(command, args) {
  const python = process.env.PYTHON || 'python3';
  const result = spawnSync(python, [COMPONENT_SCRIPT, command, ...args], {
    cwd: REPO_ROOT,
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  if (result.stdout) process.stdout.write(result.stdout);
  if (result.stderr) process.stderr.write(result.stderr);
  if (result.error) {
    console.error(`error: failed to run component adapter: ${result.error.message}`);
    return 1;
  }
  return typeof result.status === 'number' ? result.status : 1;
}


function hasHelpFlag(args) {
  return args.includes('-h') || args.includes('--help');
}


function packageVersion() {
  try {
    return JSON.parse(fs.readFileSync(PACKAGE_JSON, 'utf8')).version || '0.0.0';
  } catch {
    return '0.0.0';
  }
}

#!/usr/bin/env python3
"""Smoke-test LoreForge wiki config, initialization, and import flow.

The skill owns these behaviors as operating instructions rather than as a
runtime library. This test makes the expected file effects concrete: registry
discovery, environment overrides, wiki/domain initialization, and source-only
import into a native domain.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "skills" / "loreforge-domain" / "scripts"))

from validate_native_domain import validate_domain


TODAY = "2026-04-30"
LOG_ENTRY_PATTERN = re.compile(r"\n## \d{4}-\d{2}-\d{2} \| ")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def digest_tree(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            result[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def digest_index(values: dict[str, str]) -> str:
    payload = "\n".join(f"{path}:{digest}" for path, digest in sorted(values.items()))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def insert_log_entry(domain: Path, entry: str) -> None:
    path = domain / "log.md"
    text = path.read_text(encoding="utf-8")
    normalized = entry.strip() + "\n\n"
    match = LOG_ENTRY_PATTERN.search(text)
    if match:
        offset = match.start() + 1
        path.write_text(text[:offset] + normalized + text[offset:], encoding="utf-8")
    else:
        path.write_text(text.rstrip() + "\n\n" + normalized, encoding="utf-8")


def log_headings(domain: Path) -> list[str]:
    text = (domain / "log.md").read_text(encoding="utf-8")
    return re.findall(r"^## .+$", text, flags=re.MULTILINE)


def load_registry(home: Path) -> dict:
    path = home / ".config" / "loreforge" / "registry.toml"
    return tomllib.loads(path.read_text(encoding="utf-8"))


def registry_wiki(registry: dict, name: str | None = None) -> dict:
    target = name or registry["default"]
    for wiki in registry.get("wikis", []):
        if wiki["name"] == target:
            return wiki
    raise AssertionError(f"missing wiki entry: {target}")


def registry_source(registry: dict, name: str) -> dict:
    for source in registry.get("sources", []):
        if source["name"] == name:
            return source
    raise AssertionError(f"missing source entry: {name}")


def toml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def write_registry(home: Path, *, default: str, wikis: list[dict], sources: list[dict]) -> None:
    lines: list[str] = [f'default = {toml_quote(default)}', ""]
    for wiki_entry in wikis:
        lines.extend(
            [
                "[[wikis]]",
                f'name = {toml_quote(wiki_entry["name"])}',
                f'path = {toml_quote(wiki_entry["path"])}',
                f'description = {toml_quote(wiki_entry["description"])}',
                f'sync = {toml_quote(wiki_entry["sync"])}',
                f'remote = {toml_quote(wiki_entry["remote"])}',
                f'default_domain = {toml_quote(wiki_entry["default_domain"])}',
                f'sync_bootstrapped = {str(bool(wiki_entry["sync_bootstrapped"])).lower()}',
                "",
            ]
        )
    for source_entry in sources:
        lines.extend(
            [
                "[[sources]]",
                f'name = {toml_quote(source_entry["name"])}',
                f'kind = {toml_quote(source_entry["kind"])}',
                f'path = {toml_quote(source_entry["path"])}',
                f'default_target_wiki = {toml_quote(source_entry["default_target_wiki"])}',
                f'default_target_domain = {toml_quote(source_entry["default_target_domain"])}',
                "",
            ]
        )
    write(home / ".config" / "loreforge" / "registry.toml", "\n".join(lines).rstrip() + "\n")


def rclone_sync_command(wiki: Path | str, remote: str, *, mode: str = "pull") -> str:
    script = REPO_ROOT / "skills" / "loreforge-domain" / "scripts" / "sync_rclone.sh"
    argv = [
        "bash",
        script.as_posix(),
        "--wiki",
        wiki.as_posix() if isinstance(wiki, Path) else wiki,
        "--remote",
        remote,
        "--mode",
        mode,
        "--dry-run",
    ]
    result = subprocess.run(argv, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def pre_read_sync_plan(wiki: Path, wiki_entry: dict) -> list[str]:
    backend = wiki_entry["sync"]
    remote = wiki_entry.get("remote", "")
    if backend == "rclone":
        return [rclone_sync_command(wiki, remote, mode="pull")]
    return []


def post_write_sync_plan(wiki: Path, wiki_entry: dict, message: str) -> list[str]:
    backend = wiki_entry["sync"]
    remote = wiki_entry.get("remote", "")
    if backend == "local":
        return [f"local-only: no remote sync ran for {wiki.as_posix()}"]
    if backend == "rclone":
        if not wiki_entry.get("sync_bootstrapped", False):
            return [rclone_sync_command(wiki, remote, mode="bootstrap")]
        return [rclone_sync_command(wiki, remote, mode="push")]
    if backend == "git":
        return [
            f"git -C {wiki.as_posix()} add .",
            f"git -C {wiki.as_posix()} commit -m {message!r}",
            f"git -C {wiki.as_posix()} push",
        ]
    raise AssertionError(f"unknown sync backend: {backend}")


def resolve_wiki_and_domain(
    registry: dict,
    *,
    env: dict[str, str] | None = None,
    user_wiki: str | None = None,
    user_domain: str | None = None,
) -> tuple[Path, str]:
    """Model the discovery order documented in loreforge-domain."""

    env = env or {}
    if user_wiki:
        wiki_path = Path(user_wiki)
    elif env.get("WIKI_PATH"):
        wiki_path = Path(env["WIKI_PATH"])
    elif env.get("WIKI_NAME"):
        wiki_path = Path(registry_wiki(registry, env["WIKI_NAME"])["path"])
    else:
        wiki_path = Path(registry_wiki(registry)["path"])

    if user_domain:
        domain_name = user_domain
    elif env.get("DOMAIN_NAME"):
        domain_name = env["DOMAIN_NAME"]
    else:
        selected = None
        if env.get("WIKI_NAME"):
            selected = registry_wiki(registry, env["WIKI_NAME"])
        elif not env.get("WIKI_PATH") and not user_wiki:
            selected = registry_wiki(registry)
        domain_name = (selected or {}).get("default_domain") or "<ask-user>"

    return wiki_path, domain_name


def initialize_domain(
    wiki: Path,
    domain_name: str,
) -> Path:
    domain = wiki / "Domains" / domain_name
    for directory in [
        wiki / "00_System",
        wiki / "Calendar" / "dailynotes",
        wiki / "Shared" / "Raw",
        wiki / "Shared" / "Templates",
        domain / "Atlas",
        domain / "Cards",
        domain / "Spaces",
    ]:
        directory.mkdir(parents=True, exist_ok=True)

    write(wiki / "00_System" / "index.md", "# Wiki Index\n\n- Domains: [[domains]]\n")
    write(
        wiki / "00_System" / "index.md",
        "# Wiki Index\n\n- Layout: [[wiki-layout]]\n- Domains: [[domains]]\n",
    )
    write(
        wiki / "00_System" / "wiki-layout.md",
        "# Wiki Layout\n\n"
        "Canonical shared layer:\n\n"
        "- `Shared/Raw/<source-id>/` for raw source packages and attachments\n"
        "- `Shared/Templates/` for reusable templates\n\n"
        "Domain layer:\n\n"
        "- `Domains/<domain>/Atlas/`, `Cards/`, `Sources/`, and `Spaces/` for compiled durable knowledge\n\n"
        "Compiled pages live in `Domains/<domain>/Atlas/`, `Cards/`, `Sources/`, and `Spaces/`. "
        "Capture writes raw source packages into `Shared/Raw/<source-id>/` and stops there; ingest updates those packages; `Sources/` is optional for source excerpts.\n\n"
        "Tags are coarse domain classification labels; keep them to 1-3 per page instead of keyword stacks.\n\n"
        "Create `Domains/<domain>/Extras/` only when the domain needs its own\n"
        "non-source attachments.\n",
    )
    write(
        wiki / "00_System" / "domains.md",
        "# Domains\n\n"
        "| Domain | Purpose | Default Language | Expert | Status |\n"
        "|---|---|---|---|---|\n"
        f"| {domain_name} | Test research domain | zh | test expert | active |\n",
    )
    write(
        domain / "SCHEMA.md",
        "# Schema\n\n"
        "## Domain\nTest research domain.\n\n"
        "## Language Policy\n- Extracted Cards, Atlas pages, and Spaces use zh.\n\n"
        "## Tag Taxonomy\n"
        "- Core: wiki, source, concept, map\n"
        "- Spaces: person, entity, tool, project\n",
    )
    write(
        domain / "index.md",
        "# Domain Index\n\n"
        f"> Last updated: {TODAY} | Total pages: 0\n\n"
        "## Atlas\n\n## Cards\n\n## Spaces\n",
    )
    write(
        domain / "log.md",
        "# Domain Log\n\n"
        "> Reverse chronological audit trail. Newest entries go first.\n"
        "> Insert each new entry directly below this instruction block.\n"
        "> Format: `## YYYY-MM-DD | <action> | <subject>`\n"
        "> Actions: create, query, ingest, update, lint, archive, delete\n\n"
        f"## {TODAY} | create | Domain initialized\n"
        f"- domain: {domain_name}\n"
        "- default_note_language: zh\n"
        "- files: SCHEMA.md, index.md, log.md\n",
    )
    return domain


def import_source(source: Path, domain: Path) -> None:
    source_text = (source / "notes" / "llm-wiki.md").read_text(encoding="utf-8")
    wiki = domain.parents[1]

    raw_root = wiki / "Shared" / "Raw"
    raw_root.mkdir(parents=True, exist_ok=True)
    raw = raw_root / "old-obsidian-llm-wiki"
    raw.mkdir(parents=True, exist_ok=True)
    (raw / "original").mkdir(exist_ok=True)
    write(raw / "original" / "clip.md", source_text)
    (raw / "assets").mkdir(exist_ok=True)
    origin = raw / "origin.md"
    origin.write_text(
        f"""---
title: Old Obsidian LLM Wiki Raw Source
created: {TODAY}
updated: {TODAY}
type: source
source_type: obsidian-vault
source_language: en
retrieved_at: {TODAY}
source_description: Imported source-language note from the old Obsidian vault
origin: Shared/Raw/old-obsidian-llm-wiki/origin.md
candidate_domains:
  - ai-research
compiled_pages: []
status: captured
---

# Old Obsidian LLM Wiki Raw Source

Imported source-language note from the old Obsidian vault.
""",
        encoding="utf-8",
    )
    (raw / "assets" / "diagram.png").write_bytes(b"fake image bytes for import smoke test")
    raw_hash = hashlib.sha256(origin.read_bytes()).hexdigest()

    write(
        raw / "manifest.md",
        f"""---
title: Old Obsidian LLM Wiki Raw Source
source_id: old-obsidian-llm-wiki
source_alias: old-obsidian
source_type: obsidian-vault
source_language: en
retrieved_at: {TODAY}
source_description: Imported source-language note from the old Obsidian vault
content_hash: {raw_hash}
origin: Shared/Raw/old-obsidian-llm-wiki/origin.md
candidate_domains:
  - ai-research
compiled_pages:
  - Domains/{domain.name}/Cards/compounding-wiki.md
  - Domains/{domain.name}/Spaces/obsidian.md
status: compiled
artifacts:
  - Shared/Raw/old-obsidian-llm-wiki/original/clip.md
  - Shared/Raw/old-obsidian-llm-wiki/assets/diagram.png
---

# Old Obsidian LLM Wiki Raw Source

Imported source-language note from the old Obsidian vault.
""",
    )
    write(
        domain / "Cards" / "compounding-wiki.md",
        f"""---
title: Compounding Wiki
created: {TODAY}
updated: {TODAY}
type: concept
tags: [concept, wiki]
confidence: medium
status: active
contested: false
contradictions: []
---

# Compounding Wiki

A compounding wiki turns repeated source processing into durable knowledge. It is
grounded by raw source capture and maintained with [[obsidian]].[^source]

[^source]: [[Shared/Raw/old-obsidian-llm-wiki/manifest.md]]
""",
    )
    write(
        domain / "Spaces" / "obsidian.md",
        f"""---
title: Obsidian
created: {TODAY}
updated: {TODAY}
type: space
tags: [tool]
confidence: medium
status: active
contested: false
contradictions: []
---

# Obsidian

Obsidian is the editor used to browse [[compounding-wiki]] notes and imported raw
source manifests.[^source]

[^source]: [[Shared/Raw/old-obsidian-llm-wiki/manifest.md]]
""",
    )
    write(
        domain / "index.md",
        "# Domain Index\n\n"
        f"> Last updated: {TODAY} | Total pages: 2\n\n"
        "## Atlas\n\n"
        "## Cards\n"
        "- [[compounding-wiki]] - Durable knowledge that compounds from repeated source processing.\n\n"
        "## Spaces\n"
        "- [[obsidian]] - Tool used to browse and edit the wiki.\n",
    )
    insert_log_entry(
        domain,
        f"""## {TODAY} | ingest | old-obsidian import
- captured: Shared/Raw/old-obsidian-llm-wiki/
- source_alias: old-obsidian
- import_scope: notes/llm-wiki.md and attachment metadata
- created: Shared/Raw/old-obsidian-llm-wiki/origin.md
- created: Shared/Raw/old-obsidian-llm-wiki/manifest.md
- created: Shared/Raw/old-obsidian-llm-wiki/assets/diagram.png
- created: Cards/compounding-wiki.md
- created: Spaces/obsidian.md
- updated: index.md
""",
    )


def assert_valid(domain: Path) -> None:
    issues = validate_domain(domain)
    if issues:
        lines = "\n".join(issue.line() for issue in issues)
        raise AssertionError(f"{domain} is invalid:\n{lines}")


def assert_skill_example_is_generic() -> None:
    wiki_skill = (REPO_ROOT / "skills" / "loreforge-domain" / "SKILL.md").read_text(encoding="utf-8")
    config_skill = (REPO_ROOT / "skills" / "loreforge-config" / "SKILL.md").read_text(encoding="utf-8")
    capture_skill = (REPO_ROOT / "skills" / "loreforge-capture" / "SKILL.md").read_text(encoding="utf-8")
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    config_doc = (REPO_ROOT / "docs" / "config.md").read_text(encoding="utf-8")
    sync_script = REPO_ROOT / "skills" / "loreforge-domain" / "scripts" / "sync_rclone.sh"
    forbidden = ["/home/cambricon", "Nutstore", "OldVault"]
    found = [value for value in forbidden if value in config_skill or value in capture_skill]
    if found:
        raise AssertionError(f"skill example contains environment-specific values: {found}")
    for expected in ["/path/to/loreforge-wiki", "/path/to/source-vault", "~/.config/loreforge/registry.toml", "sync_bootstrapped", "local | rclone | git"]:
        if expected not in config_skill:
            raise AssertionError(f"config skill is missing config guidance: {expected}")
    for expected in [
        "Shared/Raw/",
        "raw source package",
        "origin.md",
        "manifest.md",
        "create `Cards/`, `Atlas/`, `Spaces/`, or domain `Sources/`",
        "route or choose final domain ownership",
    ]:
        if expected not in capture_skill:
            raise AssertionError(f"capture skill is missing capture guidance: {expected}")
    for expected in [
        'sync = "local"',
        "rclone",
        "git",
        "local-only",
        "~/.config/loreforge/registry.toml",
        "machine-local registry",
        "scripts/sync_rclone.sh",
    ]:
        if expected not in config_skill:
            raise AssertionError(f"skill is missing sync guidance: {expected}")
    for expected in [
        "skills/loreforge-domain/scripts/sync_rclone.sh",
    ]:
        if expected not in readme:
            raise AssertionError(f"README is missing sync helper guidance: {expected}")
        if expected not in config_doc:
            raise AssertionError(f"config docs are missing sync helper guidance: {expected}")
    if not sync_script.exists():
        raise AssertionError(f"rclone sync helper is missing: {sync_script}")
    if (REPO_ROOT / "skills" / "loreforge-domain" / "scripts" / "sync_scp.sh").exists():
        raise AssertionError("SCP helper should not exist; use rclone SFTP instead")
    if (REPO_ROOT / "skills" / "loreforge-domain" / "scripts" / "sync_webdav.sh").exists():
        raise AssertionError("WebDAV helper should not exist; use the generic rclone helper instead")
    pull = rclone_sync_command("~/wiki", "wiki-webdav:LoreForgeWiki")
    push = rclone_sync_command("~/wiki", "wiki-webdav:LoreForgeWiki", mode="push")
    bootstrap = rclone_sync_command("~/wiki", "wiki-webdav:LoreForgeWiki", mode="bootstrap")
    sftp = rclone_sync_command("~/wiki", "wiki-sftp:LoreForgeWiki")
    home_wiki = (Path.home() / "wiki").as_posix()
    for expected in [
        "rclone sync",
        f"wiki-webdav:LoreForgeWiki {home_wiki}",
        "--create-empty-src-dirs",
        "--exclude .obsidian\\*/\\*\\*",
        "-P -v",
    ]:
        if expected not in pull:
            raise AssertionError(f"rclone helper pull command is missing {expected}: {pull}")
    if "rclone bisync" in pull:
        raise AssertionError(f"rclone helper should not use bisync by default: {pull}")
    if f"{home_wiki} wiki-webdav:LoreForgeWiki" not in push:
        raise AssertionError(f"rclone helper push command should copy local to remote: {push}")
    if f"{home_wiki} wiki-webdav:LoreForgeWiki" not in bootstrap:
        raise AssertionError(f"rclone helper bootstrap command should seed remote from local: {bootstrap}")
    if "wiki-sftp:LoreForgeWiki" not in sftp:
        raise AssertionError(f"rclone helper should support SFTP rclone remotes: {sftp}")
    for expected in [".obsidian*", ".obsidian-desktop", ".obsidian-mobile"]:
        if expected not in wiki_skill:
            raise AssertionError(f"skill is missing Obsidian profile boundary: {expected}")


def main() -> int:
    assert_skill_example_is_generic()
    print("PASS skill example: registry paths are generic placeholders")

    with tempfile.TemporaryDirectory(prefix="loreforge-config-flow-") as tmp_raw:
        tmp = Path(tmp_raw)
        home = tmp / "home"
        wiki = tmp / "wiki-root"
        named_wiki = tmp / "named-wiki-root"
        source = tmp / "source-vault"

        write(source / "notes" / "llm-wiki.md", "# LLM Wiki\n\nA prior vault note.\n")
        write(source / "diagram.png", "placeholder attachment\n")

        registry_wikis = [
            {
                "name": "main",
                "path": wiki.as_posix(),
                "description": "Temp LoreForge wiki",
                "sync": "local",
                "remote": "",
                "default_domain": "ai-research",
                "sync_bootstrapped": False,
            },
            {
                "name": "systems",
                "path": named_wiki.as_posix(),
                "description": "Named wiki",
                "sync": "local",
                "remote": "",
                "default_domain": "ml-systems",
                "sync_bootstrapped": False,
            },
        ]
        registry_sources = [
            {
                "name": "old-obsidian",
                "kind": "obsidian-vault",
                "path": source.as_posix(),
                "default_target_wiki": "main",
                "default_target_domain": "ai-research",
            }
        ]
        write_registry(
            home,
            default="main",
            wikis=registry_wikis,
            sources=registry_sources,
        )

        registry = load_registry(home)
        selected_source = registry_source(registry, "old-obsidian")

        assert resolve_wiki_and_domain(registry) == (wiki, "ai-research")
        assert resolve_wiki_and_domain(registry, env={"WIKI_NAME": "systems"}) == (named_wiki, "ml-systems")
        assert resolve_wiki_and_domain(
            registry,
            env={"WIKI_PATH": (tmp / "env-wiki").as_posix(), "DOMAIN_NAME": "env-domain"},
        ) == (tmp / "env-wiki", "env-domain")
        assert resolve_wiki_and_domain(
            registry,
            user_wiki=(tmp / "explicit-wiki").as_posix(),
            user_domain="explicit-domain",
        ) == (tmp / "explicit-wiki", "explicit-domain")
        assert Path(selected_source["path"]) == source
        assert selected_source["default_target_wiki"] == "main"
        assert selected_source["default_target_domain"] == "ai-research"
        print("PASS discovery: registry, env override, explicit paths, and source alias resolved")

        domain = initialize_domain(wiki, "ai-research")
        assert_valid(domain)
        assert (wiki / "00_System" / "index.md").exists()
        assert (wiki / "00_System" / "wiki-layout.md").exists()
        assert not (wiki / "00_System" / "loreforge.toml").exists()
        assert (wiki / "Calendar" / "dailynotes").is_dir()
        assert (wiki / "Shared" / "Raw").is_dir()
        assert (wiki / "Shared" / "Templates").is_dir()
        assert not (domain / "Sources").exists()
        assert "Layout: [[wiki-layout]]" in (wiki / "00_System" / "index.md").read_text(encoding="utf-8")
        assert "ai-research" in (wiki / "00_System" / "domains.md").read_text(encoding="utf-8")
        local_plan = post_write_sync_plan(wiki, registry_wiki(registry, "main"), "initial wiki update")
        assert local_plan == [f"local-only: no remote sync ran for {wiki.as_posix()}"]
        print("PASS initialization: 00_System, Calendar, shared raw layer, wiki layout, and native domain contract created")

        bootstrap_plan = post_write_sync_plan(
            wiki,
            {
                "sync": "rclone",
                "remote": "wiki-webdav:LoreForgeWiki",
                "sync_bootstrapped": False,
            },
            "bootstrap wiki",
        )
        assert bootstrap_plan == [
            rclone_sync_command(wiki, "wiki-webdav:LoreForgeWiki", mode="bootstrap")
        ]
        print("PASS sync bootstrap: first rclone run explicitly seeds remote from local")

        registry_wikis[0].update(
            {
                "sync": "rclone",
                "remote": "wiki-webdav:LoreForgeWiki",
                "sync_bootstrapped": True,
            }
        )
        write_registry(
            home,
            default="main",
            wikis=registry_wikis,
            sources=registry_sources,
        )
        registry = load_registry(home)
        main_wiki = registry_wiki(registry, "main")
        assert main_wiki["sync"] == "rclone"
        assert main_wiki["remote"] == "wiki-webdav:LoreForgeWiki"
        assert main_wiki["sync_bootstrapped"] is True
        rclone_pull_plan = pre_read_sync_plan(wiki, main_wiki)
        assert rclone_pull_plan == [rclone_sync_command(wiki, "wiki-webdav:LoreForgeWiki", mode="pull")]
        rclone_plan = post_write_sync_plan(wiki, main_wiki, "update compounding card")
        assert rclone_plan == [rclone_sync_command(wiki, "wiki-webdav:LoreForgeWiki", mode="push")]
        print("PASS sync upgrade: existing wiki pulls before write and pushes after write with WebDAV")

        named_domain = initialize_domain(named_wiki, "ml-systems")
        assert_valid(named_domain)
        assert not (named_wiki / "00_System" / "loreforge.toml").exists()
        registry_wikis[1].update(
            {
                "sync": "git",
                "remote": "git@github.com:PHLens/named-wiki.git",
                "sync_bootstrapped": True,
            }
        )
        write_registry(
            home,
            default="main",
            wikis=registry_wikis,
            sources=registry_sources,
        )
        registry = load_registry(home)
        systems_wiki = registry_wiki(registry, "systems")
        assert systems_wiki["sync"] == "git"
        assert systems_wiki["remote"] == "git@github.com:PHLens/named-wiki.git"
        assert systems_wiki["sync_bootstrapped"] is True
        git_plan = post_write_sync_plan(named_wiki, systems_wiki, "update systems wiki")
        expected_git_commit = f"git -C {named_wiki.as_posix()} commit -m 'update systems wiki'"
        assert git_plan == [
            f"git -C {named_wiki.as_posix()} add .",
            expected_git_commit,
            f"git -C {named_wiki.as_posix()} push",
        ]
        print("PASS sync upgrade: existing wiki can be switched to git and commit/push is required")

        registry_wikis[1].update(
            {
                "sync": "rclone",
                "remote": "wiki-sftp:LoreForgeWiki",
                "sync_bootstrapped": True,
            }
        )
        write_registry(
            home,
            default="main",
            wikis=registry_wikis,
            sources=registry_sources,
        )
        registry = load_registry(home)
        systems_wiki = registry_wiki(registry, "systems")
        assert systems_wiki["sync"] == "rclone"
        assert systems_wiki["remote"] == "wiki-sftp:LoreForgeWiki"
        assert systems_wiki["sync_bootstrapped"] is True
        sftp_pull_plan = pre_read_sync_plan(named_wiki, systems_wiki)
        assert sftp_pull_plan == [rclone_sync_command(named_wiki, "wiki-sftp:LoreForgeWiki", mode="pull")]
        sftp_plan = post_write_sync_plan(named_wiki, systems_wiki, "sync systems wiki")
        assert sftp_plan == [rclone_sync_command(named_wiki, "wiki-sftp:LoreForgeWiki", mode="push")]
        print("PASS sync upgrade: existing wiki pulls before write and pushes after write with SFTP")

        source_before = digest_tree(source)
        import_source(source, domain)
        if source_before != digest_tree(source):
            raise AssertionError("source vault changed during import")
        assert_valid(domain)
        manifest = wiki / "Shared" / "Raw" / "old-obsidian-llm-wiki" / "manifest.md"
        assert manifest.exists()
        manifest_text = manifest.read_text(encoding="utf-8")
        assert "content_hash:" in manifest_text
        assert "compiled_pages:" in manifest_text
        assert "origin: Shared/Raw/old-obsidian-llm-wiki/origin.md" in manifest_text
        assert (wiki / "Shared" / "Raw" / "old-obsidian-llm-wiki" / "original" / "clip.md").exists()
        assert (wiki / "Shared" / "Raw" / "old-obsidian-llm-wiki" / "origin.md").exists()
        assert (wiki / "Shared" / "Raw" / "old-obsidian-llm-wiki" / "assets" / "diagram.png").exists()
        assert not (domain / "Sources").exists()
        assert "source_alias: old-obsidian" in (domain / "log.md").read_text(encoding="utf-8")
        if not log_headings(domain)[0].startswith(f"## {TODAY} | ingest |"):
            raise AssertionError("import log entry was not inserted as newest entry")
        print("PASS import: source stayed read-only and target domain remains valid")

    print("wiki config flow smoke test ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

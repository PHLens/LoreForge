#!/usr/bin/env python3
"""Smoke-test LoreForge wiki config, initialization, and migration flow.

The skill owns these behaviors as operating instructions rather than as a
runtime library. This test makes the expected file effects concrete: registry
discovery, environment overrides, wiki/domain initialization, and source-only
migration into a native domain.
"""

from __future__ import annotations

import hashlib
import tempfile
import tomllib
from pathlib import Path

from validate_native_domain import validate_domain


TODAY = "2026-04-30"
REPO_ROOT = Path(__file__).resolve().parents[1]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def digest_tree(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            result[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


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


def resolve_wiki_and_domain(
    registry: dict,
    *,
    env: dict[str, str] | None = None,
    user_wiki: str | None = None,
    user_domain: str | None = None,
) -> tuple[Path, str]:
    """Model the discovery order documented in loreforge-wiki."""

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


def initialize_domain(wiki: Path, domain_name: str) -> Path:
    domain = wiki / "Domains" / domain_name
    for directory in [
        wiki / "00_System",
        domain / "Atlas",
        domain / "Cards",
        domain / "Sources",
        domain / "Spaces",
        domain / "Extras",
    ]:
        directory.mkdir(parents=True, exist_ok=True)

    write(wiki / "00_System" / "index.md", "# Wiki Index\n\n- Domains: [[domains]]\n")
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
        "## Atlas\n\n## Cards\n\n## Sources\n\n## Spaces\n",
    )
    write(
        domain / "log.md",
        "# Domain Log\n\n"
        f"## {TODAY} | create | Domain initialized\n"
        f"- domain: {domain_name}\n"
        "- default_note_language: zh\n"
        "- files: SCHEMA.md, index.md, log.md\n",
    )
    return domain


def migrate_source(source: Path, domain: Path) -> None:
    (source / "notes" / "llm-wiki.md").read_text(encoding="utf-8")

    extras = domain / "Extras" / "old-obsidian"
    extras.mkdir(parents=True, exist_ok=True)
    (extras / "diagram.png").write_bytes(b"fake image bytes for migration smoke test")

    write(
        domain / "Sources" / "old-obsidian-llm-wiki.md",
        f"""---
title: Old Obsidian LLM Wiki Note
created: {TODAY}
updated: {TODAY}
type: source
tags: [source, wiki]
confidence: medium
status: active
sources: []
contested: false
contradictions: []
---

# Old Obsidian LLM Wiki Note

The imported note connects [[compounding-wiki]] and [[obsidian]] for this domain.
Local attachment: `Extras/old-obsidian/diagram.png`.
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
sources: ["[[old-obsidian-llm-wiki]]"]
contested: false
contradictions: []
---

# Compounding Wiki

A compounding wiki turns repeated source processing into durable knowledge. It is
grounded by [[old-obsidian-llm-wiki]] and maintained with [[obsidian]].
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
sources: ["[[old-obsidian-llm-wiki]]"]
contested: false
contradictions: []
---

# Obsidian

Obsidian is the editor used to browse [[compounding-wiki]] notes and imported
source material such as [[old-obsidian-llm-wiki]].
""",
    )
    write(
        domain / "index.md",
        "# Domain Index\n\n"
        f"> Last updated: {TODAY} | Total pages: 3\n\n"
        "## Atlas\n\n"
        "## Cards\n"
        "- [[compounding-wiki]] - Durable knowledge that compounds from repeated source processing.\n\n"
        "## Sources\n"
        "- [[old-obsidian-llm-wiki]] - Migrated source note from old Obsidian vault.\n\n"
        "## Spaces\n"
        "- [[obsidian]] - Tool used to browse and edit the wiki.\n",
    )
    with (domain / "log.md").open("a", encoding="utf-8") as handle:
        handle.write(
            f"\n## {TODAY} | ingest | old-obsidian migration\n"
            "- source_alias: old-obsidian\n"
            "- import_scope: notes/llm-wiki.md and attachment metadata\n"
            "- created: Sources/old-obsidian-llm-wiki.md\n"
            "- created: Cards/compounding-wiki.md\n"
            "- created: Spaces/obsidian.md\n"
            "- created: Extras/old-obsidian/diagram.png\n"
            "- updated: index.md\n"
        )


def assert_valid(domain: Path) -> None:
    issues = validate_domain(domain)
    if issues:
        lines = "\n".join(issue.line() for issue in issues)
        raise AssertionError(f"{domain} is invalid:\n{lines}")


def assert_skill_example_is_generic() -> None:
    skill = (REPO_ROOT / "skills" / "loreforge-wiki" / "SKILL.md").read_text(encoding="utf-8")
    forbidden = ["/home/cambricon", "Nutstore", "OldVault"]
    found = [value for value in forbidden if value in skill]
    if found:
        raise AssertionError(f"skill example contains environment-specific values: {found}")
    for expected in ["/path/to/loreforge-wiki", "/path/to/source-vault"]:
        if expected not in skill:
            raise AssertionError(f"skill example is missing placeholder path: {expected}")
    for expected in [".obsidian*", ".obsidian-desktop", ".obsidian-mobile"]:
        if expected not in skill:
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

        write(
            home / ".config" / "loreforge" / "registry.toml",
            f"""default = "main"

[[wikis]]
name = "main"
path = "{wiki.as_posix()}"
description = "Temp LoreForge wiki"
sync = "local"
default_domain = "ai-research"
remote = ""

[[wikis]]
name = "systems"
path = "{named_wiki.as_posix()}"
description = "Named wiki"
sync = "local"
default_domain = "ml-systems"
remote = ""

[[sources]]
name = "old-obsidian"
kind = "obsidian-vault"
path = "{source.as_posix()}"
default_target_wiki = "main"
default_target_domain = "ai-research"
""",
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
        assert "ai-research" in (wiki / "00_System" / "domains.md").read_text(encoding="utf-8")
        print("PASS initialization: 00_System and native domain contract created")

        source_before = digest_tree(source)
        migrate_source(source, domain)
        if source_before != digest_tree(source):
            raise AssertionError("source vault changed during migration")
        assert_valid(domain)
        assert (domain / "Extras" / "old-obsidian" / "diagram.png").exists()
        assert "source_alias: old-obsidian" in (domain / "log.md").read_text(encoding="utf-8")
        print("PASS migration: source stayed read-only and target domain remains valid")

    print("wiki config flow smoke test ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

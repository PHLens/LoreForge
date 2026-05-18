#!/usr/bin/env python3
"""Smoke-test LoreForge's read-only external component contract."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "skills" / "loreforge-domain" / "scripts" / "loreforge_component.py"


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, SCRIPT.as_posix(), *args],
        check=check,
        capture_output=True,
        text=True,
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def seed_domain(wiki: Path, domain: str = "ai-research") -> None:
    domain_root = wiki / "Domains" / domain
    write(
        domain_root / "SCHEMA.md",
        """# AI Research

## Tag Taxonomy
- topic: agent
""",
    )
    write(domain_root / "index.md", "# Index\n")
    write(domain_root / "log.md", "# Log\n")
    (domain_root / "Atlas").mkdir(parents=True)
    (domain_root / "Cards").mkdir(parents=True)
    (domain_root / "Spaces").mkdir(parents=True)
    (wiki / "Shared" / "Raw").mkdir(parents=True)


def test_status_contract() -> None:
    with tempfile.TemporaryDirectory(prefix="loreforge-component-") as tmp:
        root = Path(tmp)
        wiki = root / "wiki"
        seed_domain(wiki)
        registry = root / "registry.toml"
        write(
            registry,
            f'''default = "main"

[[wikis]]
name = "main"
path = "{wiki.as_posix()}"
description = "test wiki"
sync = "local"
remote = ""
default_domain = "ai-research"
sync_bootstrapped = false
''',
        )
        result = run("status", "--registry", registry.as_posix(), "--json")
        payload = json.loads(result.stdout)
        assert payload["component"] == "loreforge"
        assert payload["contract_version"] == "0.1"
        assert payload["operation"] == "status"
        assert payload["ok"] is True
        assert payload["selected_wiki"]["domains"] == ["ai-research"]


def test_validate_contract() -> None:
    with tempfile.TemporaryDirectory(prefix="loreforge-component-") as tmp:
        wiki = Path(tmp) / "wiki"
        seed_domain(wiki)
        result = run("validate", "--wiki", wiki.as_posix(), "--domain", "ai-research", "--json")
        payload = json.loads(result.stdout)
        assert payload["ok"] is True
        assert payload["domains"][0]["ok"] is True


def test_init_is_read_only_plan() -> None:
    with tempfile.TemporaryDirectory(prefix="loreforge-component-") as tmp:
        wiki = Path(tmp) / "planned-wiki"
        result = run(
            "init",
            "--wiki",
            wiki.as_posix(),
            "--domain",
            "ai-research",
            "--sync",
            "rclone",
            "--remote",
            "wiki-webdav:LoreForgeWiki",
            "--json",
        )
        payload = json.loads(result.stdout)
        assert payload["ok"] is True
        assert payload["writes"] is False
        assert not wiki.exists()
        assert payload["registry_entry"]["sync"] == "rclone"


if __name__ == "__main__":
    test_status_contract()
    test_validate_contract()
    test_init_is_read_only_plan()
    print("LoreForge component contract tests passed.")

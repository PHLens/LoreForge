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


def seed_valid_paper_note(wiki: Path) -> None:
    bundle = wiki / "Shared" / "Zotero" / "examplePaper2026"
    write(bundle / "examplePaper2026 - Example Paper.pdf", "%PDF placeholder\n")
    write(
        bundle / "examplePaper2026.md",
        """---
citekey: examplePaper2026
title: "Example Paper"
aliases:
  - Example Paper
authors: "Ada Lovelace"
date: "2026"
category: "Example"
keywords:
  - example
conference: "ExampleConf 2026"
link: "https://example.com/paper"
create_date: "2026/01/01 00:00:00"
zotero_link: ""
zotero_folder:
  - Papers
abstract: "Example abstract."
tags: []
$version: 1
$libraryID: 1
$itemKey: EXAMPLE
---

# Example Paper

[[examplePaper2026 - Example Paper.pdf|PDF]]

## Summary

### What's the problem?

Example problem.

### How does this paper solved it?

Example mechanism.

### What's the improvements?

Example improvement.

## Strengths

Example strengths.

## Weakness

Example weakness.

## Detailed Comments

Example details.

## Ideas for improvement(How Can I do better)

Example improvement ideas.

## Lessons learned

Example lessons.
""",
    )


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
        seed_valid_paper_note(wiki)
        result = run("validate", "--wiki", wiki.as_posix(), "--domain", "ai-research", "--json")
        payload = json.loads(result.stdout)
        assert payload["ok"] is True
        assert payload["domains"][0]["ok"] is True


def test_validate_reports_paper_note_format_errors() -> None:
    with tempfile.TemporaryDirectory(prefix="loreforge-component-") as tmp:
        wiki = Path(tmp) / "wiki"
        seed_domain(wiki)
        write(
            wiki / "Shared" / "Zotero" / "badPaper" / "wrong-name.md",
            """---
citekey: otherPaper
title: "Bad Paper"
aliases: []
tags: []
---

This body intentionally lacks the paper-note shape.
""",
        )

        result = run("validate", "--wiki", wiki.as_posix(), "--domain", "ai-research", "--json", check=False)
        assert result.returncode == 1
        payload = json.loads(result.stdout)
        issues = payload["domains"][0]["issues"]
        codes = {item["code"] for item in issues}
        assert "paper-note-name-mismatch" in codes
        assert "paper-note-citekey-mismatch" in codes
        assert "missing-paper-field" in codes
        assert "missing-paper-pdf" in codes
        assert "missing-paper-pdf-link" in codes
        assert "missing-paper-heading" in codes
        assert "missing-paper-section" in codes


def test_validate_ignores_legacy_directory() -> None:
    with tempfile.TemporaryDirectory(prefix="loreforge-component-") as tmp:
        wiki = Path(tmp) / "wiki"
        seed_domain(wiki)
        write(wiki / "90-Legacy" / "bad-note.md", "# Missing frontmatter in ignored legacy note\n")
        write(wiki / "Domains" / "ai-research" / "index.md", "# Index\n- [[legacy-pointer]]\n")
        write(
            wiki / "Domains" / "ai-research" / "Cards" / "legacy-pointer.md",
            """---
title: Legacy Pointer
created: 2026-01-01
updated: 2026-01-01
type: concept
aliases:
  - Legacy pointer
tags: [agent]
status: active
---

# Legacy Pointer

Legacy imports can be named without making the legacy vault part of validation: [[90-Legacy/missing-page]].
""",
        )

        result = run("validate", "--wiki", wiki.as_posix(), "--domain", "ai-research", "--json")
        payload = json.loads(result.stdout)
        assert payload["ok"] is True


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


def test_cli_setup_writes_bootstrap_files() -> None:
    with tempfile.TemporaryDirectory(prefix="loreforge-component-") as tmp:
        root = Path(tmp)
        wiki = root / "wiki"
        registry = root / "registry.toml"
        result = subprocess.run(
            [
                "node",
                (REPO_ROOT / "bin" / "loreforge").as_posix(),
                "setup",
                "--wiki",
                wiki.as_posix(),
                "--domain",
                "ai-research",
                "--registry",
                registry.as_posix(),
                "--json",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        assert payload["component"] == "loreforge"
        assert payload["operation"] == "setup"
        assert payload["ok"] is True
        assert payload["validation"]["ok"] is True
        assert (wiki / "00_System" / "index.md").exists()
        assert (wiki / "Shared" / "Templates" / "weekly.md").exists()
        assert not (wiki / "Shared" / "Templates" / "card.md").exists()
        assert not (wiki / "Shared" / "Templates" / "moc.md").exists()
        assert not (wiki / "Shared" / "Templates" / "relationship.md").exists()
        assert (wiki / "Domains" / "ai-research" / "SCHEMA.md").exists()
        assert "default_domain = \"ai-research\"" in registry.read_text(encoding="utf-8")


if __name__ == "__main__":
    test_status_contract()
    test_validate_contract()
    test_validate_reports_paper_note_format_errors()
    test_validate_ignores_legacy_directory()
    test_init_is_read_only_plan()
    test_cli_setup_writes_bootstrap_files()
    print("LoreForge component contract tests passed.")

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
sys.path.insert(0, str(REPO_ROOT / "lib"))

from loreforge_validator import Issue, fix_orphan_footnotes, validate_domain


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
    (wiki / "Shared" / "Raw").mkdir(parents=True, exist_ok=True)


def seed_research_paper_space(wiki: Path) -> None:
    domain_root = wiki / "Domains" / "research"
    write(
        domain_root / "SCHEMA.md",
        """# Research

## Tag Taxonomy
- topic: paper
""",
    )
    write(domain_root / "index.md", "# Index\n")
    write(domain_root / "log.md", "# Log\n")
    (domain_root / "Atlas").mkdir(parents=True)
    (domain_root / "Cards").mkdir(parents=True)
    (domain_root / "Spaces" / "papers").mkdir(parents=True)


def seed_valid_paper_note(wiki: Path) -> None:
    seed_research_paper_space(wiki)
    papers = wiki / "Domains" / "research" / "Spaces" / "papers"
    write_valid_paper_note(papers)


def write_valid_paper_note(papers: Path) -> None:
    write(
        papers / "examplePaper2026.md",
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
zotero_link: "zotero://open-pdf/0_EXAMPLE"
zotero_folder:
  - Papers
abstract: "Example abstract."
tags: []
$version: 1
$libraryID: 1
$itemKey: EXAMPLE
---

# Example Paper

[PDF](zotero://open-pdf/0_EXAMPLE)

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


def seed_root_card_wiki(wiki: Path) -> None:
    write(
        wiki / "00_System" / "card-domains.md",
        """# Card Domain Details

## Global Rules

- Tags are domain-internal classification labels.

## cs

Computer science.

Tag taxonomy:

- agent, gpu, source
""",
    )
    write(
        wiki / "00_System" / "domains.md",
        """# Card Domains

| Domain | Directory | Purpose | Default Language | Status |
|---|---|---|---|---|
| cs | `Cards/cs/` | Computer science | 中文 | active |
""",
    )
    write(
        wiki / "Cards" / "cs" / "agent-card.md",
        """---
title: Agent Card
created: 2026-01-01
updated: 2026-01-01
type: concept
aliases:
  - Agent system card
tags: [agent]
status: active
---

# Agent Card

Agent card content cites a new-layout raw package.[^source]

[^source]: [[Sources/Raw/agent-card-source/manifest]]
""",
    )
    raw = wiki / "Sources" / "Raw" / "agent-card-source"
    write(raw / "origin.md", "Raw source for the root Cards layout.\n")
    digest = __import__("hashlib").sha256((raw / "origin.md").read_bytes()).hexdigest()
    write(
        raw / "manifest.md",
        f"""---
title: Agent Card Source
source_id: agent-card-source
source_type: local note
source_language: en
retrieved_at: 2026-01-01
source_description: New layout source
content_hash: {digest}
origin: Sources/Raw/agent-card-source/origin.md
candidate_domains:
  - cs
compiled_pages:
  - Cards/cs/agent-card.md
status: compiled
---

# Agent Card Source
""",
    )
    write_valid_paper_note(wiki / "Sources" / "Papers")


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
        result = run("validate", "--wiki", wiki.as_posix(), "--all-domains", "--json")
        payload = json.loads(result.stdout)
        assert payload["ok"] is True
        domains = {item["name"]: item for item in payload["domains"]}
        assert domains["ai-research"]["ok"] is True
        assert domains["research"]["ok"] is True


def test_validate_root_cards_layout_contract() -> None:
    with tempfile.TemporaryDirectory(prefix="loreforge-component-") as tmp:
        wiki = Path(tmp) / "wiki"
        seed_root_card_wiki(wiki)
        result = run("validate", "--wiki", wiki.as_posix(), "--all-domains", "--json")
        payload = json.loads(result.stdout)
        assert payload["ok"] is True
        assert payload["domains"] == [
            {
                "issues": [],
                "name": "cs",
                "ok": True,
                "path": (wiki / "Cards" / "cs").as_posix(),
            }
        ]


def test_validate_all_domains_includes_mixed_root_and_legacy_layouts() -> None:
    with tempfile.TemporaryDirectory(prefix="loreforge-component-") as tmp:
        wiki = Path(tmp) / "wiki"
        seed_root_card_wiki(wiki)
        seed_domain(wiki, "legacy-research")
        seed_domain(wiki, "cs")
        result = run("validate", "--wiki", wiki.as_posix(), "--all-domains", "--json")
        payload = json.loads(result.stdout)
        assert payload["ok"] is True
        paths = {item["path"] for item in payload["domains"]}
        assert paths == {
            (wiki / "Cards" / "cs").as_posix(),
            (wiki / "Domains" / "cs").as_posix(),
            (wiki / "Domains" / "legacy-research").as_posix(),
        }

        status = run("status", "--wiki", wiki.as_posix(), "--json")
        status_payload = json.loads(status.stdout)
        assert status_payload["selected_wiki"]["domains"] == ["cs", "legacy-research"]
        assert status_payload["selected_wiki"]["domain_entries"] == [
            {
                "layout": "root-cards",
                "name": "cs",
                "path": (wiki / "Cards" / "cs").as_posix(),
            },
            {
                "layout": "legacy-domains",
                "name": "cs",
                "path": (wiki / "Domains" / "cs").as_posix(),
            },
            {
                "layout": "legacy-domains",
                "name": "legacy-research",
                "path": (wiki / "Domains" / "legacy-research").as_posix(),
            },
        ]


def test_validate_rejects_unsafe_domain_name() -> None:
    with tempfile.TemporaryDirectory(prefix="loreforge-component-") as tmp:
        wiki = Path(tmp) / "wiki"
        seed_root_card_wiki(wiki)
        result = run("validate", "--wiki", wiki.as_posix(), "--domain", "../../outside", "--json", check=False)
        assert result.returncode == 1
        payload = json.loads(result.stdout)
        assert payload["issues"][0]["code"] == "invalid-domain-name"
        assert payload["issues"][0]["path"] == "../../outside"
        assert payload["domains"] == []


def test_init_rejects_unsafe_domain_name() -> None:
    with tempfile.TemporaryDirectory(prefix="loreforge-component-") as tmp:
        wiki = Path(tmp) / "planned-wiki"
        result = run("init", "--wiki", wiki.as_posix(), "--domain", "../../outside", "--json", check=False)
        assert result.returncode == 1
        payload = json.loads(result.stdout)
        assert payload["issues"][0]["code"] == "invalid-domain-name"
        assert payload["issues"][0]["path"] == "../../outside"
        assert payload["writes"] is False
        assert "actions" not in payload
        assert not wiki.exists()


def test_validate_rejects_wikilink_parent_path_components() -> None:
    with tempfile.TemporaryDirectory(prefix="loreforge-component-") as tmp:
        wiki = Path(tmp) / "wiki"
        seed_root_card_wiki(wiki)
        (wiki / "Cards" / "other").mkdir(parents=True)
        write(
            wiki / "Cards" / "other" / "secret.md",
            """---
title: Secret
created: 2026-01-01
updated: 2026-01-01
type: card
aliases:
  - hidden other domain card
tags: []
status: active
---

# Secret
""",
        )
        card = wiki / "Cards" / "cs" / "agent-card.md"
        card.write_text(
            card.read_text(encoding="utf-8")
            + "\nThis should not cross domains via [[Cards/cs/../other/secret]].\n",
            encoding="utf-8",
        )

        result = run("validate", "--wiki", wiki.as_posix(), "--domain", "cs", "--json", check=False)
        assert result.returncode == 1
        payload = json.loads(result.stdout)
        issues = payload["domains"][0]["issues"]
        assert any(item["code"] == "cross-domain-link" for item in issues)
        assert not any(
            item["code"] == "broken-wikilink" and "Cards/cs/../other/secret" in item["message"]
            for item in issues
        )


def test_validate_root_atlas_and_spaces_pages() -> None:
    with tempfile.TemporaryDirectory(prefix="loreforge-component-") as tmp:
        wiki = Path(tmp) / "wiki"
        seed_root_card_wiki(wiki)
        write(
            wiki / "Atlas" / "bad-view.md",
            """---
title: Bad View
created: 2026-01-01
updated: 2026-01-01
type: map
tags: []
status: active
sources: []
---

# Bad View

Root Atlas pages should be validated with compiled-page rules.
""",
        )
        write(
            wiki / "Spaces" / "projects" / "bad-work-item.md",
            """---
title: Bad Work Item
created: 2026-01-01
updated: 2026-01-01
type: space
tags: []
status: active
---

# Bad Work Item

This should not cross root paths with [[Spaces/projects/../private-note]].
""",
        )
        write(
            wiki / "Sources" / "bad-source-note.md",
            """---
title: Bad Source Note
created: 2026-01-01
updated: 2026-01-01
type: source
tags: []
status: active
sources: []
---

# Bad Source Note

Root source notes should also be validated with compiled-page rules.
""",
        )
        write(
            wiki / "Spaces" / "private-note.md",
            """---
title: Private Note
created: 2026-01-01
updated: 2026-01-01
type: space
tags: []
status: active
---

# Private Note
""",
        )

        result = run("validate", "--wiki", wiki.as_posix(), "--domain", "cs", "--json", check=False)
        assert result.returncode == 1
        payload = json.loads(result.stdout)
        issues = payload["domains"][0]["issues"]
        assert any(
            item["code"] == "deprecated-frontmatter-field" and item["path"] == "Atlas/bad-view.md"
            for item in issues
        )
        assert any(
            item["code"] == "deprecated-frontmatter-field" and item["path"] == "Sources/bad-source-note.md"
            for item in issues
        )
        assert any(
            item["code"] == "cross-domain-link" and item["path"] == "Spaces/projects/bad-work-item.md"
            for item in issues
        )


def test_fix_orphan_footnotes_reports_root_layout_paths() -> None:
    with tempfile.TemporaryDirectory(prefix="loreforge-component-") as tmp:
        wiki = Path(tmp) / "wiki"
        seed_root_card_wiki(wiki)
        write(
            wiki / "Atlas" / "view.md",
            """---
title: View
created: 2026-01-01
updated: 2026-01-01
type: map
tags: []
status: active
---

# View

Useful view content.

[^orphan]: This orphan should be removed.
""",
        )

        changed = fix_orphan_footnotes(wiki / "Cards" / "cs")
        assert changed == ["Atlas/view.md"]
        assert "[^orphan]" not in (wiki / "Atlas" / "view.md").read_text(encoding="utf-8")


def test_validate_root_cards_rejects_nested_markdown() -> None:
    with tempfile.TemporaryDirectory(prefix="loreforge-component-") as tmp:
        wiki = Path(tmp) / "wiki"
        seed_root_card_wiki(wiki)
        write(
            wiki / "Cards" / "cs" / "nested" / "bad-card.md",
            """---
title: Bad Nested Card
created: 2026-01-01
updated: 2026-01-01
type: card
aliases:
  - nested misplaced card
tags: [agent]
status: active
---

# Bad Nested Card

Nested Card pages should still be validated and rejected.
""",
        )
        write(
            wiki / "Cards" / "cs" / "nested" / "index.md",
            """---
title: Bad Nested Index
created: 2026-01-01
updated: 2026-01-01
type: card
aliases:
  - nested misplaced index
tags: [agent]
status: active
---

# Bad Nested Index

Nested system-like Markdown names should not bypass root Cards layout checks.
""",
        )
        result = run("validate", "--wiki", wiki.as_posix(), "--domain", "cs", "--json", check=False)
        assert result.returncode == 1
        payload = json.loads(result.stdout)
        issues = payload["domains"][0]["issues"]
        codes = {item["code"] for item in issues}
        assert "nested-card-page" in codes
        nested_paths = {item["path"] for item in issues if item["code"] == "nested-card-page"}
        assert {"Cards/cs/nested/bad-card.md", "Cards/cs/nested/index.md"} <= nested_paths


def test_validate_root_cards_requires_card_domain_policy() -> None:
    with tempfile.TemporaryDirectory(prefix="loreforge-component-") as tmp:
        wiki = Path(tmp) / "wiki"
        seed_root_card_wiki(wiki)
        (wiki / "Cards" / "unregistered").mkdir(parents=True)
        write(
            wiki / "Cards" / "unregistered" / "agent-card.md",
            """---
title: Agent Card
created: 2026-01-01
updated: 2026-01-01
type: card
aliases:
  - unregistered agent card
tags: []
status: active
---

# Agent Card

Unregistered domains should not validate as fully configured.
""",
        )
        result = run("validate", "--wiki", wiki.as_posix(), "--domain", "unregistered", "--json", check=False)
        assert result.returncode == 1
        payload = json.loads(result.stdout)
        codes = {item["code"] for item in payload["domains"][0]["issues"]}
        assert "missing-card-domain-policy" in codes


def test_shared_validator_module_importable() -> None:
    domain = REPO_ROOT / "tests" / "fixtures" / "native-domain" / "valid" / "wiki" / "Domains" / "ai-research"
    issues = validate_domain(domain)
    assert issues == []
    assert Issue("code", "path", "message").line() == "code: path: message"


def test_validate_reports_paper_note_format_errors() -> None:
    with tempfile.TemporaryDirectory(prefix="loreforge-component-") as tmp:
        wiki = Path(tmp) / "wiki"
        seed_domain(wiki)
        seed_research_paper_space(wiki)
        write(
            wiki / "Domains" / "research" / "Spaces" / "papers" / "wrong-name.md",
            """---
citekey: otherPaper
title: "Bad Paper"
aliases: []
tags: []
---

This body intentionally lacks the paper-note shape.
""",
        )

        result = run("validate", "--wiki", wiki.as_posix(), "--domain", "research", "--json", check=False)
        assert result.returncode == 1
        payload = json.loads(result.stdout)
        issues = payload["domains"][0]["issues"]
        codes = {item["code"] for item in issues}
        assert "paper-note-name-mismatch" in codes
        assert "paper-note-citekey-mismatch" in codes
        assert "missing-paper-field" in codes
        assert "missing-zotero-link" in codes
        assert "missing-paper-pdf-link" in codes
        assert "missing-paper-heading" in codes
        assert "missing-paper-section" in codes


def test_validate_reports_root_paper_errors_from_any_card_domain() -> None:
    with tempfile.TemporaryDirectory(prefix="loreforge-component-") as tmp:
        wiki = Path(tmp) / "wiki"
        seed_root_card_wiki(wiki)
        write(
            wiki / "Sources" / "Papers" / "badPaper.md",
            """---
citekey: otherPaper
title: "Bad Paper"
aliases: []
tags: []
---

This body intentionally lacks the paper-note shape.
""",
        )

        result = run("validate", "--wiki", wiki.as_posix(), "--domain", "cs", "--json", check=False)
        assert result.returncode == 1
        payload = json.loads(result.stdout)
        issues = payload["domains"][0]["issues"]
        codes = {item["code"] for item in issues}
        assert "paper-note-name-mismatch" in codes
        assert "missing-paper-field" in codes
        assert any(item["path"].startswith("Sources/Papers/") for item in issues)


def test_validate_checks_root_and_legacy_paper_notes_when_both_exist() -> None:
    with tempfile.TemporaryDirectory(prefix="loreforge-component-") as tmp:
        wiki = Path(tmp) / "wiki"
        seed_root_card_wiki(wiki)
        seed_research_paper_space(wiki)
        write_valid_paper_note(wiki / "Sources" / "Papers")
        write(
            wiki / "Domains" / "research" / "Spaces" / "papers" / "badLegacyPaper.md",
            """---
citekey: otherPaper
title: "Bad Legacy Paper"
aliases: []
tags: []
---

This body intentionally lacks the paper-note shape.
""",
        )

        result = run("validate", "--wiki", wiki.as_posix(), "--domain", "cs", "--json", check=False)
        assert result.returncode == 1
        payload = json.loads(result.stdout)
        issues = payload["domains"][0]["issues"]
        assert any(item["path"].startswith("Domains/research/Spaces/papers/") for item in issues)
        assert "paper-note-name-mismatch" in {item["code"] for item in issues}


def test_validate_checks_root_and_legacy_raw_roots_when_both_exist() -> None:
    with tempfile.TemporaryDirectory(prefix="loreforge-component-") as tmp:
        wiki = Path(tmp) / "wiki"
        seed_root_card_wiki(wiki)
        (wiki / "Sources" / "Raw").mkdir(parents=True, exist_ok=True)
        write(
            wiki / "Shared" / "Raw" / "legacy-bad" / "manifest.md",
            """---
title: "Legacy Bad"
source_id: different-id
source_type: file
source_language: en
retrieved_at: 2026-01-01
source_description: legacy bad raw package
content_hash: bad
origin: Shared/Raw/legacy-bad/origin.md
candidate_domains: []
compiled_pages: []
status: captured
---
""",
        )
        write(wiki / "Shared" / "Raw" / "legacy-bad" / "origin.md", "legacy content\n")

        result = run("validate", "--wiki", wiki.as_posix(), "--domain", "cs", "--json", check=False)
        assert result.returncode == 1
        payload = json.loads(result.stdout)
        issues = payload["domains"][0]["issues"]
        assert any(item["path"].startswith("Shared/Raw/legacy-bad/") for item in issues)
        assert "raw-source-id-mismatch" in {item["code"] for item in issues}


def test_validate_rejects_malformed_zotero_pdf_links() -> None:
    with tempfile.TemporaryDirectory(prefix="loreforge-component-") as tmp:
        wiki = Path(tmp) / "wiki"
        seed_domain(wiki)
        seed_research_paper_space(wiki)
        write(
            wiki / "Domains" / "research" / "Spaces" / "papers" / "badPdfLink.md",
            """---
citekey: badPdfLink
title: "Bad PDF Link"
aliases:
  - Bad PDF Link
authors: "Ada Lovelace"
date: "2026"
category: "Example"
keywords: []
conference: "ExampleConf"
link: "https://example.com/bad"
create_date: "2026/01/01 00:00:00"
zotero_link: "zotero://select/library/items/BADPDF"
zotero_folder: []
abstract: "Example abstract."
tags: []
$version: 1
$libraryID: 1
$itemKey: BADPDF
---

# Bad PDF Link

[[badPdfLink - Bad PDF Link.pdf|PDF]]

zotero://select/library/items/BADPDF

## Summary

### What's the problem?

Invalid link shape.

### How does this paper solved it?

It does not use a Zotero PDF jump.

### What's the improvements?

None.

## Strengths

Focused invalid fixture.

## Weakness

Invalid PDF link.

## Detailed Comments

This body has no `[PDF](zotero://open-pdf/...)` link.

## Ideas for improvement(How Can I do better)

Use a Zotero open-pdf link.

## Lessons learned

Validate the body link shape.
""",
        )

        result = run("validate", "--wiki", wiki.as_posix(), "--domain", "research", "--json", check=False)
        assert result.returncode == 1
        payload = json.loads(result.stdout)
        codes = {item["code"] for item in payload["domains"][0]["issues"]}
        assert "missing-zotero-link" in codes
        assert "missing-paper-pdf-link" in codes


def test_validate_rejects_bare_zotero_pdf_uri_without_markdown_pdf_link() -> None:
    with tempfile.TemporaryDirectory(prefix="loreforge-component-") as tmp:
        wiki = Path(tmp) / "wiki"
        seed_domain(wiki)
        seed_research_paper_space(wiki)
        write(
            wiki / "Domains" / "research" / "Spaces" / "papers" / "barePdfUri.md",
            """---
citekey: barePdfUri
title: "Bare PDF URI"
aliases:
  - Bare PDF URI
authors: "Ada Lovelace"
date: "2026"
category: "Example"
keywords: []
conference: "ExampleConf"
link: "https://example.com/bare"
create_date: "2026/01/01 00:00:00"
zotero_link: "zotero://open-pdf/0_BAREPDF"
zotero_folder: []
abstract: "Example abstract."
tags: []
$version: 1
$libraryID: 1
$itemKey: BAREPDF
---

# Bare PDF URI

zotero://open-pdf/0_BAREPDF

## Summary

### What's the problem?

The body has a bare Zotero PDF URI but no Markdown PDF link.

### How does this paper solved it?

It does not.

### What's the improvements?

None.

## Strengths

Focused invalid fixture.

## Weakness

Missing Markdown PDF link.

## Detailed Comments

The frontmatter URI is valid, but the body link contract is not satisfied.

## Ideas for improvement(How Can I do better)

Use `[PDF](zotero://open-pdf/...)`.

## Lessons learned

Validation must require the Markdown PDF link shape.
""",
        )

        result = run("validate", "--wiki", wiki.as_posix(), "--domain", "research", "--json", check=False)
        assert result.returncode == 1
        payload = json.loads(result.stdout)
        codes = {item["code"] for item in payload["domains"][0]["issues"]}
        assert "missing-zotero-link" not in codes
        assert "missing-paper-pdf-link" in codes


def test_validate_rejects_mismatched_zotero_pdf_link_target() -> None:
    with tempfile.TemporaryDirectory(prefix="loreforge-component-") as tmp:
        wiki = Path(tmp) / "wiki"
        seed_domain(wiki)
        seed_research_paper_space(wiki)
        write(
            wiki / "Domains" / "research" / "Spaces" / "papers" / "mismatchedPdfUri.md",
            """---
citekey: mismatchedPdfUri
title: "Mismatched PDF URI"
aliases:
  - Mismatched PDF URI
authors: "Ada Lovelace"
date: "2026"
category: "Example"
keywords: []
conference: "ExampleConf"
link: "https://example.com/mismatch"
create_date: "2026/01/01 00:00:00"
zotero_link: "zotero://open-pdf/0_EXPECTED"
zotero_folder: []
abstract: "Example abstract."
tags: []
$version: 1
$libraryID: 1
$itemKey: MISMATCH
---

# Mismatched PDF URI

[PDF](zotero://open-pdf/0_OTHER)

## Summary

### What's the problem?

The body opens a different Zotero attachment than frontmatter.

### How does this paper solved it?

It does not.

### What's the improvements?

None.

## Strengths

Focused invalid fixture.

## Weakness

Mismatched PDF target.

## Detailed Comments

The body PDF link must equal `zotero_link`.

## Ideas for improvement(How Can I do better)

Use the same open-pdf URI in frontmatter and body.

## Lessons learned

Validation must compare the two URI values.
""",
        )

        result = run("validate", "--wiki", wiki.as_posix(), "--domain", "research", "--json", check=False)
        assert result.returncode == 1
        payload = json.loads(result.stdout)
        codes = {item["code"] for item in payload["domains"][0]["issues"]}
        assert "missing-zotero-link" not in codes
        assert "missing-paper-pdf-link" in codes


def test_validate_rejects_nested_paper_notes() -> None:
    with tempfile.TemporaryDirectory(prefix="loreforge-component-") as tmp:
        wiki = Path(tmp) / "wiki"
        seed_domain(wiki)
        seed_research_paper_space(wiki)
        write(
            wiki / "Domains" / "research" / "Spaces" / "papers" / "nestedPaper" / "nestedPaper.md",
            """---
citekey: nestedPaper
title: "Nested Paper"
aliases:
  - Nested Paper
authors: "Ada Lovelace"
date: "2026"
category: "Example"
keywords: []
conference: "ExampleConf"
link: "https://example.com/nested"
create_date: "2026/01/01 00:00:00"
zotero_link: "zotero://open-pdf/0_NESTED"
zotero_folder: []
abstract: "Example abstract."
tags: []
$version: 1
$libraryID: 1
$itemKey: NESTED
---

# Nested Paper

[PDF](zotero://open-pdf/0_NESTED)

## Summary

### What's the problem?

Nested location.

### How does this paper solved it?

It is nested.

### What's the improvements?

None.

## Strengths

Focused invalid fixture.

## Weakness

Nested location.

## Detailed Comments

Nested notes are not allowed.

## Ideas for improvement(How Can I do better)

Move it to the flat papers directory.

## Lessons learned

Paper notes should be flat files.
""",
        )

        result = run("validate", "--wiki", wiki.as_posix(), "--domain", "research", "--json", check=False)
        assert result.returncode == 1
        payload = json.loads(result.stdout)
        codes = {item["code"] for item in payload["domains"][0]["issues"]}
        assert "paper-note-location" in codes


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
  - Legacy import pointer
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


def test_validate_rejects_title_only_card_aliases() -> None:
    with tempfile.TemporaryDirectory(prefix="loreforge-component-") as tmp:
        wiki = Path(tmp) / "wiki"
        seed_domain(wiki)
        write(wiki / "Domains" / "ai-research" / "index.md", "# Index\n- [[alias-card]]\n")
        write(
            wiki / "Domains" / "ai-research" / "Cards" / "alias-card.md",
            """---
title: Alias Card
created: 2026-01-01
updated: 2026-01-01
type: concept
aliases:
  - Alias Card!
  - alias-card?
tags: [agent]
status: active
---

# Alias Card

This card only repeats its title and page stem as aliases with punctuation-only variants.
""",
        )

        result = run("validate", "--wiki", wiki.as_posix(), "--domain", "ai-research", "--json", check=False)
        assert result.returncode == 1
        payload = json.loads(result.stdout)
        codes = {item["code"] for item in payload["domains"][0]["issues"]}
        assert "uninformative-card-aliases" in codes


def test_validate_rejects_redundant_card_aliases() -> None:
    with tempfile.TemporaryDirectory(prefix="loreforge-component-") as tmp:
        wiki = Path(tmp) / "wiki"
        seed_domain(wiki)
        write(wiki / "Domains" / "ai-research" / "index.md", "# Index\n- [[alias-card]]\n")
        write(
            wiki / "Domains" / "ai-research" / "Cards" / "alias-card.md",
            """---
title: Alias Card
created: 2026-01-01
updated: 2026-01-01
type: concept
aliases:
  - Alias Card
  - Agent alias pattern
tags: [agent]
status: active
---

# Alias Card

This card has one useful alias and one alias that only repeats its title.
""",
        )

        result = run("validate", "--wiki", wiki.as_posix(), "--domain", "ai-research", "--json", check=False)
        assert result.returncode == 1
        payload = json.loads(result.stdout)
        issues = payload["domains"][0]["issues"]
        assert "redundant-card-aliases" in {item["code"] for item in issues}
        assert any("Alias Card" in item["message"] for item in issues)


def test_validate_accepts_path_qualified_index_links() -> None:
    with tempfile.TemporaryDirectory(prefix="loreforge-component-") as tmp:
        wiki = Path(tmp) / "wiki"
        seed_domain(wiki)
        write(wiki / "Domains" / "ai-research" / "index.md", "# Index\n- [[Cards/path-card|Path Card]]\n")
        write(
            wiki / "Domains" / "ai-research" / "Cards" / "path-card.md",
            """---
title: Path Card
created: 2026-01-01
updated: 2026-01-01
type: concept
aliases:
  - Path-qualified card
tags: [agent]
status: active
---

# Path Card

Index entries may use domain-relative paths when a merged domain needs stable link identity.
""",
        )

        result = run("validate", "--wiki", wiki.as_posix(), "--domain", "ai-research", "--json")
        payload = json.loads(result.stdout)
        assert payload["ok"] is True


def test_validate_rejects_ambiguous_bare_wikilinks_for_duplicate_stems() -> None:
    with tempfile.TemporaryDirectory(prefix="loreforge-component-") as tmp:
        wiki = Path(tmp) / "wiki"
        seed_domain(wiki)
        write(
            wiki / "Domains" / "ai-research" / "index.md",
            "# Index\n"
            "- [[Spaces/projects/a/research-plan|A research plan]]\n"
            "- [[Spaces/projects/b/research-plan|B research plan]]\n"
            "- [[Cards/planning-card]]\n",
        )
        for project in ("a", "b"):
            write(
                wiki / "Domains" / "ai-research" / "Spaces" / "projects" / project / "research-plan.md",
                f"""---
title: Project {project.upper()} Research Plan
created: 2026-01-01
updated: 2026-01-01
type: space
tags: [project]
status: active
---

# Project {project.upper()} Research Plan
""",
            )
        write(
            wiki / "Domains" / "ai-research" / "Cards" / "planning-card.md",
            """---
title: Planning Card
created: 2026-01-01
updated: 2026-01-01
type: concept
aliases:
  - Research planning
tags: [agent]
status: active
---

# Planning Card

The bare link [[research-plan]] is ambiguous after domains are merged.
""",
        )

        result = run("validate", "--wiki", wiki.as_posix(), "--domain", "ai-research", "--json", check=False)
        assert result.returncode == 1
        payload = json.loads(result.stdout)
        codes = {item["code"] for item in payload["domains"][0]["issues"]}
        assert "ambiguous-wikilink" in codes


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
        action_paths = {item["path"] for item in payload["actions"]}
        for path in [
            wiki / "00_System" / "card-policy.md",
            wiki / "00_System" / "card-domains.md",
            wiki / "00_System" / "agent-policy.md",
            wiki / "Atlas",
            wiki / "Cards" / "ai-research",
            wiki / "Sources" / "Raw",
            wiki / "Sources" / "Papers",
            wiki / "Sources" / "Clippings",
            wiki / "Spaces",
            wiki / "Extras" / "Templates",
            wiki / "Extras" / "Img",
            wiki / "Extras" / "Excalidraw",
            wiki / "z-Legacy",
        ]:
            assert path.as_posix() in action_paths


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
        assert (wiki / "00_System" / "card-policy.md").exists()
        assert (wiki / "00_System" / "card-domains.md").exists()
        assert (wiki / "00_System" / "agent-policy.md").exists()
        assert (wiki / "Extras" / "Templates" / "weekly.md").exists()
        assert not (wiki / "Extras" / "Templates" / "card.md").exists()
        assert not (wiki / "Extras" / "Templates" / "moc.md").exists()
        assert not (wiki / "Extras" / "Templates" / "relationship.md").exists()
        assert (wiki / "Cards" / "ai-research").is_dir()
        assert not (wiki / "Cards" / "ai-research" / "SCHEMA.md").exists()
        assert not (wiki / "Domains" / "ai-research" / "SCHEMA.md").exists()
        assert (wiki / "Sources" / "Raw").is_dir()
        assert (wiki / "Sources" / "Papers").is_dir()
        assert "default_domain = \"ai-research\"" in registry.read_text(encoding="utf-8")


if __name__ == "__main__":
    test_status_contract()
    test_validate_contract()
    test_validate_root_cards_layout_contract()
    test_validate_all_domains_includes_mixed_root_and_legacy_layouts()
    test_validate_rejects_unsafe_domain_name()
    test_init_rejects_unsafe_domain_name()
    test_validate_rejects_wikilink_parent_path_components()
    test_validate_root_atlas_and_spaces_pages()
    test_fix_orphan_footnotes_reports_root_layout_paths()
    test_validate_root_cards_rejects_nested_markdown()
    test_validate_root_cards_requires_card_domain_policy()
    test_shared_validator_module_importable()
    test_validate_reports_paper_note_format_errors()
    test_validate_reports_root_paper_errors_from_any_card_domain()
    test_validate_checks_root_and_legacy_paper_notes_when_both_exist()
    test_validate_checks_root_and_legacy_raw_roots_when_both_exist()
    test_validate_rejects_malformed_zotero_pdf_links()
    test_validate_rejects_bare_zotero_pdf_uri_without_markdown_pdf_link()
    test_validate_rejects_mismatched_zotero_pdf_link_target()
    test_validate_rejects_nested_paper_notes()
    test_validate_ignores_legacy_directory()
    test_validate_rejects_title_only_card_aliases()
    test_validate_rejects_redundant_card_aliases()
    test_validate_accepts_path_qualified_index_links()
    test_validate_rejects_ambiguous_bare_wikilinks_for_duplicate_stems()
    test_init_is_read_only_plan()
    test_cli_setup_writes_bootstrap_files()
    print("LoreForge component contract tests passed.")

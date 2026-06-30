"""Validation strategy for Zotero-managed paper notes."""

from __future__ import annotations

import re
from pathlib import Path

from .markdown import clean_scalar, frontmatter, heading_exists, split_frontmatter
from .model import Issue
from .paths import rel


PAPER_NOTES_RELATIVE_DIR = Path("Sources") / "Papers"
LEGACY_PAPER_NOTES_RELATIVE_DIR = Path("Domains") / "research" / "Spaces" / "papers"
PAPER_NOTE_REQUIRED_FRONTMATTER = [
    "citekey",
    "title",
    "aliases",
    "authors",
    "date",
    "category",
    "keywords",
    "conference",
    "link",
    "create_date",
    "zotero_link",
    "zotero_folder",
    "abstract",
    "tags",
    "$version",
    "$libraryID",
    "$itemKey",
]
PAPER_NOTE_REQUIRED_SECTION_GROUPS = [
    ("Summary", ("## Summary",)),
    ("What's the problem?", ("### What's the problem?",)),
    (
        "How does this paper solved it?",
        ("### How does this paper solved it?", "### How does this paper sovled it?"),
    ),
    ("What's the improvements?", ("### What's the improvements?",)),
    ("Strengths", ("## Strengths",)),
    ("Weakness", ("## Weakness", "## Weaknesses")),
    ("Detailed Comments", ("## Detailed Comments",)),
    (
        "Ideas for improvement",
        (
            "## Ideas for improvement(How Can I do better)",
            "## Ideas for improvement (How Can I do better)",
            "## Ideas for improvement",
        ),
    ),
    ("Lessons learned", ("## Lessons learned",)),
]


def paper_note_roots_for_wiki(wiki: Path) -> list[Path]:
    return [
        candidate
        for candidate in (wiki / PAPER_NOTES_RELATIVE_DIR, wiki / LEGACY_PAPER_NOTES_RELATIVE_DIR)
        if candidate.exists()
    ]


def has_zotero_pdf_link(body: str, zotero_link: str) -> bool:
    if not zotero_link.startswith("zotero://open-pdf/"):
        return False
    for match in re.finditer(r"^\s*\[PDF\]\(\s*(zotero://open-pdf/[^)\s]+)\s*\)\s*$", body, flags=re.IGNORECASE | re.MULTILINE):
        if match.group(1) == zotero_link:
            return True
    return False


def validate_zotero_paper_notes(wiki: Path) -> list[Issue]:
    wiki = wiki.resolve()
    issues: list[Issue] = []
    paper_note_roots = paper_note_roots_for_wiki(wiki)
    if not paper_note_roots:
        return issues

    for paper_notes_root in paper_note_roots:
        for note in sorted(paper_notes_root.rglob("*.md")):
            note_rel = rel(note, wiki)

            parts = note.relative_to(paper_notes_root).parts
            if len(parts) != 1:
                issues.append(
                    Issue(
                        "paper-note-location",
                        note_rel,
                        f"paper notes should be flat files directly under {rel(paper_notes_root, wiki)}/",
                    )
                )
                continue

            citekey = note.stem
            text = note.read_text()
            fields = frontmatter(text)
            if fields is None:
                issues.append(Issue("missing-paper-frontmatter", note_rel, "paper note lacks YAML frontmatter"))
                continue

            for field in PAPER_NOTE_REQUIRED_FRONTMATTER:
                if field not in fields:
                    issues.append(Issue("missing-paper-field", note_rel, f"missing `{field}`"))

            frontmatter_citekey = fields.get("citekey")
            if frontmatter_citekey and clean_scalar(frontmatter_citekey) != citekey:
                expected_name = f"{clean_scalar(frontmatter_citekey)}.md"
                issues.append(
                    Issue(
                        "paper-note-name-mismatch",
                        note_rel,
                        f"paper note filename should be `{expected_name}` to match frontmatter `citekey`",
                    )
                )
                issues.append(
                    Issue(
                        "paper-note-citekey-mismatch",
                        note_rel,
                        f"`citekey` should match paper note filename `{citekey}.md`",
                    )
                )

            zotero_link = clean_scalar(fields.get("zotero_link", ""))
            if not zotero_link.startswith("zotero://open-pdf/"):
                issues.append(
                    Issue(
                        "missing-zotero-link",
                        note_rel,
                        "`zotero_link` should contain a Zotero PDF URI such as `zotero://open-pdf/...`",
                    )
                )

            _, body = split_frontmatter(text)
            if not has_zotero_pdf_link(body, zotero_link):
                issues.append(
                    Issue(
                        "missing-paper-pdf-link",
                        note_rel,
                        "paper note should use a Zotero URI for the PDF jump link, for example `[PDF](zotero://open-pdf/...)`",
                    )
                )

            if not re.search(r"^# .+", text, flags=re.MULTILINE):
                issues.append(Issue("missing-paper-heading", note_rel, "paper note should have a top-level `#` title"))

            for label, headings in PAPER_NOTE_REQUIRED_SECTION_GROUPS:
                if not any(heading_exists(text, heading) for heading in headings):
                    accepted = "`, `".join(headings)
                    issues.append(
                        Issue(
                            "missing-paper-section",
                            note_rel,
                            f"missing `{label}` section; accepted headings: `{accepted}`",
                        )
                    )

    return sorted(issues, key=lambda issue: (issue.code, issue.path, issue.message))

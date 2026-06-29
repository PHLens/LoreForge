"""Validation strategy for Zotero-managed paper notes."""

from __future__ import annotations

import re
from pathlib import Path

from .markdown import clean_scalar, frontmatter, heading_exists, wikilinks
from .model import Issue
from .paths import LEGACY_TOP_LEVEL_DIRS, rel


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


def paper_pdf_link_exists(note: Path, wiki: Path, links: list[str]) -> bool:
    for target in links:
        if not target.lower().endswith(".pdf"):
            continue
        candidate = wiki / target if "/" in target else note.parent / target
        if candidate.exists():
            return True
    return False


def validate_zotero_paper_notes(wiki: Path) -> list[Issue]:
    wiki = wiki.resolve()
    issues: list[Issue] = []
    zotero_root = wiki / "Shared" / "Zotero"
    if not zotero_root.exists():
        return issues

    for note in sorted(zotero_root.rglob("*.md")):
        note_rel = rel(note, wiki)
        parts = note.relative_to(zotero_root).parts
        if not parts or parts[0] in LEGACY_TOP_LEVEL_DIRS:
            continue
        if len(parts) != 2:
            continue

        citekey = parts[0]
        if note.name != f"{citekey}.md":
            issues.append(
                Issue(
                    "paper-note-name-mismatch",
                    note_rel,
                    f"paper note filename should be `{citekey}.md` inside Shared/Zotero/{citekey}/",
                )
            )

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
            issues.append(
                Issue(
                    "paper-note-citekey-mismatch",
                    note_rel,
                    f"`citekey` should match bundle folder `{citekey}`",
                )
            )

        pdfs = sorted(path for path in note.parent.iterdir() if path.is_file() and path.suffix.lower() == ".pdf")
        if not pdfs:
            issues.append(Issue("missing-paper-pdf", rel(note.parent, wiki), "paper bundle has a note but no PDF"))

        if not paper_pdf_link_exists(note, wiki, wikilinks(text)):
            issues.append(
                Issue(
                    "missing-paper-pdf-link",
                    note_rel,
                    "paper note should link to an existing PDF in its bundle",
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

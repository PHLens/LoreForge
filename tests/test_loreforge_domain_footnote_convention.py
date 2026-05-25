"""Lint tests for LoreForge wiki source-link conventions."""
import pathlib
import re

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL_PATHS = [
    REPO_ROOT / "skills" / "loreforge-card" / "SKILL.md",
    REPO_ROOT / "skills" / "loreforge-moc" / "SKILL.md",
    REPO_ROOT / "skills" / "loreforge-domain" / "SKILL.md",
]
CARD_SKILL_PATH = REPO_ROOT / "skills" / "loreforge-card" / "SKILL.md"

CARET_FOOTNOTE_RE = re.compile(r"\^\[.*?\]")


def test_no_inline_caret_footnotes():
    """SKILL.md files must not use ^[...] inline footnote syntax."""
    found = []
    for path in SKILL_PATHS:
        matches = CARET_FOOTNOTE_RE.findall(path.read_text())
        found.extend(f"{path.name}:{match}" for match in matches)
    assert found == [], (
        "Found deprecated ^[...] inline footnote syntax: "
        + str(found)
        + ". Use inline wikilinks for wiki-local sources; use [^N] only when provenance is ambiguous."
    )


def test_source_links_prefer_internal_wikilinks():
    """Card source-link guidance should prefer filename/stem wikilinks for wiki-local sources."""
    content = CARD_SKILL_PATH.read_text()
    lower_content = content.lower()
    assert "Provenance" in content
    assert "prefer inline wikilinks" in lower_content
    assert "[[source-artifact-or-manifest|readable source alias]]" in content


def test_footnotes_are_exception_not_default():
    """Footnotes should be limited to ambiguous paragraph-level provenance."""
    content = CARD_SKILL_PATH.read_text()
    assert "Use source footnotes only" in content
    assert "Single-source pages should still use a footnote" not in content


def test_single_source_cards_do_not_repeat_same_source_marker():
    """Single-source Card guidance should forbid mechanical repeated source markers."""
    content = CARD_SKILL_PATH.read_text()
    collapsed = " ".join(content.split())
    assert "instead of repeating the same marker in every paragraph" in collapsed
    assert "link the dominant source once or in a small" in collapsed
    assert "boundary-setting locations" in collapsed
    assert "multi-source synthesis" in content


if __name__ == "__main__":
    test_no_inline_caret_footnotes()
    test_source_links_prefer_internal_wikilinks()
    test_footnotes_are_exception_not_default()
    test_single_source_cards_do_not_repeat_same_source_marker()
    print("All source-link convention tests passed.")

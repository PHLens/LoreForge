"""Lint tests for LoreForge wiki source-link conventions."""
import re
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL_PATH = REPO_ROOT / "skills" / "loreforge-domain" / "SKILL.md"

CARET_FOOTNOTE_RE = re.compile(r"\^\[.*?\]")


def test_no_inline_caret_footnotes():
    """SKILL.md must not use ^[...] inline footnote syntax."""
    content = SKILL_PATH.read_text()
    matches = CARET_FOOTNOTE_RE.findall(content)
    assert matches == [], (
        "Found deprecated ^[...] inline footnote syntax: "
        + str(matches)
        + ". Use inline wikilinks for wiki-local sources; use [^N] only when provenance is ambiguous."
    )


def test_source_links_prefer_internal_wikilinks():
    """Source-link guidance should prefer filename/stem wikilinks for wiki-local sources."""
    content = SKILL_PATH.read_text()
    assert "Provenance links" in content
    assert "prefer an inline wikilink" in content
    assert "[[clip-name|readable alias]]" in content


def test_footnotes_are_exception_not_default():
    """Footnotes should be limited to ambiguous paragraph-level provenance."""
    content = SKILL_PATH.read_text()
    assert "Use source footnotes only" in content
    assert "Single-source pages should still use a footnote" not in content


def test_single_source_cards_do_not_repeat_same_source_marker():
    """Single-source Card guidance should forbid mechanical repeated source markers."""
    content = SKILL_PATH.read_text()
    assert "Do not add the same source marker to every paragraph" in content
    assert "link the dominant source once or in a small" in content
    assert "boundary-setting locations" in content
    assert "multi-source synthesis" in content


if __name__ == "__main__":
    test_no_inline_caret_footnotes()
    test_source_links_prefer_internal_wikilinks()
    test_footnotes_are_exception_not_default()
    test_single_source_cards_do_not_repeat_same_source_marker()
    print("All source-link convention tests passed.")

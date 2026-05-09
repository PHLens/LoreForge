"""Lint tests for LoreForge wiki SKILL.md footnote conventions."""
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
        + ". Use [^N] inline + [^N]: [[wikilink]] at page end instead."
    )


def test_provenance_uses_bracket_footnotes():
    """Provenance marker section must use [^N] syntax."""
    content = SKILL_PATH.read_text()
    assert "[^1]" in content, (
        "SKILL.md must reference [^1] footnote syntax for provenance markers."
    )


def test_provenance_shows_footnote_definition_example():
    """Provenance marker section must show wikilink footnote definition example."""
    content = SKILL_PATH.read_text()
    assert "[^1]: [[" in content, (
        "SKILL.md must show [^1]: [[wikilink]] footnote definition example."
    )


if __name__ == "__main__":
    test_no_inline_caret_footnotes()
    test_provenance_uses_bracket_footnotes()
    test_provenance_shows_footnote_definition_example()
    print("All footnote convention tests passed.")

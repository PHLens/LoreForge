"""Lint tests for LoreForge wiki Card / Atlas boundary guidance."""
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL_PATH = REPO_ROOT / "skills" / "loreforge-wiki" / "SKILL.md"


def test_skill_contains_card_template_in_schema():
    """SKILL.md should define the Card template directly in the schema template."""
    content = SKILL_PATH.read_text()
    assert "### Default Card Template" in content
    assert "Cards are shared knowledge objects" in content
    assert "The default Card shape is shown in the SCHEMA template below." in content
    assert "One-sentence lead." in content
    assert "[^1]: [[Shared/Raw/source-id/manifest.md]]" in content


def test_skill_preserves_card_vs_atlas_split():
    """SKILL.md should keep Cards reusable and Atlas for problem-specific views."""
    content = SKILL_PATH.read_text()
    assert "Use `Cards/` for shared, reusable knowledge objects" in content
    assert "Use `Atlas/` for question-driven views" in content
    assert "Overview: what problem or claim the view is trying to discuss" in content
    assert "Key ideas or comments about those concepts" in content
    assert "Cards should answer the stable \"what is it\" and" in content
    assert "specific problem, project, proposal, or point of view" in content
    assert "Common Card shapes:" in content
    assert "Concept pages: definition or explanation" in content
    assert "Comparison pages: what is being compared and why" in content
    assert "project-specific commentary, proposal framing" in content


if __name__ == "__main__":
    test_skill_contains_card_template_in_schema()
    test_skill_preserves_card_vs_atlas_split()
    print("All Card / Atlas boundary tests passed.")

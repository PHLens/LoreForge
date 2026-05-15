"""Lint tests for LoreForge wiki Card / Atlas boundary guidance."""
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL_PATH = REPO_ROOT / "skills" / "loreforge-domain" / "SKILL.md"


def test_skill_contains_card_template_in_schema():
    """SKILL.md should define the Card template directly in the schema template."""
    content = SKILL_PATH.read_text()
    assert "### Default Card Template" in content
    assert "Cards are shared knowledge objects" in content
    assert "The default Card shape is" in content
    assert "shown in the SCHEMA template below." in content
    assert "One-sentence direct definition or problem statement." in content
    assert "[^1]: [[Shared/Raw/source-id/manifest.md]]" in content
    assert "## Writing Style" in content
    assert "Write Cards like concise wiki/reference entries" in content
    assert "## Knowledge links" not in content
    assert "**Knowledge links:**" in content
    assert "semantic wiki" in content
    assert "[[kv-cache-memory-hierarchy|KV cache hierarchy]]" in content
    assert "Do not cite Cards with" in content
    assert "source-style footnote markers" in content
    assert "related:: [[concept-a]], [[concept-b|Readable label]]" in content
    assert "not naturally mentioned in the body" in content
    assert "Use aliases when" in content
    assert "do not repeat links already expressed naturally in the body" in content
    assert "Do not add `related::` by default" in content
    assert "do not use it" in content
    assert "Body wikilinks are preferred" in content
    assert "related:: [[related-page]]" not in content


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
    assert "project-specific" in content
    assert "commentary, proposal framing" in content
    assert "Avoid repeated page" in content
    assert "self-description" in content
    assert "proposal evidence" in content
    assert "project support" in content
    assert "Prefer direct" in content
    assert '"not X but Y" phrasing' in content
    assert "weave `[[wikilinks]]` into the relevant sentence" in content
    assert "reference-list style citation" in content


if __name__ == "__main__":
    test_skill_contains_card_template_in_schema()
    test_skill_preserves_card_vs_atlas_split()
    print("All Card / Atlas boundary tests passed.")

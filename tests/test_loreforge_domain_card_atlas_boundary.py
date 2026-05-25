"""Lint tests for LoreForge Card / MOC authoring contracts."""
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
CARD_SKILL_PATH = REPO_ROOT / "skills" / "loreforge-card" / "SKILL.md"
MOC_SKILL_PATH = REPO_ROOT / "skills" / "loreforge-moc" / "SKILL.md"
DOMAIN_SKILL_PATH = REPO_ROOT / "skills" / "loreforge-domain" / "SKILL.md"
ENTRY_SKILL_PATH = REPO_ROOT / "skills" / "loreforge" / "SKILL.md"


def test_card_skill_has_hard_authoring_contract():
    """Card authoring should be a narrow leaf workflow with an acceptance gate."""
    content = CARD_SKILL_PATH.read_text()
    assert "page_type_decision" in content
    assert "selected: card" in content
    assert "Hard Gate" in content
    assert "Card Contract" in content
    assert "Acceptance Gate" in content
    assert "strict page-type decision" in content
    assert "reusable concept/method/mechanism/pattern/tradeoff/comparison" in content
    assert "Do not write a Card when the decision is weak" in content
    assert "aliases" in content
    assert "First body paragraph is a direct definition" in content
    assert "source summary" in content
    assert "project record" in content
    assert "proposal argument" in content
    assert "One-sentence direct definition or problem statement." in content
    assert "## Why" in content
    assert "## What Is Page Title" in content
    assert "## Constraints" in content
    assert "## Open Questions" in content
    assert "## Mechanism" not in content
    assert "## Example" not in content
    assert "[[source-artifact-or-manifest|readable source alias]]" in content
    assert "Do not cite Cards with source-style footnote markers" in content
    assert "related:: [[concept-a]], [[concept-b|Readable label]]" in content


def test_card_skill_defines_split_gate():
    """Growing Cards should be split by reusable concept boundaries, not arbitrary length."""
    content = CARD_SKILL_PATH.read_text()
    collapsed = " ".join(content.split())
    assert "## Split Gate" in content
    assert "Before expanding an existing Card" in content
    assert "multiple `What Is ...` explanations" in content
    assert "independently searched, linked, or reused" in content
    assert "Constraints, variants, or comparisons dominate the parent concept" in content
    assert "Use a MOC for the relationship view" in collapsed
    assert "Do not split when the added material is just an example" in content
    assert "## Split Procedure" in content
    assert "Keep the original Card as the canonical page" in content
    assert "Replace extracted detail in the original Card with a concise summary" in collapsed
    assert "The Split Gate was checked" in content


def test_moc_skill_has_hard_view_contract():
    """MOC authoring should require a view question and relationship structure."""
    content = MOC_SKILL_PATH.read_text()
    assert "page_type_decision" in content
    assert "selected: moc" in content
    assert "view_question" in content
    assert "Hard Gate" in content
    assert "MOC Contract" in content
    assert "Acceptance Gate" in content
    assert "Do not write a MOC without a clear view question" in content
    assert "A MOC is a human-readable view over relationships" in content
    assert "not an index mirror" in content
    assert "not a Card list" in content
    assert "question-driven or problem-driven view" in content
    assert "relationship map across multiple Cards" in content
    assert "Links are woven naturally into the body" in content


def test_entrypoint_routes_directly_to_leaf_workflows():
    """The main entrypoint should choose Card/MOC leaves without a domain router hop."""
    content = ENTRY_SKILL_PATH.read_text()
    assert "`loreforge-card` | strict reusable Card authoring" in content
    assert "`loreforge-moc` | strict Atlas/MOC view authoring" in content
    assert "Delegate directly to `loreforge-card`" in content
    assert "Delegate directly to `loreforge-moc`" in content
    assert "Page-Type Decision" in content
    assert "Do not force uncertain material into Cards or MOCs" in content


def test_domain_skill_delegates_card_and_moc_authoring():
    """The generic domain workflow should no longer own Card/MOC prose."""
    content = DOMAIN_SKILL_PATH.read_text()
    assert "Card and MOC authoring belong to loreforge-card and loreforge-moc" in content
    assert "delegate Card authoring to `loreforge-card`" in content
    assert "delegate Atlas/MOC authoring to `loreforge-moc`" in content
    assert "Do not author Card pages in this workflow" in content
    assert "Do not author Atlas/MOC pages in this workflow" in content
    assert "### Default Card Template" not in content
    assert "Common Card shapes:" not in content


if __name__ == "__main__":
    test_card_skill_has_hard_authoring_contract()
    test_card_skill_defines_split_gate()
    test_moc_skill_has_hard_view_contract()
    test_entrypoint_routes_directly_to_leaf_workflows()
    test_domain_skill_delegates_card_and_moc_authoring()
    print("All Card / MOC authoring contract tests passed.")

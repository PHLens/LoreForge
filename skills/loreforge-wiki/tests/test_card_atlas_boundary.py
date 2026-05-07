"""Lint tests for LoreForge wiki Card / Atlas boundary guidance."""
import pathlib

SKILL_DIR = pathlib.Path(__file__).resolve().parent.parent
SKILL_PATH = SKILL_DIR / "SKILL.md"
BOUNDARY_PATH = SKILL_DIR / "references" / "card-atlas-boundary.md"


def test_skill_links_card_atlas_boundary_reference():
    """SKILL.md should point agents to the Card / Atlas boundary reference."""
    content = SKILL_PATH.read_text()
    assert "references/card-atlas-boundary.md" in content


def test_boundary_reference_defines_reusable_cards_and_view_atlas():
    """Boundary reference should preserve the reusable Card vs view Atlas split."""
    content = BOUNDARY_PATH.read_text()
    assert "Cards are shared knowledge objects" in content
    assert "Atlas/MOC pages are project or view objects" in content
    assert "Do not reserve a mandatory proposal section" in content


if __name__ == "__main__":
    test_skill_links_card_atlas_boundary_reference()
    test_boundary_reference_defines_reusable_cards_and_view_atlas()
    print("All Card / Atlas boundary tests passed.")

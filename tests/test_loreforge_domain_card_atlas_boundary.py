"""Lint tests for LoreForge Card / MOC authoring contracts."""
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
CARD_SKILL_PATH = REPO_ROOT / "skills" / "loreforge-card" / "SKILL.md"
MOC_SKILL_PATH = REPO_ROOT / "skills" / "loreforge-moc" / "SKILL.md"
DOMAIN_SKILL_PATH = REPO_ROOT / "skills" / "loreforge-domain" / "SKILL.md"
ENTRY_SKILL_PATH = REPO_ROOT / "skills" / "loreforge" / "SKILL.md"
PAPER_SKILL_PATH = REPO_ROOT / "skills" / "loreforge-paper" / "SKILL.md"
PAPER_BUNDLE_DOC_PATHS = [
    REPO_ROOT / "README.md",
    REPO_ROOT / "docs" / "philosophy.md",
    REPO_ROOT / "docs" / "schema.md",
    REPO_ROOT / "skills" / "README.md",
    REPO_ROOT / "skills" / "loreforge-capture" / "SKILL.md",
    REPO_ROOT / "skills" / "loreforge-paper" / "SKILL.md",
    REPO_ROOT / "skills" / "loreforge" / "SKILL.md",
    REPO_ROOT / "tests" / "README.md",
    REPO_ROOT / "tests" / "simulate_loreforge_entrypoint_flow.py",
]


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


def test_card_skill_adapts_zettelkasten_permanent_notes():
    """Cards should adapt permanent-note discipline without importing the numbering system."""
    content = CARD_SKILL_PATH.read_text()
    collapsed = " ".join(content.split())
    assert "## Zettelkasten Adaptation" in content
    assert "permanent notes" in content
    assert "one focus object" in content
    assert "self-contained enough to make sense later" in content
    assert "Write in the domain's own words" in content
    assert "semantic links whose nearby prose explains why the linked page matters" in collapsed
    assert "Do not copy the physical Zettelkasten numbering/sequence system" in content
    assert "The Card is self-contained, written in domain words, and has one focus object" in content


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


def test_moc_skill_adapts_zettelkasten_structure_notes():
    """MOCs should act as structure notes instead of broad related-link dumps."""
    content = MOC_SKILL_PATH.read_text()
    collapsed = " ".join(content.split())
    assert "## Zettelkasten Adaptation" in content
    assert "structure notes" in content
    assert "entry point into a cluster" in content
    assert "why the linked notes belong together" in content
    assert "relationship, contrast, dependency, sequence, or tension" in content
    assert "extract those definitions into Cards" in collapsed
    assert "Do not copy the physical Zettelkasten numbering/sequence system" in content
    assert "The page acts as a structure note: an entry point with relationship context" in collapsed


def test_inline_examples_cover_card_moc_and_relationship_shapes():
    """Card/MOC shapes should live in skills/schema instead of seeded wiki template files."""
    card_skill = CARD_SKILL_PATH.read_text()
    moc_skill = MOC_SKILL_PATH.read_text()

    assert "type: concept" in card_skill
    assert "aliases:" in card_skill
    assert "One-sentence direct definition or problem statement." in card_skill
    assert "## What Is Page Title" in card_skill

    assert "type: map" in moc_skill
    assert "This view asks: ..." in moc_skill
    assert "## Key Relationships" in moc_skill
    assert "## Tradeoffs" in moc_skill
    assert "This relationship view asks how [[page-a]] and [[page-b]] connect." in moc_skill
    assert "## Direction" in moc_skill
    assert "## Tension" in moc_skill
    assert "not a separate page type" in moc_skill


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


def test_compiled_page_language_gate_applies_to_all_wiki_pages():
    """All compiled wiki page workflows should share the language gate."""
    entry = ENTRY_SKILL_PATH.read_text()
    card = CARD_SKILL_PATH.read_text()
    moc = MOC_SKILL_PATH.read_text()
    domain = DOMAIN_SKILL_PATH.read_text()
    paper = (REPO_ROOT / "skills" / "loreforge-paper" / "SKILL.md").read_text()
    work_item = (REPO_ROOT / "skills" / "loreforge-work-item" / "SKILL.md").read_text()
    collapsed_entry = " ".join(entry.split())
    collapsed_domain = " ".join(domain.split())
    collapsed_work_item = " ".join(work_item.split())

    assert "## Compiled Page Language Gate" in entry
    assert "Apply this gate to every synthesized LoreForge wiki page" in entry
    assert "Cards, Atlas/MOCs, Sources, Spaces, paper notes, work items" in collapsed_entry
    assert "Raw captures and `log.md` entries are exempt" in entry
    assert "Keep process, placement, routing, and edit-history commentary out of page bodies" in collapsed_entry
    assert "this page records" in entry
    assert "not X but Y" in entry

    assert "Apply the `loreforge` Compiled Page Language Gate before handoff." in card
    assert "Apply the `loreforge` Compiled Page Language Gate before handoff." in moc
    assert "Compiled Page Language Gate" in domain
    assert "Apply the `loreforge` Compiled Page Language Gate before handoff." in paper
    assert "Compiled Page Language Gate" in work_item

    assert "Formal project artifacts under `Spaces/projects/`" in entry
    assert "proposal*.md" in entry
    assert "research-plan*.md" in entry
    assert "literature-survey*.md" in entry
    assert "must not be routed to Cards as related-work notes" in collapsed_entry

    assert "## Formal Project Artifacts" in work_item
    assert "Apply the `loreforge` Compiled Page Language Gate to every work-item or project" in collapsed_work_item
    assert "Literature surveys should compare mechanisms, assumptions, scope, IR level" in collapsed_work_item
    assert "Research plans should use milestone, artifact, experiment, and validation language" in collapsed_work_item

    assert "Formal Project Artifacts" in domain
    assert "### Default Card Template" not in domain
    assert "Common Card shapes:" not in domain


def test_paper_skill_uses_read_only_paper_bundles():
    """Paper workflow should stay inside existing citekey bundles."""
    content = PAPER_SKILL_PATH.read_text()
    collapsed = " ".join(content.split())

    assert "Shared/Zotero/<citekey>/" in content
    assert "Shared/Papers" not in content
    assert "AlphaCuTransformationDrivenSynthesis2017" in content
    assert "If no matching paper bundle exists, stop" in content
    assert "Do not create paper directories" in content
    assert "Treat all PDF files in the selected paper directory as raw artifacts" in collapsed
    assert "read-only" in content
    assert "write only paper notes under `Shared/Zotero/<citekey>/`" in content
    assert "Creating `<citekey>.md` is allowed" in content
    assert "Do not use `Shared/Raw/` for paper PDFs or paper notes" in content
    assert "Writable paths: Markdown note files under Shared/Zotero/<citekey>/ only" in content
    assert "Paper raw package: Shared/Raw/<source-id>/" not in content
    assert "Save `original/<paper>.pdf` only when" not in content


def test_paper_bundle_docs_use_zotero_path_consistently():
    """Published paper-bundle docs should not drift back to the old path."""
    for path in PAPER_BUNDLE_DOC_PATHS:
        content = path.read_text()
        assert "Shared/Zotero" in content, f"{path} should mention Shared/Zotero"
        assert "Shared/Papers" not in content, f"{path} still mentions Shared/Papers"


def test_entrypoint_preserves_paper_bundle_boundary():
    """The user-facing entrypoint should not route paper capture/ingest through raw packages."""
    content = ENTRY_SKILL_PATH.read_text()
    collapsed = " ".join(content.split())

    assert "For paper capture requests, delegate to `loreforge-paper`" in content
    assert "Shared/Papers" not in content
    assert "Do not delegate paper capture to" in content
    assert "`loreforge-capture`" in content
    assert "For ordinary paper ingest, stop after the paper-note update" in content
    assert "Only continue to Cards, Atlas, Sources, Spaces, or cross-domain synthesis" in collapsed
    assert "do not create `Shared/Raw/` paper packages" in content


if __name__ == "__main__":
    test_card_skill_has_hard_authoring_contract()
    test_card_skill_defines_split_gate()
    test_card_skill_adapts_zettelkasten_permanent_notes()
    test_moc_skill_has_hard_view_contract()
    test_moc_skill_adapts_zettelkasten_structure_notes()
    test_inline_examples_cover_card_moc_and_relationship_shapes()
    test_entrypoint_routes_directly_to_leaf_workflows()
    test_domain_skill_delegates_card_and_moc_authoring()
    test_compiled_page_language_gate_applies_to_all_wiki_pages()
    test_paper_skill_uses_read_only_paper_bundles()
    test_paper_bundle_docs_use_zotero_path_consistently()
    test_entrypoint_preserves_paper_bundle_boundary()
    print("All Card / MOC authoring contract tests passed.")

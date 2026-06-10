#!/usr/bin/env python3
"""Check the LoreForge capture workflow contract.

The capture flow is implemented mostly as skill instructions. This test keeps
the expected web-capture behavior explicit so raw packages preserve more than a
directory shape.
"""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def assert_contains(path: str, required: list[str]) -> None:
    text = read(path)
    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError(f"{path} is missing capture contract text: {missing}")


def test_capture_skill_web_clipper_contract() -> None:
    assert_contains(
        "skills/loreforge-capture/SKILL.md",
        [
            "capture plan",
            "Web Capture Flow",
            "clipper-style pipeline",
            "Snapshot first.",
            "Extract deterministic variables.",
            "Use selectors for site-specific structure.",
            "Apply a capture template.",
            "Localize important assets.",
            "Record extraction lineage.",
            "obsidian-clipper",
            "retrieved_at",
            "source_url",
            "source_description",
            "extraction:",
            "selectors:",
            "schema_triggers:",
            "prompt_assisted:",
        ],
    )


def test_domain_and_docs_reference_capture_plan() -> None:
    assert_contains(
        "skills/loreforge-domain/SKILL.md",
        [
            "clipper-style capture plan",
            "deterministic page variables",
            "extractor/template/selector decisions",
            "obsidian-clipper",
        ],
    )
    assert_contains(
        "docs/schema.md",
        [
            "Web capture should be planned before extraction.",
            "deterministic page variables",
            "prompt-assistance choices",
        ],
    )
    assert_contains(
        "README.md",
        [
            "clipper-style plan",
            "Obsidian Web Clipper",
        ],
    )


if __name__ == "__main__":
    test_capture_skill_web_clipper_contract()
    test_domain_and_docs_reference_capture_plan()
    print("LoreForge capture skill contract tests passed.")

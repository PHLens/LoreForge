#!/usr/bin/env python3
"""Check the LoreForge capture workflow contract.

The capture flow is implemented mostly as skill instructions. This test keeps
the expected web-capture behavior explicit so raw packages preserve more than a
directory shape.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def assert_contains(path: str, required: list[str]) -> None:
    text = read(path)
    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError(f"{path} is missing capture contract text: {missing}")


def markdown_body(text: str) -> str:
    return text.split("---", 2)[2]


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
            "Render a fixed capture card.",
            "Localize important assets.",
            "Record extraction lineage.",
            "Capture Card Format",
            "title: \"<title>\"",
            "author: \"<author>\"",
            "published: \"<published date or empty>\"",
            "created: \"YYYY-MM-DD\"",
            "created",
            "description",
            "tags:",
            "capture_card:",
            "format: web-clipper-like",
            "dedupe fixed-field metadata",
            "primary_method:",
            "methods:",
            "metadata-supplement",
            "fallback:",
            "obsidian-clipper",
            "retrieved_at",
            "source_url",
            "source_description",
            "extraction:",
            "variables:",
            "selectors:",
            "schema_triggers:",
            "filters:",
            "prompt_assisted:",
        ],
    )


def test_domain_and_docs_reference_capture_plan() -> None:
    assert_contains(
        "skills/loreforge-domain/SKILL.md",
        [
            "clipper-style capture plan",
            "deterministic page variables",
            "extractor/source-mode/selector decisions",
            "obsidian-clipper",
        ],
    )
    assert_contains(
        "docs/schema.md",
        [
            "Web capture should be planned before extraction.",
            "deterministic page variables",
            "fixed Web Clipper-like capture card shape",
            "Markdown body",
            "is not duplicated",
            "manifest extraction lineage",
            "prompt-assistance choices",
        ],
    )
    assert_contains(
        "README.md",
        [
            "clipper-style plan",
            "Web Clipper-like capture card",
            "fixed Web Clipper-like capture card",
        ],
    )


def test_golden_capture_fixture_shape() -> None:
    raw = REPO_ROOT / "tests" / "fixtures" / "capture" / "web-clipper-like" / "Shared" / "Raw" / "moe-web-capture"
    origin = raw / "origin.md"
    manifest = raw / "manifest.md"
    defuddle = raw / "extracted" / "defuddle.md"
    origin_text = origin.read_text(encoding="utf-8")
    manifest_text = manifest.read_text(encoding="utf-8")
    defuddle_text = defuddle.read_text(encoding="utf-8")

    expected_hash = hashlib.sha256(origin.read_bytes()).hexdigest()
    if f'content_hash: "{expected_hash}"' not in manifest_text:
        raise AssertionError("golden manifest content_hash does not match origin.md")

    required_origin = [
        "retrieved_at: \"2026-06-10\"",
        "created: \"2026-06-10\"",
        "capture_card:",
        "format: web-clipper-like",
    ]
    missing_origin = [item for item in required_origin if item not in origin_text]
    if missing_origin:
        raise AssertionError(f"golden origin is missing fixed capture-card fields: {missing_origin}")

    body = markdown_body(origin_text)
    forbidden_content = [
        "## Title:",
        "Authors:",
        "Cite as:",
        "## Description",
        "## Content",
        "## Structured Metadata",
        "## Capture Limits",
        "MCP wiki search was unavailable",
    ]
    found_forbidden = [item for item in forbidden_content if item in body]
    if found_forbidden:
        raise AssertionError(f"golden origin keeps duplicated extractor metadata: {found_forbidden}")

    if "Abstract:" not in body or "Mixture of Experts (MoE)" not in body:
        raise AssertionError("golden origin content does not preserve filtered source substance")

    if "## Title:" not in defuddle_text or "Cite as:" not in defuddle_text:
        raise AssertionError("golden defuddle artifact does not preserve unfiltered extractor output")

    required_manifest = [
        "primary_method:",
        "methods:",
        "Shared/Raw/moe-web-capture/extracted/defuddle.md",
        "role: \"metadata-supplement\"",
        "role: \"manual-cleanup\"",
        "content_filters:",
        "fallback:",
        "status: \"unavailable\"",
        "substitute_sources:",
    ]
    missing_manifest = [item for item in required_manifest if item not in manifest_text]
    if missing_manifest:
        raise AssertionError(f"golden manifest is missing lineage fields: {missing_manifest}")


if __name__ == "__main__":
    test_capture_skill_web_clipper_contract()
    test_domain_and_docs_reference_capture_plan()
    test_golden_capture_fixture_shape()
    print("LoreForge capture skill contract tests passed.")

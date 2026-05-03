#!/usr/bin/env python3
"""Smoke-test the LoreForge router contract.

The router is a skill-level workflow, not a runtime library. This test keeps the
expected behavior concrete: discover domains, choose read/write targets, and
preserve the rule that durable domain work is delegated to loreforge-wiki.
"""

from __future__ import annotations

import re
import tempfile
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Route:
    operation: str
    primary: str | None
    selected: tuple[str, ...]
    secondary: tuple[str, ...]
    requires_confirmation: bool


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def read_skill() -> str:
    return (REPO_ROOT / "skills" / "loreforge-router" / "SKILL.md").read_text(encoding="utf-8")


def assert_skill_contract() -> None:
    skill = read_skill()
    required = [
        "loreforge-wiki",
        "one expert-owned domain as the write boundary",
        "write domain pages directly as the router",
        "Multiple write matches",
        "ask before writing multiple domains",
        ".obsidian*",
        "delegate initialization to `loreforge-wiki`",
        "parallel expert review is useful",
        "Otherwise process selected domains sequentially",
        "one subagent per selected domain",
        "Write policy: <read-only|write-confirmed>",
        "Set `Write policy: read-only` for query operations",
        "do not create or update wiki files",
        "Shared/Raw/",
        "footnotes, not YAML",
    ]
    missing = [item for item in required if item not in skill]
    if missing:
        raise AssertionError(f"router skill is missing required routing contract text: {missing}")


def create_domain(wiki: Path, name: str, purpose: str, tags: str, index: str) -> None:
    write(
        wiki / "Domains" / name / "SCHEMA.md",
        f"""# Schema

## Domain
{purpose}

## Tag Taxonomy
- {tags}
""",
    )
    write(wiki / "Domains" / name / "index.md", f"# Domain Index\n\n{index}\n")
    write(wiki / "Domains" / name / "log.md", "# Domain Log\n")


def domain_names(wiki: Path) -> list[str]:
    return sorted(path.name for path in (wiki / "Domains").iterdir() if path.is_dir())


def domain_text(wiki: Path, domain: str) -> str:
    parts = [
        (wiki / "Domains" / domain / "SCHEMA.md").read_text(encoding="utf-8"),
        (wiki / "Domains" / domain / "index.md").read_text(encoding="utf-8"),
    ]
    return "\n".join(parts).lower()


def tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9][a-z0-9-]*", text.lower()) if len(token) > 2}


def operation_for(request: str) -> str:
    lower = request.lower()
    if any(word in lower for word in ["ingest", "import", "source", "paper", "url"]):
        return "ingest"
    if any(word in lower for word in ["health check", "lint", "audit"]):
        return "review"
    return "query"


def route(wiki: Path, request: str) -> Route:
    operation = operation_for(request)
    available = domain_names(wiki)
    request_tokens = tokens(request)

    explicit = [name for name in available if name in request.lower()]
    if explicit:
        selected = tuple(explicit)
        return Route(operation, selected[0], selected, tuple(), False)

    scores: list[tuple[int, str]] = []
    for domain in available:
        score = len(request_tokens & tokens(domain_text(wiki, domain)))
        scores.append((score, domain))
    scores.sort(reverse=True)

    matches = [domain for score, domain in scores if score > 0]
    if not matches:
        return Route(operation, None, tuple(), tuple(), operation != "query")

    if operation == "query":
        selected = tuple(matches[:2])
        return Route(operation, selected[0], selected, tuple(matches[2:]), False)

    primary = matches[0]
    secondary = tuple(matches[1:2])
    return Route(operation, primary, (primary,), secondary, bool(secondary))


def main() -> int:
    assert_skill_contract()
    print("PASS skill contract: router delegates and preserves write boundaries")

    with tempfile.TemporaryDirectory(prefix="loreforge-router-") as tmp_raw:
        wiki = Path(tmp_raw) / "wiki"
        write(
            wiki / "00_System" / "domains.md",
            "# Domains\n\n"
            "| Domain | Purpose | Default Language | Expert | Status |\n"
            "|---|---|---|---|---|\n"
            "| gpu-arch-research | GPU architecture, CUDA, memory hierarchy, roofline, profiling | 中文 | gpu expert | active |\n"
            "| ml-systems | PyTorch, compiler runtime, distributed training, inference systems | 中文 | systems expert | active |\n"
            "| product-strategy | Roadmaps, market positioning, customer research | 中文 | strategy expert | active |\n",
        )
        write(
            wiki / "00_System" / "index.md",
            "# Wiki Index\n\n- Layout: [[wiki-layout]]\n- Domains: [[domains]]\n",
        )
        write(
            wiki / "00_System" / "wiki-layout.md",
            "# Wiki Layout\n\n"
            "Canonical shared layer:\n\n"
            "- `Shared/Raw/<source-id>/manifest.md` for raw source manifests, hashes, and compiled page metadata\n"
            "- `Shared/Raw/<source-id>/` for source artifacts\n"
            "- `Shared/Templates/` for reusable templates\n\n"
        "Domain layer:\n\n"
        "- `Domains/<domain>/Atlas/`, `Cards/`, `Sources/`, and `Spaces/` for compiled durable knowledge\n\n"
        "Compiled pages live in `Domains/<domain>/Atlas/`, `Cards/`, `Sources/`, and `Spaces/`. "
        "Raw source material belongs in `Shared/Raw/<source-id>/`, and `Sources/` is optional for source excerpts.\n\n"
        "Create `Domains/<domain>/Extras/` only when the domain needs its own\n"
        "non-source attachments.\n",
    )
        create_domain(
            wiki,
            "gpu-arch-research",
            "GPU microarchitecture, CUDA kernels, cache hierarchy, memory bandwidth, roofline models, profiling.",
            "gpu, architecture, cuda, memory, cache, roofline, profiling",
            "- [[gpu-memory-hierarchy]] - GPU cache and memory bandwidth concepts.",
        )
        create_domain(
            wiki,
            "ml-systems",
            "ML systems, PyTorch runtime, compilers, distributed training, serving, inference.",
            "pytorch, compiler, runtime, distributed, inference, serving",
            "- [[pytorch-runtime]] - PyTorch execution and compiler runtime notes.",
        )
        create_domain(
            wiki,
            "product-strategy",
            "Product strategy, roadmap tradeoffs, positioning, customer research.",
            "roadmap, positioning, customer, market, strategy",
            "- [[roadmap-tradeoffs]] - Product roadmap decision notes.",
        )

        explicit = route(wiki, "ingest this source into gpu-arch-research")
        assert explicit.operation == "ingest"
        assert explicit.selected == ("gpu-arch-research",)
        assert explicit.requires_confirmation is False
        print("PASS explicit domain: routes directly to named domain")

        single = route(wiki, "query CUDA cache hierarchy and memory bandwidth")
        assert single.operation == "query"
        assert single.primary == "gpu-arch-research"
        assert "gpu-arch-research" in single.selected
        print("PASS single strong match: routes to GPU expert")

        cross_query = route(wiki, "query PyTorch compiler runtime profiling for CUDA kernels")
        assert cross_query.operation == "query"
        assert "gpu-arch-research" in cross_query.selected
        assert "ml-systems" in cross_query.selected
        assert cross_query.requires_confirmation is False
        print("PASS cross-domain query: can consult multiple domains read-only")

        cross_ingest = route(wiki, "ingest paper about PyTorch compiler runtime profiling for CUDA kernels")
        assert cross_ingest.operation == "ingest"
        assert cross_ingest.primary in {"gpu-arch-research", "ml-systems"}
        assert cross_ingest.secondary
        assert cross_ingest.requires_confirmation is True
        print("PASS cross-domain ingest: selects primary domain and requires confirmation for secondary writes")

        no_match = route(wiki, "ingest source about medieval manuscript preservation")
        assert no_match.primary is None
        assert no_match.requires_confirmation is True
        print("PASS no match: asks before creating or forcing a domain")

    print("router flow smoke test ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

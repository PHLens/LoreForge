#!/usr/bin/env python3
"""Smoke-test the LoreForge entrypoint contract.

The entrypoint is a skill-level dispatch workflow, not a runtime library.
This test keeps the expected behavior concrete: discover domains, choose
read/write targets, and preserve the rule that durable domain work is delegated
to focused leaf workflows.
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
    return (REPO_ROOT / "skills" / "loreforge" / "SKILL.md").read_text(encoding="utf-8")


def read_paper_skill() -> str:
    return (REPO_ROOT / "skills" / "loreforge-paper" / "SKILL.md").read_text(encoding="utf-8")


def read_work_item_skill() -> str:
    return (REPO_ROOT / "skills" / "loreforge-work-item" / "SKILL.md").read_text(encoding="utf-8")


def assert_skill_contract() -> None:
    skill = read_skill()
    paper_skill = read_paper_skill()
    work_item_skill = read_work_item_skill()
    collapsed_skill = " ".join(skill.split())
    required = [
        "Default LoreForge entrypoint",
        "loreforge-config",
        "loreforge-capture",
        "loreforge-paper",
        "plan-docomposer",
        "loreforge-work-item",
        "loreforge-card",
        "loreforge-moc",
        "loreforge-check",
        "loreforge-import",
        "loreforge-domain",
        "Do not ask the user which LoreForge skill to invoke.",
        "intent classification",
        "Capture source material only",
        "post-write sync through `loreforge-config`",
        "Use `loreforge` as the default user-facing entry point.",
        "If the operation is unclear and a write would happen, ask one concise question.",
        "capture if needed, update raw package metadata, and compile domain knowledge",
        "delegate the paper-specific workflow to",
        "Calendar daily/weekly planning handoff",
        "Do not turn plan notes into agent memory, source capture, or domain ingest.",
        "Delegate work-item shaping and bounded domain write guidance to",
        "Compiled Page Language Gate",
        "Apply this gate to every synthesized LoreForge wiki page",
        "Raw captures and `log.md` entries are exempt",
        "Formal project artifacts under `Spaces/projects/`",
        "proposals, research plans, literature surveys",
        "Delegate lint, audit, and check work to `loreforge-check`",
        "Delegate source discovery and capture planning to `loreforge-import`",
        "Delegate directly to `loreforge-card`",
        "Delegate directly to `loreforge-moc`",
        "Page-Type Decision",
        "Do not force uncertain material into Cards or MOCs",
        "Use loreforge-domain.",
        ]
    missing = [item for item in required if item not in skill]
    if missing:
        raise AssertionError(f"main entrypoint skill is missing required routing contract text: {missing}")
    if "Cards, Atlas/MOCs, Sources, Spaces, paper notes, work items" not in collapsed_skill:
        raise AssertionError("main entrypoint skill is missing compiled page coverage text")
    paper_required = [
        "Paper ingest is a distinct workflow.",
        "loreforge-capture",
        "loreforge-card",
        "loreforge-moc",
        "loreforge-domain",
        "ordinary articles, blogs, docs, transcripts, reports, local notes, or web",
        "Paper Artifact Policy",
        "metadata-and-text first",
        "Do not save every PDF into the wiki",
        "does not need to store a PDF",
        "binary by default",
        "Save `original/<paper>.pdf` only when",
        "PDF binary not",
        "archived; retrieve from canonical_url/arxiv_id",
        "Paper Page Shape",
        "Domain Handoff Prompt",
    ]
    missing_paper = [item for item in paper_required if item not in paper_skill]
    if missing_paper:
        raise AssertionError(f"paper workflow skill is missing required contract text: {missing_paper}")
    work_item_required = [
        "Work-item notes are durable project records, not activity logs.",
        "project work, feature work, Jira, issue, task, bugfix, CI failure",
        "Spaces/projects",
        "Domains/<domain>/Spaces/projects/<project>/<work-item>.md",
        "Problem Background",
        "Solution",
        "Bug Diagnosis And Fixes",
        "Verification",
        "Do not save chat transcripts",
        "Attach diagrams or artifacts only in the section that explains them",
        "Use Shared/Raw/ only for diagrams, logs, screenshots, or source artifacts",
        "Link And Citation Style",
        "Prefer inline wikilinks to wiki-local Jira/issue/MR/PR/design-doc/CI-log raw",
        "Weave concepts, systems, modules, files, failures, fixes, and related work",
        "Avoid standalone \"related Cards\" or \"related pages\" tables",
        "Formal Project Artifacts",
        "Apply the `loreforge` Compiled Page Language Gate to every work-item or project",
        "proposal*.md",
        "literature-survey*.md",
        "Domain Handoff Prompt",
        "loreforge-card",
        "loreforge-moc",
    ]
    missing_work_item = [item for item in work_item_required if item not in work_item_skill]
    if missing_work_item:
        raise AssertionError(f"work-item workflow skill is missing required contract text: {missing_work_item}")


def create_domain(wiki: Path, name: str, purpose: str, tags: str, index: str) -> None:
    write(
        wiki / "Domains" / name / "SCHEMA.md",
        f"""# Schema

## Domain
{purpose}

## Tag Taxonomy
- {tags}

Rule: tags are coarse domain classification labels; keep them to 1-3 per page instead of keyword stacks.
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
    request_tokens = tokens(request)
    work_item_phrases = ["work item", "project note", "spaces/projects", "ci failure"]
    work_item_tokens = {"jira", "mr", "pr", "bugfix"}
    if any(phrase in lower for phrase in work_item_phrases) or request_tokens & work_item_tokens:
        return "work-item"
    if any(word in lower for word in ["ingest", "import", "source", "paper", "url"]):
        return "ingest"
    if any(word in lower for word in ["check", "lint", "audit"]):
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
    print("PASS skill contract: main entrypoint delegates and preserves write boundaries")

    with tempfile.TemporaryDirectory(prefix="loreforge-") as tmp_raw:
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
            "- `Shared/Raw/<source-id>/` for raw source packages and attachments\n"
            "- `Shared/Templates/` for reusable templates\n\n"
        "Domain layer:\n\n"
        "- `Domains/<domain>/Atlas/`, `Cards/`, `Sources/`, and `Spaces/` for compiled durable knowledge\n\n"
        "Compiled pages live in `Domains/<domain>/Atlas/`, `Cards/`, `Sources/`, and `Spaces/`. "
        "Capture writes raw source packages into `Shared/Raw/<source-id>/` and stops there; ingest updates those packages; `Sources/` is optional for source excerpts.\n\n"
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

        work_item = route(wiki, "create a work item for PyTorch compiler runtime CI failure")
        assert work_item.operation == "work-item"
        assert work_item.primary == "ml-systems"
        assert work_item.requires_confirmation is False
        print("PASS work item: routes durable project records to the matching domain")

    print("main entrypoint flow smoke test ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

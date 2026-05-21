#!/usr/bin/env python3
"""Smoke-test native domain query, ingest, and update boundaries.

The test copies the valid fixture into /tmp, simulates the file effects expected
from loreforge-domain operations, and asserts that only the selected domain changes.
"""

from __future__ import annotations

import hashlib
import re
import shutil
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "skills" / "loreforge-domain" / "scripts"))

from validate_native_domain import validate_domain


TODAY = "2026-04-29"
LOG_ENTRY_PATTERN = re.compile(r"\n## \d{4}-\d{2}-\d{2} \| ")


def digest_tree(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        result[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def changed_paths(before: dict[str, str], after: dict[str, str]) -> set[str]:
    keys = set(before) | set(after)
    return {key for key in keys if before.get(key) != after.get(key)}


def assert_valid(domain: Path) -> None:
    issues = validate_domain(domain)
    if issues:
        lines = "\n".join(issue.line() for issue in issues)
        raise AssertionError(f"{domain} is invalid:\n{lines}")


def assert_no_changes(before: dict[str, str], after: dict[str, str], label: str) -> None:
    changes = changed_paths(before, after)
    if changes:
        raise AssertionError(f"{label} changed unexpectedly: {sorted(changes)}")


def assert_selected_domain_only(before: dict[str, str], after: dict[str, str], selected: str) -> None:
    allowed_prefix = f"Domains/{selected}/"
    changes = changed_paths(before, after)
    leaks = sorted(path for path in changes if not path.startswith(allowed_prefix))
    if leaks:
        raise AssertionError(f"operation changed paths outside {allowed_prefix}: {leaks}")


def assert_selected_domain_or_shared_only(before: dict[str, str], after: dict[str, str], selected: str) -> None:
    allowed_prefixes = (f"Domains/{selected}/", "Shared/Raw/")
    changes = changed_paths(before, after)
    leaks = sorted(path for path in changes if not path.startswith(allowed_prefixes))
    if leaks:
        raise AssertionError(f"operation changed paths outside selected domain or shared source areas: {leaks}")


def insert_log_entry(domain: Path, entry: str) -> None:
    path = domain / "log.md"
    text = path.read_text()
    normalized = entry.strip() + "\n\n"
    match = LOG_ENTRY_PATTERN.search(text)
    if match:
        offset = match.start() + 1
        path.write_text(text[:offset] + normalized + text[offset:])
    else:
        path.write_text(text.rstrip() + "\n\n" + normalized)


def log_headings(domain: Path) -> list[str]:
    text = (domain / "log.md").read_text()
    return re.findall(r"^## .+$", text, flags=re.MULTILINE)


def simulate_query(domain: Path) -> str:
    wiki = domain.parents[1]
    schema = (domain / "SCHEMA.md").read_text()
    index = (domain / "index.md").read_text()
    log = (domain / "log.md").read_text()
    card = (domain / "Cards" / "expert-domain-wiki.md").read_text()
    source_note_path = domain / "Sources" / "agent-domain-boundary-source.md"
    source_note = source_note_path.read_text() if source_note_path.exists() else ""
    manifest = (wiki / "Shared" / "Raw" / "llm-wiki-skill-note" / "manifest.md").read_text()
    return "\n".join([schema, index, log, card, source_note, manifest])


def digest_index(values: dict[str, str]) -> str:
    payload = "\n".join(f"{path}:{digest}" for path, digest in sorted(values.items()))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def simulate_ingest(domain: Path) -> None:
    wiki = domain.parents[1]
    raw_root = wiki / "Shared" / "Raw"
    raw_root.mkdir(parents=True, exist_ok=True)
    raw = raw_root / "agent-domain-boundary-note"
    raw.mkdir(parents=True, exist_ok=True)
    (raw / "original").mkdir(exist_ok=True)
    (raw / "original" / "clip.md").write_text("# Agent Domain Boundary Raw Source\n\nRaw source shared by any domain that needs the boundary note.\n")
    (raw / "assets").mkdir(exist_ok=True)
    origin = raw / "origin.md"
    origin.write_text(f"""---
title: Agent Domain Boundary Raw Source
created: {TODAY}
updated: {TODAY}
type: source
source_type: local note
source_language: en
retrieved_at: {TODAY}
source_description: Local boundary test source
origin: Shared/Raw/agent-domain-boundary-note/origin.md
candidate_domains:
  - ai-research
compiled_pages: []
status: captured
---

# Agent Domain Boundary Raw Source

Raw source shared by any domain that needs the boundary note.
""")
    raw_hash = hashlib.sha256(origin.read_bytes()).hexdigest()
    (raw / "assets" / "diagram.txt").write_text("test attachment\n")
    (raw / "manifest.md").write_text(f"""---
title: Agent Domain Boundary Raw Source
source_id: agent-domain-boundary-note
source_type: local note
source_language: en
retrieved_at: {TODAY}
source_description: Local boundary test source
content_hash: {raw_hash}
origin: Shared/Raw/agent-domain-boundary-note/origin.md
candidate_domains:
  - ai-research
compiled_pages:
  - Domains/{domain.name}/Sources/agent-domain-boundary-source.md
  - Domains/{domain.name}/Cards/domain-boundary-discipline.md
  - Domains/{domain.name}/Cards/agent-domain-boundary-note.md
status: compiled
artifacts:
  - Shared/Raw/agent-domain-boundary-note/original/clip.md
  - Shared/Raw/agent-domain-boundary-note/assets/diagram.txt
---

# Agent Domain Boundary Raw Source

Raw source shared by any domain that needs the boundary note.
""")

    source_dir = domain / "Sources"
    source_dir.mkdir(exist_ok=True)
    source_note = source_dir / "agent-domain-boundary-source.md"
    source_note.write_text(f"""---
title: Agent Domain Boundary Source
created: {TODAY}
updated: {TODAY}
type: source
tags: [wiki, agent, source]
confidence: medium
status: active
contested: false
contradictions: []
---

# Agent Domain Boundary Source

This excerpt preserves the stable parts of the raw boundary note for
[[agent-domain-boundary-note]] and [[domain-boundary-discipline]].[^raw]

[^raw]: [[Shared/Raw/agent-domain-boundary-note/manifest.md]]
""")

    source = domain / "Cards" / "agent-domain-boundary-note.md"
    source.write_text(f"""---
title: Agent Domain Boundary Note
created: {TODAY}
updated: {TODAY}
type: concept
aliases:
  - Agent domain boundary note
tags: [wiki, agent, source]
confidence: medium
status: active
contested: false
contradictions: []
---

# Agent Domain Boundary Note

This source describes why [[expert-domain-wiki]] should update only the selected
domain and why [[domain-boundary-discipline]] belongs in `Cards/`.[^source]

[^source]: [[Sources/agent-domain-boundary-source]]
""")

    card = domain / "Cards" / "domain-boundary-discipline.md"
    card.write_text(f"""---
title: Domain Boundary Discipline
created: {TODAY}
updated: {TODAY}
type: concept
aliases:
  - Domain boundary discipline
tags: [wiki, agent, concept]
confidence: medium
status: active
contested: false
contradictions: []
---

# Domain Boundary Discipline

Domain boundary discipline means an expert updates the selected domain after
orientation and does not write into sibling domains. It connects
[[expert-domain-wiki]] with the source note.[^source]

[^source]: [[Sources/agent-domain-boundary-source]]
""")

    index = domain / "index.md"
    text = index.read_text()
    text = text.replace(
        "> Last updated: 2026-04-29 | Total pages: 4",
        "> Last updated: 2026-04-29 | Total pages: 6",
    )
    text = text.replace(
        "- [[expert-domain-wiki]] - Self-contained expert-owned domain wiki.\n",
        "- [[agent-domain-boundary-note]] - Raw-first note captured as a durable card.\n"
        "- [[domain-boundary-discipline]] - Selected-domain-only update discipline.\n"
        "- [[expert-domain-wiki]] - Self-contained expert-owned domain wiki.\n",
    )
    if "## Sources" not in text:
        text = text.replace("\n## Spaces\n", "\n## Sources\n\n## Spaces\n")
    text = text.replace(
        "## Sources\n\n",
        "## Sources\n- [[agent-domain-boundary-source]] - Optional source excerpt for the boundary note.\n\n",
    )
    index.write_text(text)

    insert_log_entry(
        domain,
        f"""
## {TODAY} | ingest | Agent domain boundary note
- captured: Shared/Raw/agent-domain-boundary-note/
- created: Shared/Raw/agent-domain-boundary-note/origin.md
- created: Shared/Raw/agent-domain-boundary-note/assets/diagram.txt
- created: Shared/Raw/agent-domain-boundary-note/manifest.md
- created: Sources/agent-domain-boundary-source.md
- created: Cards/domain-boundary-discipline.md
- created: Cards/agent-domain-boundary-note.md
- updated: index.md
""",
    )


def simulate_update(domain: Path) -> None:
    card = domain / "Cards" / "expert-domain-wiki.md"
    text = card.read_text()
    text = text.replace(
        "An expert domain wiki is maintained by one expert agent",
        "An expert domain wiki is maintained by one expert agent after orientation",
    )
    if "[[domain-boundary-discipline]]" not in text:
        text += "\nIt should preserve [[domain-boundary-discipline]].\n"
    card.write_text(text)

    insert_log_entry(
        domain,
        f"""
## {TODAY} | update | Expert domain wiki
- updated: Cards/expert-domain-wiki.md
""",
    )


def main() -> int:
    source_root = Path(__file__).resolve().parent / "fixtures" / "native-domain" / "valid" / "wiki"
    with tempfile.TemporaryDirectory(prefix="loreforge-native-ops-") as tmp:
        wiki = Path(tmp) / "wiki"
        shutil.copytree(source_root, wiki)

        selected = "ai-research"
        selected_domain = wiki / "Domains" / selected
        other_domain = wiki / "Domains" / "other-domain"

        assert_valid(selected_domain)
        wiki_before_query = digest_tree(wiki)
        other_before = digest_tree(other_domain)

        query_answer = simulate_query(selected_domain)
        if "Expert Domain Wiki" not in query_answer:
            raise AssertionError("query simulation did not read expected domain page")
        assert_no_changes(wiki_before_query, digest_tree(wiki), "query")

        wiki_before_ingest = digest_tree(wiki)
        simulate_ingest(selected_domain)
        if not log_headings(selected_domain)[0].startswith(f"## {TODAY} | ingest |"):
            raise AssertionError("ingest log entry was not inserted as newest entry")
        assert_valid(selected_domain)
        assert_selected_domain_or_shared_only(wiki_before_ingest, digest_tree(wiki), selected)
        assert_no_changes(other_before, digest_tree(other_domain), "other-domain after ingest")

        wiki_before_update = digest_tree(wiki)
        simulate_update(selected_domain)
        if not log_headings(selected_domain)[0].startswith(f"## {TODAY} | update |"):
            raise AssertionError("update log entry was not inserted as newest entry")
        assert_valid(selected_domain)
        assert_selected_domain_only(wiki_before_update, digest_tree(wiki), selected)
        assert_no_changes(other_before, digest_tree(other_domain), "other-domain after update")

    print("native operation smoke test ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

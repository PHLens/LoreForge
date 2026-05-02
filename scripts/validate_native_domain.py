#!/usr/bin/env python3
"""Validate the minimal LoreForge native domain contract.

Run without arguments to validate the checked-in good and bad fixtures. Run with
one or more domain paths to validate external domains.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


REQUIRED_PATHS = [
    "SCHEMA.md",
    "index.md",
    "log.md",
    "Atlas",
    "Cards",
    "Sources",
    "Spaces",
]

PAGE_DIRS = ["Atlas", "Cards", "Sources", "Spaces"]
REQUIRED_FRONTMATTER = [
    "title",
    "created",
    "updated",
    "type",
    "tags",
    "status",
    "sources",
]
INDEXABLE_SPACE_TAGS = {"person", "entity", "tool", "project"}
EXPECTED_TYPE_BY_DIR = {
    "Atlas": "map",
    "Cards": "concept",
    "Sources": "source",
    "Spaces": "space",
}

FOOTNOTE_REF_RE = re.compile(r"(?<!\^)\[\^([^\]]+)\](?!:)")
FOOTNOTE_DEF_RE = re.compile(r"^\[\^([^\]]+)\]:\s*(.*)$")


@dataclass(frozen=True)
class Issue:
    code: str
    path: str
    message: str

    def line(self) -> str:
        return f"{self.code}: {self.path}: {self.message}"


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def frontmatter(text: str) -> dict[str, str] | None:
    if not text.startswith("---\n"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    fields: dict[str, str] = {}
    for line in parts[1].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields


def list_value(value: str) -> set[str]:
    value = value.strip()
    if not value.startswith("[") or not value.endswith("]"):
        return set()
    inner = value[1:-1].strip()
    if not inner:
        return set()
    return {item.strip().strip("\"'") for item in inner.split(",") if item.strip()}


def taxonomy(schema_text: str) -> set[str]:
    tags: set[str] = set()
    in_taxonomy = False
    for line in schema_text.splitlines():
        if line.startswith("## "):
            in_taxonomy = line.strip().lower() == "## tag taxonomy"
            continue
        if not in_taxonomy or not line.startswith("- "):
            continue
        value = line[2:].strip()
        if ":" in value:
            value = value.split(":", 1)[1]
        for item in re.split(r"[, ]+", value):
            item = item.strip().strip("`")
            if item:
                tags.add(item)
    return tags


def wikilinks(text: str) -> list[str]:
    return [match.split("|", 1)[0].split("#", 1)[0].strip()
            for match in re.findall(r"\[\[([^\]]+)\]\]", text)]


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        return "", text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return "", text
    return f"---{parts[1]}---", parts[2]


def footnote_blocks(lines: list[str]) -> list[tuple[str, int, int]]:
    blocks: list[tuple[str, int, int]] = []
    i = 0
    while i < len(lines):
        match = FOOTNOTE_DEF_RE.match(lines[i])
        if not match:
            i += 1
            continue
        label = match.group(1)
        start = i
        i += 1
        while i < len(lines):
            line = lines[i]
            if line.startswith("    ") or line.startswith("\t"):
                i += 1
                continue
            if line.strip() == "":
                next_index = i + 1
                if next_index < len(lines) and (
                    lines[next_index].startswith("    ") or lines[next_index].startswith("\t")
                ):
                    i += 1
                    continue
            break
        blocks.append((label, start, i))
    return blocks


def footnote_labels(body: str) -> tuple[set[str], set[str]]:
    lines = body.splitlines()
    blocks = footnote_blocks(lines)
    defined = {label for label, _, _ in blocks}
    if not blocks:
        refs = set(FOOTNOTE_REF_RE.findall(body))
        return refs, defined

    block_starts = {start: end for _, start, end in blocks}
    filtered: list[str] = []
    i = 0
    while i < len(lines):
        if i in block_starts:
            i = block_starts[i]
            continue
        filtered.append(lines[i])
        i += 1
    refs = set(FOOTNOTE_REF_RE.findall("\n".join(filtered)))
    return refs, defined


def remove_orphan_footnote_definitions(text: str) -> str:
    prefix, body = split_frontmatter(text)
    if not body:
        return text

    lines = body.splitlines()
    blocks = footnote_blocks(lines)
    if not blocks:
        return text

    refs, _ = footnote_labels(body)
    keep_labels = refs
    block_starts = {start: (label, end) for label, start, end in blocks}

    filtered: list[str] = []
    i = 0
    changed = False
    while i < len(lines):
        block = block_starts.get(i)
        if block is not None:
            label, end = block
            if label in keep_labels:
                filtered.extend(lines[i:end])
            else:
                changed = True
            i = end
            continue
        filtered.append(lines[i])
        i += 1

    if not changed:
        return text

    cleaned_body = "\n".join(filtered).rstrip()
    if cleaned_body:
        cleaned_body += "\n"
    return prefix + cleaned_body


def log_entry_dates(text: str) -> list[str]:
    return re.findall(r"^## (\d{4}-\d{2}-\d{2}) \| ", text, flags=re.MULTILINE)


def is_cross_domain_link(target: str) -> bool:
    return (
        target.startswith("/")
        or target.startswith("../")
        or "/Domains/" in target
        or target.startswith("Domains/")
        or "\\" in target
    )


def active_pages(domain: Path) -> list[Path]:
    pages: list[Path] = []
    for dirname in PAGE_DIRS:
        base = domain / dirname
        if not base.exists():
            continue
        for page in base.rglob("*.md"):
            page_rel = rel(page, domain)
            if page_rel.startswith("Spaces/_archive/"):
                continue
            pages.append(page)
    return sorted(pages)


def archived_pages(domain: Path) -> list[Path]:
    archive = domain / "Spaces" / "_archive"
    if not archive.exists():
        return []
    return sorted(archive.rglob("*.md"))


def expected_type(page: Path, domain: Path) -> str | None:
    parts = page.relative_to(domain).parts
    if not parts:
        return None
    return EXPECTED_TYPE_BY_DIR.get(parts[0])


def should_index(page: Path, domain: Path, fields: dict[str, str]) -> bool:
    top = page.relative_to(domain).parts[0]
    if top != "Spaces":
        return True
    tags = list_value(fields.get("tags", "[]"))
    return bool(tags & INDEXABLE_SPACE_TAGS)


def validate_domain(domain: Path) -> list[Issue]:
    domain = domain.resolve()
    issues: list[Issue] = []

    for name in REQUIRED_PATHS:
        if not (domain / name).exists():
            issues.append(Issue("missing-required-path", name, "required domain path is missing"))

    schema_path = domain / "SCHEMA.md"
    index_path = domain / "index.md"
    log_path = domain / "log.md"
    schema_text = schema_path.read_text() if schema_path.exists() else ""
    index_text = index_path.read_text() if index_path.exists() else ""
    log_text = log_path.read_text() if log_path.exists() else ""
    allowed_tags = taxonomy(schema_text)

    pages = active_pages(domain)
    archived = archived_pages(domain)
    known_stems = {page.stem for page in pages}

    for page in pages:
        page_rel = rel(page, domain)
        text = page.read_text()
        fields = frontmatter(text)
        if fields is None:
            issues.append(Issue("missing-frontmatter", page_rel, "page lacks YAML frontmatter"))
            continue

        for field in REQUIRED_FRONTMATTER:
            if field not in fields:
                issues.append(Issue("missing-frontmatter-field", page_rel, f"missing `{field}`"))

        expected = expected_type(page, domain)
        if expected and fields.get("type") != expected:
            issues.append(Issue("wrong-page-type", page_rel, f"expected type `{expected}`"))

        unknown = list_value(fields.get("tags", "[]")) - allowed_tags
        for tag in sorted(unknown):
            issues.append(Issue("unknown-tag", page_rel, f"`{tag}` not in SCHEMA.md taxonomy"))

        _, body = split_frontmatter(text)
        refs, defined = footnote_labels(body)
        for label in sorted(refs - defined):
            issues.append(Issue("missing-footnote-definition", page_rel, f"`[^{label}]` has no matching definition"))
        for label in sorted(defined - refs):
            issues.append(Issue("orphan-footnote-definition", page_rel, f"`[^{label}]` definition has no body references"))

        if should_index(page, domain, fields):
            if f"[[{page.stem}]]" not in index_text:
                issues.append(Issue("missing-index-entry", page_rel, "indexable page is absent from index.md"))
        elif f"[[{page.stem}]]" in index_text:
            issues.append(Issue("unexpected-index-entry", page_rel, "non-indexable Space appears in index.md"))

        for target in wikilinks(text):
            if is_cross_domain_link(target):
                issues.append(Issue("cross-domain-link", page_rel, f"`[[{target}]]` points outside the domain"))
            elif "/" not in target and target not in known_stems:
                issues.append(Issue("broken-wikilink", page_rel, f"`[[{target}]]` has no active page"))

    for page in archived:
        page_rel = rel(page, domain)
        text = page.read_text()
        fields = frontmatter(text)
        if fields is None:
            issues.append(Issue("missing-frontmatter", page_rel, "archived page lacks YAML frontmatter"))
            continue
        if fields.get("status") != "archived":
            issues.append(Issue("archive-status", page_rel, "archived page must set status: archived"))
        if f"[[{page.stem}]]" in index_text:
            issues.append(Issue("archived-index-entry", page_rel, "archived page must not appear in index.md"))

    if index_path.exists():
        for target in wikilinks(index_text):
            if is_cross_domain_link(target):
                issues.append(Issue("cross-domain-link", "index.md", f"`[[{target}]]` points outside the domain"))
            elif "/" not in target and target not in known_stems:
                issues.append(Issue("broken-wikilink", "index.md", f"`[[{target}]]` has no active page"))

    if log_path.exists():
        dates = log_entry_dates(log_text)
        for earlier, later in zip(dates, dates[1:]):
            if later > earlier:
                issues.append(
                    Issue(
                        "log-order",
                        "log.md",
                        f"`{later}` appears below older `{earlier}`; log entries must be newest first",
                    )
                )

    return sorted(issues, key=lambda issue: (issue.code, issue.path, issue.message))


def fix_orphan_footnotes(domain: Path) -> list[str]:
    changed: list[str] = []
    for page in active_pages(domain):
        text = page.read_text()
        fixed = remove_orphan_footnote_definitions(text)
        if fixed == text:
            continue
        page.write_text(fixed)
        changed.append(rel(page, domain))
    return changed


def run_fixture(name: str, domain: Path, expected_codes: set[str]) -> bool:
    issues = validate_domain(domain)
    codes = {issue.code for issue in issues}
    print(f"== {name}: {domain}")
    if issues:
        for issue in issues:
            print(issue.line())
    else:
        print("ok")

    if expected_codes:
        missing = expected_codes - codes
        if missing:
            print(f"missing expected issue codes: {', '.join(sorted(missing))}")
            return False
        return True

    return not issues


def main(argv: list[str]) -> int:
    fix = False
    if argv and argv[0] in {"--fix", "-f"}:
        fix = True
        argv = argv[1:]

    if argv:
        ok = True
        for arg in argv:
            domain = Path(arg)
            if fix:
                changed = fix_orphan_footnotes(domain)
                for page in changed:
                    print(f"fixed orphan footnotes: {page}")
            issues = validate_domain(domain)
            print(f"== {domain}")
            if issues:
                ok = False
                for issue in issues:
                    print(issue.line())
            else:
                print("ok")
        return 0 if ok else 1

    root = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "native-domain"
    valid = root / "valid" / "wiki" / "Domains" / "ai-research"
    invalid = root / "invalid" / "wiki" / "Domains" / "ai-research"
    invalid_expected = {
        "broken-wikilink",
        "cross-domain-link",
        "missing-frontmatter-field",
        "missing-footnote-definition",
        "missing-index-entry",
        "log-order",
        "orphan-footnote-definition",
        "unknown-tag",
    }

    ok = run_fixture("valid fixture", valid, set())
    ok = run_fixture("invalid fixture", invalid, invalid_expected) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

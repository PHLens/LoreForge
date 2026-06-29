"""Validation strategy for native LoreForge domains."""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from pathlib import Path

from .markdown import (
    clean_scalar,
    footnote_labels,
    frontmatter,
    list_value,
    remove_orphan_footnote_definitions,
    split_frontmatter,
    taxonomy,
    wikilinks,
)
from .model import Issue
from .papers import PAPER_NOTES_RELATIVE_DIR, validate_zotero_paper_notes
from .paths import (
    is_cross_domain_link,
    is_legacy_wiki_path,
    rel,
    wiki_root_for_domain,
)
from .raw import validate_raw_packages


REQUIRED_PATHS = [
    "SCHEMA.md",
    "index.md",
    "log.md",
    "Atlas",
    "Cards",
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
]
REQUIRED_CARD_FRONTMATTER = [
    "aliases",
]
INDEXABLE_SPACE_TAGS = {"person", "entity", "tool", "project"}
INDEXABLE_SPACE_PREFIXES = (("Spaces", "projects"),)
EXPECTED_TYPE_BY_DIR = {
    "Atlas": "map",
    "Cards": "concept",
    "Sources": "source",
    "Spaces": "space",
}

MAX_TAGS_PER_PAGE = 3


def normalized_alias_value(value: str) -> str:
    value = clean_scalar(value).casefold()
    return "".join(
        char for char in value if unicodedata.category(char)[0] not in {"P", "Z"}
    )


def redundant_card_aliases(page: Path, fields: dict[str, str]) -> set[str]:
    aliases = list_value(fields.get("aliases", ""))
    title = normalized_alias_value(fields.get("title", ""))
    stem = normalized_alias_value(page.stem)
    blocked = {value for value in {title, stem} if value}
    return {alias for alias in aliases if normalized_alias_value(alias) in blocked}


def meaningful_card_aliases(page: Path, fields: dict[str, str]) -> set[str]:
    aliases = list_value(fields.get("aliases", ""))
    redundant = redundant_card_aliases(page, fields)
    return aliases - redundant


def log_entry_dates(text: str) -> list[str]:
    return re.findall(r"^## (\d{4}-\d{2}-\d{2}) \| ", text, flags=re.MULTILINE)


def wikilink_target_exists(target: str, domain: Path, wiki: Path | None, known_stems: set[str]) -> bool:
    if is_legacy_wiki_path(target):
        return True

    if "/" not in target:
        return target in known_stems

    if wiki is None:
        return True

    if target.startswith(("Atlas/", "Cards/", "Sources/", "Spaces/")):
        base = domain
    else:
        base = wiki

    path = base / target
    candidates = [path]
    if path.suffix != ".md":
        candidates.append(path.with_suffix(".md"))
    return any(candidate.exists() for candidate in candidates)


def page_link_targets(page: Path, domain: Path, wiki: Path | None) -> set[str]:
    domain_rel = rel(page, domain)
    domain_rel_no_suffix = domain_rel.removesuffix(".md")
    targets = {page.stem, domain_rel, domain_rel_no_suffix}
    if wiki is not None:
        wiki_rel = rel(page, wiki)
        targets.update({wiki_rel, wiki_rel.removesuffix(".md")})
    return {target for target in targets if target}


def has_page_link(text: str, page: Path, domain: Path, wiki: Path | None) -> bool:
    targets = set(wikilinks(text))
    return bool(targets & page_link_targets(page, domain, wiki))


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


def is_paper_note(page: Path, wiki: Path | None) -> bool:
    if wiki is None:
        return False
    try:
        return page.resolve().relative_to((wiki / PAPER_NOTES_RELATIVE_DIR).resolve()).suffix == ".md"
    except ValueError:
        return False


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
    parts = page.relative_to(domain).parts
    top = parts[0]
    if top != "Spaces":
        return True
    if any(part in {"_archive", "archive"} for part in parts):
        return False
    for prefix in INDEXABLE_SPACE_PREFIXES:
        if parts[: len(prefix)] == prefix:
            return True
    tags = list_value(fields.get("tags", "[]"))
    return bool(tags & INDEXABLE_SPACE_TAGS)


def validate_domain(domain: Path) -> list[Issue]:
    domain = domain.resolve()
    issues: list[Issue] = []
    wiki = wiki_root_for_domain(domain)

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
    duplicate_stems = {stem for stem, count in Counter(page.stem for page in pages).items() if count > 1}

    for page in pages:
        page_rel = rel(page, domain)
        text = page.read_text()
        fields = frontmatter(text)
        if fields is None:
            issues.append(Issue("missing-frontmatter", page_rel, "page lacks YAML frontmatter"))
            continue

        paper_note = is_paper_note(page, wiki)

        if not paper_note:
            for field in REQUIRED_FRONTMATTER:
                if field not in fields:
                    issues.append(Issue("missing-frontmatter-field", page_rel, f"missing `{field}`"))

        if page_rel.startswith("Cards/"):
            for field in REQUIRED_CARD_FRONTMATTER:
                if field not in fields:
                    issues.append(Issue("missing-card-frontmatter-field", page_rel, f"missing `{field}`"))
                    continue
                if not list_value(fields.get(field, "")):
                    issues.append(
                        Issue(
                            "empty-card-aliases",
                            page_rel,
                            "`aliases` must contain at least one human-searchable alias",
                        )
                    )
                elif not meaningful_card_aliases(page, fields):
                    issues.append(
                        Issue(
                            "uninformative-card-aliases",
                            page_rel,
                            "`aliases` must include at least one search alias different from title and page stem",
                        )
                    )
                else:
                    redundant_aliases = redundant_card_aliases(page, fields)
                    if redundant_aliases:
                        formatted = ", ".join(f"`{alias}`" for alias in sorted(redundant_aliases))
                        issues.append(
                            Issue(
                                "redundant-card-aliases",
                                page_rel,
                                f"`aliases` repeats the canonical title or page stem: {formatted}",
                            )
                        )

        if "sources" in fields:
            issues.append(
                Issue(
                    "deprecated-frontmatter-field",
                    page_rel,
                    "frontmatter `sources` is no longer used; use inline wikilinks to wiki-local sources "
                    "or footnotes only when provenance is ambiguous",
                )
            )

        expected = expected_type(page, domain)
        if not paper_note and expected and fields.get("type") != expected:
            issues.append(Issue("wrong-page-type", page_rel, f"expected type `{expected}`"))

        if not paper_note:
            unknown = list_value(fields.get("tags", "[]")) - allowed_tags
            for tag in sorted(unknown):
                issues.append(Issue("unknown-tag", page_rel, f"`{tag}` not in SCHEMA.md taxonomy"))

        tags = list_value(fields.get("tags", "[]"))
        if not paper_note and len(tags) > MAX_TAGS_PER_PAGE:
            issues.append(
                Issue(
                    "tag-sprawl",
                    page_rel,
                    f"{len(tags)} tags; keep pages to at most {MAX_TAGS_PER_PAGE}",
                )
            )

        _, body = split_frontmatter(text)
        refs, defined = footnote_labels(body)
        for label in sorted(refs - defined):
            issues.append(Issue("missing-footnote-definition", page_rel, f"`[^{label}]` has no matching definition"))
        for label in sorted(defined - refs):
            issues.append(Issue("orphan-footnote-definition", page_rel, f"`[^{label}]` definition has no body references"))

        if paper_note:
            pass
        elif should_index(page, domain, fields):
            if not has_page_link(index_text, page, domain, wiki):
                issues.append(Issue("missing-index-entry", page_rel, "indexable page is absent from index.md"))
        elif has_page_link(index_text, page, domain, wiki):
            issues.append(Issue("unexpected-index-entry", page_rel, "non-indexable Space appears in index.md"))

        for target in wikilinks(text):
            if is_cross_domain_link(target):
                issues.append(Issue("cross-domain-link", page_rel, f"`[[{target}]]` uses an unsafe path"))
            elif "/" not in target and target in duplicate_stems:
                issues.append(
                    Issue(
                        "ambiguous-wikilink",
                        page_rel,
                        f"`[[{target}]]` matches multiple active pages; use a path-qualified link",
                    )
                )
            elif not wikilink_target_exists(target, domain, wiki, known_stems):
                issues.append(
                    Issue("broken-wikilink", page_rel, f"`[[{target}]]` has no active page")
                )

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
                issues.append(Issue("cross-domain-link", "index.md", f"`[[{target}]]` uses an unsafe path"))
            elif "/" not in target and target in duplicate_stems:
                issues.append(
                    Issue(
                        "ambiguous-wikilink",
                        "index.md",
                        f"`[[{target}]]` matches multiple active pages; use a path-qualified link",
                    )
                )
            elif not wikilink_target_exists(target, domain, wiki, known_stems):
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

    if wiki is not None:
        issues.extend(validate_raw_packages(wiki))
    if wiki is not None and domain == (wiki / "Domains" / "research").resolve():
        issues.extend(validate_zotero_paper_notes(wiki))

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

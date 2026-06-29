"""Validation strategy for Shared/Raw source packages."""

from __future__ import annotations

import hashlib
from pathlib import Path

from .markdown import frontmatter, list_value
from .model import Issue
from .paths import is_wiki_local_path, rel


RAW_REQUIRED_FRONTMATTER = [
    "title",
    "source_id",
    "source_type",
    "source_language",
    "retrieved_at",
    "content_hash",
    "origin",
    "status",
    "candidate_domains",
    "compiled_pages",
]
RAW_STATUS_VALUES = {"captured", "compiled", "stale", "blocked"}


def normalize_sha256(value: str) -> str:
    value = value.strip().strip("\"'")
    if value.startswith("sha256:"):
        value = value.split(":", 1)[1]
    return value.lower()


def validate_raw_packages(wiki: Path) -> list[Issue]:
    wiki = wiki.resolve()
    issues: list[Issue] = []
    raw_root = wiki / "Shared" / "Raw"
    if not raw_root.exists():
        return issues

    for raw_child in sorted(raw_root.iterdir()):
        if raw_child.is_file():
            issues.append(
                Issue(
                    "unexpected-raw-file",
                    rel(raw_child, wiki),
                    "raw sources must live in Shared/Raw/<source-id>/ packages",
                )
            )

    for package in sorted(path for path in raw_root.iterdir() if path.is_dir()):
        manifest_path = package / "manifest.md"
        origin_path = package / "origin.md"
        package_rel = rel(package, wiki)
        manifest_rel = rel(manifest_path, wiki)
        origin_rel = rel(origin_path, wiki)

        if not manifest_path.exists() and not origin_path.exists():
            continue

        if not manifest_path.exists():
            issues.append(Issue("missing-raw-manifest", package_rel, "raw package must include manifest.md"))
            continue

        if not origin_path.exists():
            issues.append(Issue("missing-raw-origin", package_rel, "raw package must include origin.md"))

        text = manifest_path.read_text()
        fields = frontmatter(text)
        if fields is None:
            issues.append(Issue("missing-raw-frontmatter", manifest_rel, "raw manifest lacks YAML frontmatter"))
            continue

        for field in RAW_REQUIRED_FRONTMATTER:
            if field not in fields:
                issues.append(Issue("missing-raw-field", manifest_rel, f"missing `{field}`"))

        if "source_url" not in fields and "source_description" not in fields:
            issues.append(
                Issue(
                    "missing-raw-field",
                    manifest_rel,
                    "missing `source_url` or `source_description`",
                )
            )

        source_id = fields.get("source_id")
        if source_id and source_id != package.name:
            issues.append(
                Issue(
                    "raw-source-id-mismatch",
                    manifest_rel,
                    f"`source_id` should match package folder `{package.name}`",
                )
            )

        status = fields.get("status")
        if status and status not in RAW_STATUS_VALUES:
            issues.append(
                Issue(
                    "invalid-raw-status",
                    manifest_rel,
                    f"`status` must be one of {', '.join(sorted(RAW_STATUS_VALUES))}",
                )
            )

        origin = fields.get("origin", "")
        if origin:
            if not is_wiki_local_path(origin):
                issues.append(Issue("raw-path-outside-wiki", manifest_rel, f"`origin` is not wiki-local: {origin}"))
            elif origin != origin_rel:
                issues.append(Issue("raw-origin-mismatch", manifest_rel, f"`origin` should be `{origin_rel}`"))
            elif not (wiki / origin).exists():
                issues.append(Issue("missing-raw-origin", manifest_rel, f"`origin` path does not exist: {origin}"))

        if origin_path.exists() and fields.get("content_hash"):
            expected_hash = hashlib.sha256(origin_path.read_bytes()).hexdigest()
            actual_hash = normalize_sha256(fields["content_hash"])
            if actual_hash != expected_hash:
                issues.append(
                    Issue(
                        "raw-content-hash-mismatch",
                        manifest_rel,
                        "`content_hash` does not match origin.md",
                    )
                )

        for field in ("artifacts", "compiled_pages"):
            for value in sorted(list_value(fields.get(field, "[]"))):
                if not is_wiki_local_path(value):
                    issues.append(
                        Issue(
                            "raw-path-outside-wiki",
                            manifest_rel,
                            f"`{field}` path is not wiki-local: {value}",
                        )
                    )
                    continue
                target = wiki / value
                if field == "artifacts" and not target.exists():
                    issues.append(Issue("missing-raw-artifact", manifest_rel, f"`{value}` does not exist"))
                if field == "compiled_pages" and value and not target.exists():
                    issues.append(Issue("missing-compiled-page", manifest_rel, f"`{value}` does not exist"))

    return sorted(issues, key=lambda issue: (issue.code, issue.path, issue.message))

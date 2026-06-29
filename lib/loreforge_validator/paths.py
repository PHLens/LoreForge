"""Path helpers shared by LoreForge validator strategies."""

from __future__ import annotations

from pathlib import Path


LEGACY_TOP_LEVEL_DIRS = {"90-Legacy"}


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def wiki_root_for_domain(domain: Path) -> Path | None:
    domain = domain.resolve()
    if len(domain.parts) >= 2 and domain.parent.name == "Domains":
        return domain.parents[1]
    return None


def is_cross_domain_link(target: str) -> bool:
    return target.startswith("/") or target.startswith("../") or "\\" in target


def is_wiki_local_path(value: str) -> bool:
    if not value:
        return False
    if value.startswith("/") or value.startswith("../") or value.startswith("~"):
        return False
    if "\\tmp\\" in value or "/tmp/" in value or value.startswith("tmp/"):
        return False
    return True


def is_legacy_wiki_path(value: str) -> bool:
    normalized = value.lstrip("/")
    return normalized.split("/", 1)[0] in LEGACY_TOP_LEVEL_DIRS

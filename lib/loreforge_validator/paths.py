"""Path helpers shared by LoreForge validator strategies."""

from __future__ import annotations

import re
from pathlib import Path


LEGACY_TOP_LEVEL_DIRS = {"90-Legacy", "z-Legacy"}
NEW_LAYOUT_DOMAIN_ROOT = "Cards"
OLD_LAYOUT_DOMAIN_ROOT = "Domains"
DOMAIN_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


class InvalidDomainName(ValueError):
    """Raised when a caller provides a domain name instead of a safe slug."""


def validate_domain_name(name: str) -> str:
    if not DOMAIN_NAME_PATTERN.fullmatch(name):
        raise InvalidDomainName(
            "domain name must be a slug containing only letters, numbers, underscores, and hyphens"
        )
    return name


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def wiki_root_for_domain(domain: Path) -> Path | None:
    domain = domain.resolve()
    if len(domain.parts) >= 2 and domain.parent.name in {OLD_LAYOUT_DOMAIN_ROOT, NEW_LAYOUT_DOMAIN_ROOT}:
        return domain.parents[1]
    return None


def is_root_card_domain(domain: Path) -> bool:
    return domain.resolve().parent.name == NEW_LAYOUT_DOMAIN_ROOT


def domain_path(wiki: Path, name: str) -> Path:
    """Return the active path for a domain name, preferring the root Cards layout."""
    validate_domain_name(name)
    cards_domain = wiki / NEW_LAYOUT_DOMAIN_ROOT / name
    if cards_domain.exists():
        return cards_domain
    return wiki / OLD_LAYOUT_DOMAIN_ROOT / name


def domain_names(wiki: Path) -> list[str]:
    names: set[str] = set()
    for _name, _path in domain_entries(wiki):
        names.add(_name)
    return sorted(names)


def domain_entries(wiki: Path) -> list[tuple[str, Path]]:
    entries: list[tuple[str, Path]] = []
    cards = wiki / NEW_LAYOUT_DOMAIN_ROOT
    if cards.exists():
        entries.extend((path.name, path) for path in sorted(cards.iterdir()) if path.is_dir())
    domains = wiki / OLD_LAYOUT_DOMAIN_ROOT
    if domains.exists():
        entries.extend((path.name, path) for path in sorted(domains.iterdir()) if path.is_dir())
    return entries


def domain_entry_dicts(wiki: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for name, path in domain_entries(wiki):
        layout = "root-cards" if path.parent.name == NEW_LAYOUT_DOMAIN_ROOT else "legacy-domains"
        entries.append({"name": name, "layout": layout, "path": path.as_posix()})
    return entries


def has_parent_path_component(value: str) -> bool:
    return any(part == ".." for part in value.split("/"))


def is_cross_domain_link(target: str) -> bool:
    return target.startswith("/") or "\\" in target or has_parent_path_component(target)


def is_wiki_local_path(value: str) -> bool:
    if not value:
        return False
    if value.startswith("/") or value.startswith("~") or has_parent_path_component(value):
        return False
    if "\\tmp\\" in value or "/tmp/" in value or value.startswith("tmp/"):
        return False
    return True


def is_legacy_wiki_path(value: str) -> bool:
    normalized = value.lstrip("/")
    return normalized.split("/", 1)[0] in LEGACY_TOP_LEVEL_DIRS

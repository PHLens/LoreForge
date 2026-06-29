#!/usr/bin/env python3
"""Compatibility wrapper for the shared LoreForge validator module.

Run without arguments to validate the checked-in good and bad fixtures. Run with
one or more domain paths to validate external domains.
"""

from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "lib"))

from loreforge_validator import (  # noqa: E402
    Issue,
    fix_orphan_footnotes,
    validate_domain,
    validate_raw_packages,
    validate_zotero_paper_notes,
)
from loreforge_validator.cli import main  # noqa: E402

__all__ = [
    "Issue",
    "fix_orphan_footnotes",
    "main",
    "validate_domain",
    "validate_raw_packages",
    "validate_zotero_paper_notes",
]


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

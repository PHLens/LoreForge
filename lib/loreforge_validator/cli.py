"""Command-line entrypoint for the shared LoreForge validator."""

from __future__ import annotations

import sys
from pathlib import Path

from .domain import fix_orphan_footnotes, validate_domain


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


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
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

    root = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "native-domain"
    valid = root / "valid" / "wiki" / "Domains" / "ai-research"
    invalid = root / "invalid" / "wiki" / "Domains" / "ai-research"
    invalid_expected = {
        "invalid-raw-status",
        "missing-paper-field",
        "missing-paper-heading",
        "missing-paper-pdf",
        "missing-paper-pdf-link",
        "missing-paper-section",
        "broken-wikilink",
        "cross-domain-link",
        "missing-compiled-page",
        "missing-raw-artifact",
        "missing-raw-manifest",
        "missing-raw-origin",
        "missing-frontmatter-field",
        "missing-card-frontmatter-field",
        "missing-footnote-definition",
        "missing-index-entry",
        "log-order",
        "orphan-footnote-definition",
        "paper-note-citekey-mismatch",
        "paper-note-name-mismatch",
        "raw-content-hash-mismatch",
        "raw-source-id-mismatch",
        "unexpected-raw-file",
        "tag-sprawl",
        "unknown-tag",
    }

    ok = run_fixture("valid fixture", valid, set())
    ok = run_fixture("invalid fixture", invalid, invalid_expected) and ok
    return 0 if ok else 1

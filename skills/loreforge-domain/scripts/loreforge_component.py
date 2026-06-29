#!/usr/bin/env python3
"""Read-only LoreForge component surface for external orchestration checks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback
    import tomli as tomllib

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "lib"))

from loreforge_validator import Issue, validate_domain  # noqa: E402


CONTRACT_VERSION = "0.1"
COMPONENT = "loreforge"


def issue(code: str, message: str, *, path: str = "", severity: str = "error") -> dict[str, str]:
    return {"code": code, "message": message, "path": path, "severity": severity}


def default_registry() -> Path:
    return Path.home() / ".config" / "loreforge" / "registry.toml"


def load_registry(path: Path) -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
    if not path.exists():
        return None, [issue("missing-registry", "registry.toml does not exist", path=path.as_posix())]
    try:
        return tomllib.loads(path.read_text(encoding="utf-8")), []
    except Exception as exc:  # noqa: BLE001 - surface parser failure to caller
        return None, [issue("invalid-registry", str(exc), path=path.as_posix())]


def registry_wikis(registry: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not registry:
        return []
    wikis = registry.get("wikis", [])
    return wikis if isinstance(wikis, list) else []


def selected_wiki(
    *,
    explicit_wiki: str | None,
    registry: dict[str, Any] | None,
    wiki_name: str | None,
) -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
    if explicit_wiki:
        return {"name": wiki_name or "", "path": explicit_wiki, "sync": "local", "remote": "", "default_domain": ""}, []

    wikis = registry_wikis(registry)
    if not wikis:
        return None, [issue("missing-wiki-entry", "no [[wikis]] entries found in LoreForge registry")]

    target = wiki_name or (registry or {}).get("default")
    if target:
        for wiki in wikis:
            if wiki.get("name") == target:
                return wiki, []
        return None, [issue("missing-wiki-entry", f"wiki entry not found: {target}")]

    return None, [issue("missing-wiki-selection", "no wiki name or registry default was provided")]


def domain_names(wiki_path: Path) -> list[str]:
    domains = wiki_path / "Domains"
    if not domains.exists():
        return []
    return sorted(path.name for path in domains.iterdir() if path.is_dir())


def component_envelope(operation: str) -> dict[str, Any]:
    return {
        "component": COMPONENT,
        "contract_version": CONTRACT_VERSION,
        "operation": operation,
        "ok": False,
        "issues": [],
    }


def print_result(result: dict[str, Any], *, as_json: bool) -> int:
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"{result['component']} {result['operation']}: {'ok' if result['ok'] else 'issues'}")
        for item in result.get("issues", []):
            path = f"{item['path']}: " if item.get("path") else ""
            print(f"{item['severity']}: {item['code']}: {path}{item['message']}")
    return 0 if result.get("ok") else 1


def cmd_status(args: argparse.Namespace) -> int:
    result = component_envelope("status")
    registry_path = Path(args.registry).expanduser()
    registry, registry_issues = load_registry(registry_path)
    wiki_entry, wiki_issues = selected_wiki(
        explicit_wiki=args.wiki,
        registry=registry,
        wiki_name=args.wiki_name,
    )

    result["registry"] = {
        "path": registry_path.as_posix(),
        "exists": registry_path.exists(),
    }
    result["issues"].extend(registry_issues if not args.wiki else [])
    result["issues"].extend(wiki_issues)

    if wiki_entry:
        wiki_path = Path(str(wiki_entry.get("path", ""))).expanduser()
        domains = domain_names(wiki_path)
        result["selected_wiki"] = {
            "name": str(wiki_entry.get("name", "")),
            "path": wiki_path.as_posix(),
            "exists": wiki_path.exists(),
            "sync": str(wiki_entry.get("sync", "local")),
            "remote": str(wiki_entry.get("remote", "")),
            "sync_bootstrapped": bool(wiki_entry.get("sync_bootstrapped", False)),
            "default_domain": str(wiki_entry.get("default_domain", "")),
            "domains": domains,
        }
        if not wiki_path.exists():
            result["issues"].append(issue("missing-wiki-root", "selected wiki path does not exist", path=wiki_path.as_posix()))
        elif not (wiki_path / "Domains").exists():
            result["issues"].append(issue("missing-domains-dir", "wiki has no Domains directory", path=(wiki_path / "Domains").as_posix()))

    result["ok"] = not any(item["severity"] == "error" for item in result["issues"])
    return print_result(result, as_json=args.json)


def issue_to_dict(item: Issue) -> dict[str, str]:
    return issue(item.code, item.message, path=item.path)


def resolve_wiki(args: argparse.Namespace, result: dict[str, Any]) -> Path | None:
    registry, registry_issues = load_registry(Path(args.registry).expanduser())
    wiki_entry, wiki_issues = selected_wiki(
        explicit_wiki=args.wiki,
        registry=registry,
        wiki_name=args.wiki_name,
    )
    if not args.wiki:
        result["issues"].extend(registry_issues)
    result["issues"].extend(wiki_issues)
    if not wiki_entry:
        return None
    wiki_path = Path(str(wiki_entry.get("path", ""))).expanduser()
    if not wiki_path.exists():
        result["issues"].append(issue("missing-wiki-root", "selected wiki path does not exist", path=wiki_path.as_posix()))
        return None
    return wiki_path


def cmd_validate(args: argparse.Namespace) -> int:
    result = component_envelope("validate")
    wiki_path = resolve_wiki(args, result)
    result["domains"] = []
    if wiki_path:
        if args.all_domains:
            names = domain_names(wiki_path)
        else:
            names = [args.domain] if args.domain else []
        if not names:
            result["issues"].append(issue("missing-domain-selection", "provide --domain or --all-domains"))
        for name in names:
            domain_path = wiki_path / "Domains" / name
            domain_result: dict[str, Any] = {
                "name": name,
                "path": domain_path.as_posix(),
                "ok": False,
                "issues": [],
            }
            if not domain_path.exists():
                domain_result["issues"].append(issue("missing-domain", "domain path does not exist", path=domain_path.as_posix()))
            else:
                domain_result["issues"].extend(issue_to_dict(item) for item in validate_domain(domain_path))
            domain_result["ok"] = not domain_result["issues"]
            result["domains"].append(domain_result)

    result["ok"] = not result["issues"] and all(domain.get("ok") for domain in result["domains"])
    return print_result(result, as_json=args.json)


def cmd_init(args: argparse.Namespace) -> int:
    result = component_envelope("init")
    wiki_path = Path(args.wiki).expanduser()
    sync = args.sync
    remote = args.remote or ""

    if sync in {"rclone", "git"} and not remote:
        result["issues"].append(issue("missing-remote", f"{sync} init requires --remote"))

    result["writes"] = False
    result["note"] = "This is a read-only init plan. LoreForge-owned init performs the actual writes."
    result["registry_entry"] = {
        "name": args.wiki_name,
        "path": wiki_path.as_posix(),
        "sync": sync,
        "remote": remote,
        "default_domain": args.domain,
        "sync_bootstrapped": bool(args.sync_bootstrapped),
    }
    result["actions"] = [
        {"kind": "directory", "path": (wiki_path / "00_System").as_posix()},
        {"kind": "directory", "path": (wiki_path / "Calendar" / "dailynotes").as_posix()},
        {"kind": "directory", "path": (wiki_path / "Calendar" / "weeklynotes").as_posix()},
        {"kind": "directory", "path": (wiki_path / "Shared" / "Raw").as_posix()},
        {"kind": "directory", "path": (wiki_path / "Shared" / "Templates").as_posix()},
        {"kind": "domain", "path": (wiki_path / "Domains" / args.domain).as_posix()},
        {"kind": "registry", "path": default_registry().as_posix()},
    ]
    result["ok"] = not result["issues"]
    return print_result(result, as_json=args.json)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.set_defaults(func=None)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--registry", default=default_registry().as_posix())
    common.add_argument("--wiki-name")
    common.add_argument("--wiki")
    common.add_argument("--json", action="store_true")

    subparsers = parser.add_subparsers(dest="command", required=True)

    status = subparsers.add_parser("status", parents=[common], help="Report LoreForge registry and wiki availability")
    status.set_defaults(func=cmd_status)

    validate = subparsers.add_parser("validate", parents=[common], help="Validate one or all LoreForge domains")
    validate.add_argument("--domain")
    validate.add_argument("--all-domains", action="store_true")
    validate.set_defaults(func=cmd_validate)

    init = subparsers.add_parser("init", help="Return a read-only LoreForge init plan")
    init.add_argument("--wiki", required=True)
    init.add_argument("--domain", required=True)
    init.add_argument("--wiki-name", default="main")
    init.add_argument("--sync", choices=["local", "rclone", "git"], default="local")
    init.add_argument("--remote", default="")
    init.add_argument("--sync-bootstrapped", action="store_true")
    init.add_argument("--json", action="store_true")
    init.set_defaults(func=cmd_init)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

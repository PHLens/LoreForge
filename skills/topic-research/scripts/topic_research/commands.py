from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .browser_ops import (
    login_and_save_state,
    run_browser_extract,
    run_browser_probe,
    run_requests_probe,
)
from .config import DEFAULT_OUTPUT_ROOT, ZHIHU_AUTH_STATE
from .reports import render_research_markdown, render_zhihu_detail_markdown
from .runtime import infer_runtime_profile, resolve_runtime_state
from .search_backends import normalize_backend_to_source, run_search, select_research_candidates
from .text_utils import slugify_text
from .zhihu import parse_zhihu_url, run_zhihu_detail, run_zhihu_native_search_async


def make_output_dir(base: str | None) -> Path:
    from datetime import datetime

    base_dir = Path(base).expanduser() if base else DEFAULT_OUTPUT_ROOT
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir = base_dir / stamp
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


async def probe_command(args: Any) -> None:
    output_dir = make_output_dir(args.output_dir)
    summary: dict[str, Any] = {
        "url": args.url,
        "profile": args.profile,
        "output_dir": str(output_dir),
    }
    try:
        summary["requests_probe"] = run_requests_probe(args.url, args.profile, args.timeout)
    except Exception as exc:
        summary["requests_probe"] = {"ok": False, "error": str(exc)}

    if not args.requests_only:
        try:
            summary["browser_probe"] = await run_browser_probe(
                url=args.url,
                profile=args.profile,
                state_path=args.state,
                headless=not args.headed,
                timeout=args.timeout,
                wait_ms=args.wait_ms,
                capture_patterns=args.capture_pattern,
                output_dir=output_dir,
            )
        except ModuleNotFoundError as exc:
            summary["browser_probe"] = {
                "ok": False,
                "error": f"缺少依赖: {exc}. 先运行 `uv sync && uv run playwright install chromium`。",
            }
        except Exception as exc:
            summary["browser_probe"] = {"ok": False, "error": str(exc)}

    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\nsummary_path={summary_path}")


async def login_command(args: Any) -> None:
    try:
        result = await login_and_save_state(
            url=args.url,
            state_path=args.state,
            profile=args.profile,
            wait_ms=args.wait_ms,
        )
    except ModuleNotFoundError as exc:
        result = {
            "ok": False,
            "error": f"缺少依赖: {exc}. 先运行 `uv sync && uv run playwright install chromium`。",
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))


async def extract_command(args: Any) -> None:
    output_dir = make_output_dir(args.output_dir)
    try:
        result = await run_browser_extract(
            url=args.url,
            profile=args.profile,
            state_path=args.state,
            headless=not args.headed,
            timeout=args.timeout,
            wait_ms=args.wait_ms,
            output_dir=output_dir,
        )
    except ModuleNotFoundError as exc:
        result = {
            "ok": False,
            "error": f"缺少依赖: {exc}. 先运行 `uv sync && uv run playwright install chromium`。",
        }
    except Exception as exc:
        result = {"ok": False, "error": str(exc)}

    summary_path = output_dir / "extract-summary.json"
    summary_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\nsummary_path={summary_path}")


def search_command(args: Any) -> None:
    try:
        result = run_search(
            query=args.query,
            limit=args.limit,
            site=args.site,
            region=args.region,
            source=args.source,
            zhihu_type=args.zhihu_type,
        )
    except Exception as exc:
        result = {"ok": False, "error": str(exc)}

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.output:
        print(f"\noutput_path={args.output}")


async def research_command(args: Any) -> None:
    output_dir = make_output_dir(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    search_runs: list[dict[str, Any]] = []
    seen_backends: set[str] = set()
    backend_plan: list[tuple[str, str | None]] = []

    if args.source == "auto":
        backend_plan.extend(
            [
                ("zhihu", "zhihu.com"),
                ("wechat", "mp.weixin.qq.com"),
                ("generic", None),
            ]
        )
    else:
        backend_plan.append((args.source, args.site))

    for backend, site in backend_plan:
        if backend in seen_backends:
            continue
        seen_backends.add(backend)
        try:
            if backend == "zhihu":
                search_runs.append(
                    await run_zhihu_native_search_async(
                        query=args.topic,
                        limit=args.limit,
                        search_type=args.zhihu_type,
                    )
                )
            else:
                search_runs.append(
                    run_search(
                        query=args.topic,
                        limit=args.limit,
                        site=site,
                        region=args.region,
                        source=backend,
                        zhihu_type=args.zhihu_type,
                    )
                )
        except Exception as exc:
            search_runs.append(
                {
                    "ok": False,
                    "backend": backend,
                    "site": site or "",
                    "error": str(exc),
                    "results": [],
                }
            )

    selected = select_research_candidates(search_runs, args.min_refs, args.max_refs)
    sources: list[dict[str, Any]] = []
    for index, item in enumerate(selected, 1):
        url = item.get("url", "")
        backend = normalize_backend_to_source(item.get("backend", "generic"))
        runtime_profile = infer_runtime_profile(url, backend, args.profile)
        runtime_state = resolve_runtime_state(url, backend, args.state)
        item_dir = output_dir / f"{index:02d}-{slugify_text(item.get('title', url))}"
        item_dir.mkdir(parents=True, exist_ok=True)

        source_record = {
            "index": index,
            "backend": item.get("backend", ""),
            "site": item.get("site", ""),
            "title": item.get("title", ""),
            "url": url,
            "display_url": item.get("display_url", ""),
            "snippet": item.get("snippet", ""),
            "author": item.get("author", "") or item.get("source_account", ""),
            "pub_date": item.get("pub_date", ""),
        }
        try:
            extract_result = await run_browser_extract(
                url=url,
                profile=runtime_profile,
                state_path=runtime_state,
                headless=not args.headed,
                timeout=args.timeout,
                wait_ms=args.wait_ms,
                output_dir=item_dir,
            )
        except Exception as exc:
            extract_result = {"ok": False, "error": str(exc)}

        source_record["extract"] = extract_result
        if extract_result.get("ok"):
            source_record["title"] = extract_result.get("title") or source_record["title"]
            source_record["author"] = extract_result.get("nickname") or source_record["author"]
            source_record["body_preview"] = extract_result.get("body_preview", "")
            source_record["body_text_length"] = extract_result.get("body_text_length", 0)
            source_record["artifacts"] = extract_result.get("artifacts", {})
        sources.append(source_record)

    report = {
        "ok": True,
        "topic": args.topic,
        "search_runs": search_runs,
        "selected_count": len(selected),
        "sources": sources,
    }
    report_json = output_dir / "research-report.json"
    report_md = output_dir / "research-pack.md"
    report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    report_md.write_text(render_research_markdown(args.topic, report), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\nreport_json={report_json}")
    print(f"report_md={report_md}")


async def detail_command(args: Any) -> None:
    parsed = parse_zhihu_url(args.url)
    if not parsed.get("type"):
        result = {"ok": False, "error": f"无法解析知乎链接: {args.url}"}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    output_dir = make_output_dir(args.output_dir)
    runtime_state = args.state or (str(ZHIHU_AUTH_STATE) if ZHIHU_AUTH_STATE.exists() else None)
    detail = await run_zhihu_detail(
        url=args.url,
        state=runtime_state,
        headed=args.headed,
        timeout=args.timeout,
        wait_ms=args.wait_ms,
        answer_limit=args.answer_limit,
        output_dir=output_dir,
    )
    json_file = output_dir / "detail.json"
    md_file = output_dir / "detail.md"
    json_file.write_text(json.dumps(detail, ensure_ascii=False, indent=2), encoding="utf-8")
    md_file.write_text(render_zhihu_detail_markdown(args.url, detail), encoding="utf-8")
    result = {
        "ok": True,
        "url": args.url,
        "type": parsed["type"],
        "artifacts": {
            "json": str(json_file),
            "markdown": str(md_file),
            "html": str(output_dir / "detail.html"),
            "screenshot": str(output_dir / "detail.png"),
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

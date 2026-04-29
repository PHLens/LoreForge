from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

from .config import HEADER_PROFILES
from .text_utils import canonical_result_url, host_matches, strip_tags, unescape
from .zhihu import run_zhihu_native_search


def infer_search_backend(source: str, site: str | None) -> str:
    if source != "auto":
        return source
    site = (site or "").lower()
    if "zhihu.com" in site:
        return "zhihu"
    if "mp.weixin.qq.com" in site or "weixin.sogou.com" in site:
        return "wechat"
    return "generic"


def normalize_backend_to_source(backend: str) -> str:
    if backend.startswith("zhihu"):
        return "zhihu"
    if backend.startswith("wechat"):
        return "wechat"
    return "generic"


def run_bing_rss_search(query: str, limit: int, site: str | None = None) -> dict[str, Any]:
    search_query = f"site:{site} {query.strip()}" if site else query.strip()
    url = "https://www.bing.com/search?format=rss&q=" + quote(search_query)
    request = Request(url, headers={"User-Agent": HEADER_PROFILES["desktop"]["User-Agent"]})
    xml_text = urlopen(request, timeout=20).read().decode("utf-8", "ignore")
    root = ET.fromstring(xml_text)
    results: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    for item in root.findall("./channel/item"):
        if len(results) >= limit:
            break
        href = (item.findtext("link") or "").strip()
        if not href or not host_matches(href, site):
            continue
        canonical_url = canonical_result_url(href)
        if canonical_url in seen_urls:
            continue
        seen_urls.add(canonical_url)
        results.append(
            {
                "title": strip_tags(item.findtext("title") or ""),
                "url": canonical_url,
                "display_url": urlparse(href).netloc,
                "snippet": strip_tags(item.findtext("description") or ""),
                "pub_date": (item.findtext("pubDate") or "").strip(),
            }
        )
    return {
        "ok": True,
        "backend": "bing_rss",
        "query": query,
        "site": site or "",
        "count": len(results),
        "results": results,
    }


def run_wechat_sogou_search(query: str, limit: int) -> dict[str, Any]:
    import re

    url = "https://weixin.sogou.com/weixin?type=2&query=" + quote(query)
    request = Request(url, headers={"User-Agent": HEADER_PROFILES["desktop"]["User-Agent"]})
    html = urlopen(request, timeout=20).read().decode("utf-8", "ignore")
    li_pattern = re.compile(
        r'<li[^>]+id="sogou_vr_11002601_box_\d+"[^>]*>(.*?)</li>',
        flags=re.IGNORECASE | re.DOTALL,
    )
    title_pattern = re.compile(
        r'<a[^>]*href="([^"]+)"[^>]*id="sogou_vr_11002601_title_\d+"[^>]*>(.*?)</a>'
        r'|<a[^>]*id="sogou_vr_11002601_title_\d+"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
        flags=re.IGNORECASE | re.DOTALL,
    )
    summary_pattern = re.compile(r'<p class="txt-info"[^>]*>(.*?)</p>', flags=re.IGNORECASE | re.DOTALL)
    source_pattern = re.compile(r'<span class="all-time-y2">(.*?)</span>', flags=re.IGNORECASE | re.DOTALL)
    time_pattern = re.compile(r"timeConvert\('(\d+)'\)")

    results = []
    for block in li_pattern.findall(html):
        if len(results) >= limit:
            break
        title_match = title_pattern.search(block)
        if not title_match:
            continue
        href = unescape(title_match.group(1) or title_match.group(3) or "")
        if href.startswith("/"):
            href = "https://weixin.sogou.com" + href
        title = strip_tags(title_match.group(2) or title_match.group(4) or "")
        summary_match = summary_pattern.search(block)
        source_match = source_pattern.search(block)
        time_match = time_pattern.search(block)
        pub_date = ""
        if time_match:
            pub_date = datetime.fromtimestamp(int(time_match.group(1))).isoformat(sep=" ")
        results.append(
            {
                "title": title,
                "url": href,
                "display_url": "weixin.sogou.com",
                "snippet": strip_tags(summary_match.group(1) if summary_match else ""),
                "source_account": strip_tags(source_match.group(1) if source_match else ""),
                "pub_date": pub_date,
            }
        )
    return {
        "ok": True,
        "backend": "wechat_sogou",
        "query": query,
        "site": "mp.weixin.qq.com",
        "count": len(results),
        "results": results,
    }


def run_search(
    query: str,
    limit: int,
    site: str | None = None,
    region: str = "wt-wt",
    source: str = "auto",
    zhihu_type: str = "all",
) -> dict[str, Any]:
    backend = infer_search_backend(source, site)
    if backend == "zhihu":
        return run_zhihu_native_search(query=query, limit=limit, search_type=zhihu_type)
    if backend == "wechat":
        return run_wechat_sogou_search(query=query, limit=limit)
    result = run_bing_rss_search(query=query, limit=limit, site=site)
    result["region"] = region
    return result


def select_research_candidates(
    search_results: list[dict[str, Any]],
    min_refs: int,
    max_refs: int,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    seen_domains: set[str] = set()

    for result in search_results:
        backend = result.get("backend", "")
        for item in result.get("results", []):
            url = item.get("url", "")
            if not url:
                continue
            canonical = canonical_result_url(url)
            domain = urlparse(canonical).netloc
            if canonical in seen_urls:
                continue
            if domain in seen_domains and len(selected) < min_refs:
                continue
            selected.append(
                {
                    "backend": backend,
                    "site": result.get("site", ""),
                    **item,
                    "url": canonical,
                }
            )
            seen_urls.add(canonical)
            if domain:
                seen_domains.add(domain)
            if len(selected) >= max_refs:
                return selected

    for result in search_results:
        backend = result.get("backend", "")
        for item in result.get("results", []):
            url = item.get("url", "")
            if not url:
                continue
            canonical = canonical_result_url(url)
            if canonical in seen_urls:
                continue
            selected.append(
                {
                    "backend": backend,
                    "site": result.get("site", ""),
                    **item,
                    "url": canonical,
                }
            )
            seen_urls.add(canonical)
            if len(selected) >= max_refs:
                return selected
    return selected

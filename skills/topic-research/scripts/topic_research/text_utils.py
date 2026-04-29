from __future__ import annotations

import hashlib
import re
from html import unescape
from urllib.parse import parse_qs, unquote, urlparse


def normalize_text(text: str) -> str:
    text = text.replace("\r", "")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def regex_hits(patterns: list[str], *values: str | None) -> list[str]:
    text = "\n".join(v for v in values if v)
    return [p for p in patterns if re.search(p, text, flags=re.IGNORECASE)]


def strip_title(html: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    title = re.sub(r"\s+", " ", match.group(1)).strip()
    return unescape(title)


def extract_js_string(html: str, var_name: str) -> str:
    pattern = rf"""(?:var|window\.)\s*{re.escape(var_name)}\s*=\s*(['"])(.*?)\1"""
    match = re.search(pattern, html, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    value = re.sub(r"\s+", " ", match.group(2)).strip()
    return unescape(value)


def strip_tags(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    return normalize_text(text)


def zhihu_strip_html_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "")


def parse_vote_count(text: str) -> int:
    text = (text or "").replace(",", "").strip()
    if not text:
        return 0
    match = re.search(r"(\d+(?:\.\d+)?)\s*万", text)
    if match:
        return int(float(match.group(1)) * 10000)
    match = re.search(r"(\d+)", text)
    return int(match.group(1)) if match else 0


def parse_comment_count(text: str) -> int:
    match = re.search(r"(\d+)", text or "")
    return int(match.group(1)) if match else 0


def html_to_text_snippet(html: str, limit: int = 300) -> str:
    return strip_tags(html)[:limit]


def slugify_text(value: str, limit: int = 48) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    if not cleaned:
        cleaned = hashlib.sha1(value.encode("utf-8")).hexdigest()[:12]
    return cleaned[:limit].strip("-") or "item"


def is_probably_url(value: str) -> bool:
    return bool(re.match(r"^https?://", value.strip(), flags=re.IGNORECASE))


def decode_duckduckgo_href(href: str) -> str:
    href = unescape(href)
    if href.startswith("//"):
        href = "https:" + href
    parsed = urlparse(href)
    qs = parse_qs(parsed.query)
    if "uddg" in qs:
        return unquote(qs["uddg"][0])
    return href


def host_matches(url: str, site: str | None) -> bool:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if host == "duckduckgo.com":
        return False
    if not site:
        return True
    site = site.lower()
    return host == site or host.endswith("." + site)


def canonical_result_url(url: str) -> str:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    filtered_query = {
        k: v
        for k, v in query.items()
        if k.lower() not in {"write", "utm_source", "utm_medium", "utm_campaign"}
    }
    clean_query = "&".join(
        f"{k}={value}"
        for k in sorted(filtered_query)
        for value in filtered_query[k]
        if value
    )
    base = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    return base + (f"?{clean_query}" if clean_query else "")

from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener

from .config import BLOCK_PATTERNS, CAPTCHA_PATTERNS, HEADER_PROFILES, LOGIN_PATTERNS
from .text_utils import extract_js_string, regex_hits, strip_tags, strip_title, unescape


def extract_page_metadata(html: str) -> dict[str, str]:
    title = strip_title(html)
    js_title = extract_js_string(html, "msg_title")
    nickname = extract_js_string(html, "nickname")
    return {
        "title": js_title or title,
        "nickname": nickname,
    }


def likely_has_article_content(html: str) -> bool:
    text = re.sub(r"<script.*?</script>", "", html, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<style.*?</style>", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return len(text) >= 400


def has_strong_content_signals(html: str, title: str) -> bool:
    if likely_has_article_content(html) and title:
        return True
    patterns = [
        r'property=["\']og:title["\']',
        r'property=["\']og:description["\']',
        r"QuestionAnswer-content",
        r"RichContent-inner",
        r'id=["\']js_content["\']',
        r'class=["\'][^"\']*RichText[^"\']*["\']',
    ]
    return any(re.search(pattern, html, flags=re.IGNORECASE) for pattern in patterns)


def classify_result(
    final_url: str,
    status: int | None,
    title: str,
    html: str,
) -> tuple[str, dict[str, list[str]]]:
    captcha_hits = regex_hits(CAPTCHA_PATTERNS, final_url, title, html[:20000])
    login_hits = regex_hits(LOGIN_PATTERNS, final_url, title, html[:20000])
    block_hits = regex_hits(BLOCK_PATTERNS, final_url, title, html[:20000])
    strong_content = has_strong_content_signals(html, title)

    if captcha_hits:
        return "captcha_or_challenge", {
            "captcha": captcha_hits,
            "login": login_hits,
            "block": block_hits,
        }
    if login_hits and not likely_has_article_content(html):
        return "login_required", {
            "captcha": captcha_hits,
            "login": login_hits,
            "block": block_hits,
        }
    if strong_content and not block_hits:
        return "content_accessible", {
            "captcha": captcha_hits,
            "login": login_hits,
            "block": block_hits,
        }
    if status in {401, 403, 429} or block_hits:
        return "blocked_http", {
            "captcha": captcha_hits,
            "login": login_hits,
            "block": block_hits,
        }
    if title or likely_has_article_content(html):
        return "content_accessible", {
            "captcha": captcha_hits,
            "login": login_hits,
            "block": block_hits,
        }
    return "unclear", {
        "captcha": captcha_hits,
        "login": login_hits,
        "block": block_hits,
    }


def recommendation_for(classification: str) -> str:
    mapping = {
        "content_accessible": "页面已可达。优先检查 matched-responses.json 是否已有结构化 JSON，其次再解析保存的 HTML。",
        "login_required": "页面看起来需要登录。用 headed 模式运行 login 保存 storage state，再带 --state 重跑 probe。",
        "captcha_or_challenge": "页面进入验证码或挑战流。优先走人工完成验证 + 保存浏览器态，否则请求正文导出或可访问替代来源。不要承诺自动绕过。",
        "blocked_http": "页面像是被 WAF、限流、IP 或网络策略拦住。降低请求频率，复用真实浏览器态，或改用替代来源。",
        "unclear": "结果不够明确。检查截图和 HTML，增加 --wait-ms，或调整 --profile 与 --capture-pattern 后重试。",
    }
    return mapping[classification]


async def apply_stealth_if_available(page: Any) -> None:
    try:
        from playwright_stealth import Stealth
    except Exception:
        return
    stealth = Stealth()
    await stealth.apply_stealth_async(page)


def matches_capture_patterns(url: str, content_type: str, patterns: list[str]) -> bool:
    if not patterns:
        return any(token in url.lower() for token in ("api", "graphql", "ajax", "json"))
    for pattern in patterns:
        if re.search(pattern, url, flags=re.IGNORECASE) or re.search(
            pattern, content_type, flags=re.IGNORECASE
        ):
            return True
    return False


def run_requests_probe(url: str, profile: str, timeout: int) -> dict[str, Any]:
    headers = dict(HEADER_PROFILES[profile])
    try:
        import requests  # type: ignore
    except ModuleNotFoundError:
        request = Request(url, headers=headers)
        opener = build_opener()
        response_headers = None
        try:
            response = opener.open(request, timeout=timeout)
            html_bytes = response.read()
            final_url = response.geturl()
            status = getattr(response, "status", response.getcode())
            response_headers = response.headers
        except HTTPError as exc:
            html_bytes = exc.read()
            final_url = exc.geturl()
            status = exc.code
            response_headers = exc.headers
        except URLError as exc:
            raise RuntimeError(f"urllib probe failed: {exc}") from exc

        charset = "utf-8"
        content_type = (
            response_headers.get_content_charset() if response_headers is not None else None
        )
        if content_type:
            charset = content_type
        html = html_bytes.decode(charset, errors="ignore")
    else:
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        html = response.text
        final_url = response.url
        status = response.status_code

    metadata = extract_page_metadata(html)
    classification, indicators = classify_result(final_url, status, metadata["title"], html)
    return {
        "ok": True,
        "profile": profile,
        "final_url": final_url,
        "status": status,
        "title": metadata["title"],
        "nickname": metadata["nickname"],
        "content_length": len(html),
        "classification": classification,
        "indicators": indicators,
        "recommendation": recommendation_for(classification),
    }


async def run_browser_probe(
    url: str,
    profile: str,
    state_path: str | None,
    headless: bool,
    timeout: int,
    wait_ms: int,
    capture_patterns: list[str],
    output_dir: Path,
) -> dict[str, Any]:
    from playwright.async_api import async_playwright

    captured_responses: list[dict[str, Any]] = []
    pending_tasks: set[asyncio.Task[Any]] = set()
    headers = HEADER_PROFILES[profile]

    async def record_response(response: Any) -> None:
        content_type = response.headers.get("content-type", "")
        if not matches_capture_patterns(response.url, content_type, capture_patterns):
            return
        entry: dict[str, Any] = {
            "url": response.url,
            "status": response.status,
            "content_type": content_type,
            "resource_type": response.request.resource_type,
        }
        if any(token in content_type.lower() for token in ("json", "text", "javascript")):
            try:
                body = await response.text()
            except Exception:
                body = ""
            if body:
                entry["snippet"] = body[:1500]
        captured_responses.append(entry)

    def schedule(coro: Any) -> None:
        task = asyncio.create_task(coro)
        pending_tasks.add(task)
        task.add_done_callback(pending_tasks.discard)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
        )
        context_kwargs: dict[str, Any] = {
            "user_agent": headers["User-Agent"],
            "locale": "zh-CN",
            "viewport": {"width": 1440, "height": 1080},
            "extra_http_headers": headers,
            "service_workers": "block",
        }
        if state_path:
            context_kwargs["storage_state"] = state_path
        context = await browser.new_context(**context_kwargs)
        page = await context.new_page()
        await apply_stealth_if_available(page)
        page.on("response", lambda response: schedule(record_response(response)))

        response = await page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)
        await page.wait_for_timeout(wait_ms)
        final_url = page.url
        html = await page.content()
        title = await page.title()
        metadata = extract_page_metadata(html)
        if not title:
            title = metadata["title"]

        html_path = output_dir / "page.html"
        screenshot_path = output_dir / "page.png"
        response_path = output_dir / "matched-responses.json"
        html_path.write_text(html, encoding="utf-8")
        await page.screenshot(path=str(screenshot_path), full_page=True)
        if pending_tasks:
            await asyncio.gather(*list(pending_tasks), return_exceptions=True)
        response_path.write_text(
            json.dumps(captured_responses, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        status = response.status if response else None
        classification, indicators = classify_result(final_url, status, title, html)
        result = {
            "ok": True,
            "profile": profile,
            "used_state": state_path,
            "headless": headless,
            "final_url": final_url,
            "status": status,
            "title": title,
            "nickname": metadata["nickname"],
            "content_length": len(html),
            "classification": classification,
            "indicators": indicators,
            "captured_response_count": len(captured_responses),
            "artifacts": {
                "html": str(html_path),
                "screenshot": str(screenshot_path),
                "responses": str(response_path),
            },
            "recommendation": recommendation_for(classification),
        }
        await context.close()
        await browser.close()
        return result


async def extract_from_browser_page(page: Any, metadata: dict[str, str]) -> dict[str, Any]:
    extracted = await page.evaluate(
        """
() => {
  const textOf = (selector) => {
    const el = document.querySelector(selector);
    return el ? (el.innerText || el.textContent || '').trim() : '';
  };
  const metaOf = (selector) => {
    const el = document.querySelector(selector);
    return el ? (el.getAttribute('content') || '').trim() : '';
  };
  const htmlOf = (selector) => {
    const el = document.querySelector(selector);
    return el ? el.innerHTML : '';
  };
  const candidates = [
    ['wechat', '#js_content'],
    ['article', 'article'],
    ['main', 'main'],
    ['role_main', '[role="main"]'],
    ['entry_content', '.entry-content'],
    ['post_content', '.post-content'],
    ['content', '#content'],
    ['content_class', '.content'],
  ];

  let best = {kind: '', selector: '', text: '', html: ''};
  for (const [kind, selector] of candidates) {
    const text = textOf(selector);
    if (text.length > best.text.length) {
      best = {kind, selector, text, html: htmlOf(selector)};
    }
  }
  if (!best.text) {
    best = {
      kind: 'body',
      selector: 'body',
      text: (document.body && (document.body.innerText || document.body.textContent || '').trim()) || '',
      html: (document.body && document.body.innerHTML) || '',
    };
  }

  const ogTitle = metaOf('meta[property="og:title"]');
  const zhihuAuthorMatch = ogTitle.match(/ - (.+?) 的回答$/);

  return {
    dom_title: textOf('#activity-name') || textOf('h1'),
    dom_nickname: textOf('#js_name') || textOf('.account_nickname_inner') || textOf('.wx_follow_nickname_normal_font') || textOf('.rich_media_meta_nickname') || (zhihuAuthorMatch ? zhihuAuthorMatch[1] : ''),
    publish_time: textOf('#publish_time') || textOf('.publish_time'),
    body_kind: best.kind,
    body_selector: best.selector,
    body_text: best.text,
    body_html: best.html,
  };
}
"""
    )
    title = extracted.get("dom_title") or metadata["title"]
    nickname = extracted.get("dom_nickname") or metadata["nickname"]
    body_text = strip_tags(extracted.get("body_html", ""))
    return {
        "title": title,
        "nickname": nickname,
        "publish_time": extracted.get("publish_time", "").strip(),
        "body_kind": extracted.get("body_kind", ""),
        "body_selector": extracted.get("body_selector", ""),
        "body_text": body_text,
        "body_html": extracted.get("body_html", ""),
        "body_preview": body_text[:400],
    }


async def run_browser_extract(
    url: str,
    profile: str,
    state_path: str | None,
    headless: bool,
    timeout: int,
    wait_ms: int,
    output_dir: Path,
) -> dict[str, Any]:
    from playwright.async_api import async_playwright

    headers = HEADER_PROFILES[profile]
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
        )
        context_kwargs: dict[str, Any] = {
            "user_agent": headers["User-Agent"],
            "locale": "zh-CN",
            "viewport": {"width": 1440, "height": 1080},
            "extra_http_headers": headers,
            "service_workers": "block",
        }
        if state_path:
            context_kwargs["storage_state"] = state_path
        context = await browser.new_context(**context_kwargs)
        page = await context.new_page()
        await apply_stealth_if_available(page)
        response = await page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)
        await page.wait_for_timeout(wait_ms)

        final_url = page.url
        raw_html = await page.content()
        metadata = extract_page_metadata(raw_html)
        page_title = await page.title()
        if page_title:
            metadata["title"] = page_title

        html_path = output_dir / "page.html"
        screenshot_path = output_dir / "page.png"
        html_path.write_text(raw_html, encoding="utf-8")
        await page.screenshot(path=str(screenshot_path), full_page=True)

        status = response.status if response else None
        classification, indicators = classify_result(final_url, status, metadata["title"], raw_html)
        result: dict[str, Any] = {
            "ok": True,
            "profile": profile,
            "used_state": state_path,
            "headless": headless,
            "final_url": final_url,
            "status": status,
            "title": metadata["title"],
            "nickname": metadata["nickname"],
            "classification": classification,
            "indicators": indicators,
            "artifacts": {
                "html": str(html_path),
                "screenshot": str(screenshot_path),
            },
            "recommendation": recommendation_for(classification),
        }
        if classification != "content_accessible":
            await context.close()
            await browser.close()
            return result

        extracted = await extract_from_browser_page(page, metadata)
        extracted_json_path = output_dir / "extracted.json"
        extracted_text_path = output_dir / "content.txt"
        extracted_html_path = output_dir / "content.html"
        extracted_text_path.write_text(extracted["body_text"], encoding="utf-8")
        extracted_html_path.write_text(extracted["body_html"], encoding="utf-8")
        extracted_record = {
            "url": final_url,
            "title": extracted["title"],
            "nickname": extracted["nickname"],
            "publish_time": extracted["publish_time"],
            "body_kind": extracted["body_kind"],
            "body_selector": extracted["body_selector"],
            "body_preview": extracted["body_preview"],
            "body_text_length": len(extracted["body_text"]),
            "body_html_length": len(extracted["body_html"]),
            "artifacts": {
                "text": str(extracted_text_path),
                "html": str(extracted_html_path),
            },
        }
        extracted_json_path.write_text(
            json.dumps(extracted_record, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        result.update(
            {
                "title": extracted["title"] or result["title"],
                "nickname": extracted["nickname"] or result["nickname"],
                "publish_time": extracted["publish_time"],
                "body_kind": extracted["body_kind"],
                "body_selector": extracted["body_selector"],
                "body_text_length": len(extracted["body_text"]),
                "body_preview": extracted["body_preview"],
                "artifacts": {
                    **result["artifacts"],
                    "extracted_json": str(extracted_json_path),
                    "content_text": str(extracted_text_path),
                    "content_html": str(extracted_html_path),
                },
            }
        )
        await context.close()
        await browser.close()
        return result


async def login_and_save_state(
    url: str,
    state_path: str,
    profile: str,
    wait_ms: int,
) -> dict[str, Any]:
    from playwright.async_api import async_playwright

    headers = HEADER_PROFILES[profile]
    state_file = Path(state_path)
    state_file.parent.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
        )
        context = await browser.new_context(
            user_agent=headers["User-Agent"],
            locale="zh-CN",
            viewport={"width": 1440, "height": 1080},
            extra_http_headers=headers,
        )
        page = await context.new_page()
        await apply_stealth_if_available(page)
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(wait_ms)
        print("请在打开的浏览器中手动完成登录或验证。")
        print("确认目标页面已经处于可访问状态后，回到终端按 Enter 保存浏览器态。")
        input()
        await context.storage_state(path=str(state_file))
        final_url = page.url
        title = await page.title()
        await context.close()
        await browser.close()
        return {
            "ok": True,
            "state_path": str(state_file),
            "final_url": final_url,
            "title": title,
        }

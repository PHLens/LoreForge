from __future__ import annotations

import asyncio
import re
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlparse

from .browser_ops import apply_stealth_if_available
from .config import HEADER_PROFILES, ZHIHU_AUTH_STATE, ZHIHU_SEARCH_API_URL
from .reports import render_zhihu_detail_markdown
from .text_utils import (
    html_to_text_snippet,
    parse_comment_count,
    parse_vote_count,
    strip_tags,
    zhihu_strip_html_tags,
)


def parse_zhihu_url(url: str) -> dict[str, str | int | None]:
    result: dict[str, str | int | None] = {
        "type": None,
        "id": None,
        "question_id": None,
    }
    question_answer = re.search(r"zhihu\.com/question/(\d+)/answer/(\d+)", url)
    if question_answer:
        result["type"] = "answer"
        result["question_id"] = int(question_answer.group(1))
        result["id"] = int(question_answer.group(2))
        return result
    question = re.search(r"zhihu\.com/question/(\d+)", url)
    if question:
        result["type"] = "question"
        result["id"] = int(question.group(1))
        return result
    article = re.search(r"zhuanlan\.zhihu\.com/p/(\d+)", url)
    if article:
        result["type"] = "article"
        result["id"] = article.group(1)
        return result
    return result


def zhihu_build_result(item: dict[str, Any]) -> dict[str, Any] | None:
    item_type = item.get("type", "")
    obj = item.get("object", item)
    highlight = item.get("highlight", {}) or {}

    if item_type == "search_result":
        obj = item.get("object", {})
        item_type = obj.get("type", item.get("type", ""))
    if item_type not in ("answer", "article", "question", "people"):
        return None

    title = highlight.get("title", "")
    if not title:
        if item_type == "answer":
            question = obj.get("question", {}) or {}
            title = question.get("title", "") or obj.get("title", "")
        elif item_type == "people":
            title = obj.get("name", "")
        else:
            title = obj.get("title", "")

    excerpt = (
        highlight.get("description", "")
        or obj.get("excerpt", "")
        or obj.get("headline", "")
    )
    author = ""
    if item_type in ("answer", "article"):
        author = (obj.get("author", {}) or {}).get("name", "")
    elif item_type == "people":
        author = obj.get("name", "")

    item_id = str(obj.get("id", ""))
    url = obj.get("url", "")
    if url and url.startswith("https://api.zhihu.com/"):
        url = ""
    if not url:
        if item_type == "answer":
            question_id = obj.get("question", {}).get("id", "")
            url = f"https://www.zhihu.com/question/{question_id}/answer/{item_id}"
        elif item_type == "question":
            url = f"https://www.zhihu.com/question/{item_id}"
        elif item_type == "article":
            url = f"https://zhuanlan.zhihu.com/p/{item_id}"
        elif item_type == "people":
            url_token = obj.get("url_token", "")
            url = f"https://www.zhihu.com/people/{url_token}"

    return {
        "title": zhihu_strip_html_tags(title),
        "url": url,
        "display_url": urlparse(url).netloc,
        "snippet": zhihu_strip_html_tags(excerpt),
        "type": item_type,
        "author": author,
        "vote_count": obj.get("voteup_count", 0) or 0,
        "comment_count": obj.get("comment_count", 0) or 0,
    }


async def run_zhihu_native_search_async(
    query: str,
    limit: int,
    search_type: str = "all",
) -> dict[str, Any]:
    from playwright.async_api import async_playwright

    headers = HEADER_PROFILES["desktop"]
    encoded_query = quote(query)
    fetch_limit = limit if search_type == "all" else max(limit * 4, 12)
    search_url = (
        f"{ZHIHU_SEARCH_API_URL}?t=general&q={encoded_query}&correction=1&offset=0&limit={fetch_limit}"
    )

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=True,
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
        if ZHIHU_AUTH_STATE.exists():
            context_kwargs["storage_state"] = str(ZHIHU_AUTH_STATE)
        context = await browser.new_context(**context_kwargs)
        page = await context.new_page()
        await apply_stealth_if_available(page)

        response = await page.goto(search_url, wait_until="networkidle", timeout=30000)
        if response is None:
            raise RuntimeError("知乎搜索请求没有返回响应")
        if not response.ok:
            raise RuntimeError(f"知乎搜索响应失败: HTTP {response.status}")
        data = await response.json()
        items = data.get("data", [])
        results = []
        for item in items:
            parsed = zhihu_build_result(item)
            if parsed:
                if search_type != "all" and parsed.get("type") != search_type:
                    continue
                results.append(parsed)
            if len(results) >= limit:
                break

        await context.close()
        await browser.close()

    return {
        "ok": True,
        "backend": "zhihu_native",
        "query": query,
        "site": "zhihu.com",
        "search_type": search_type,
        "count": len(results),
        "results": results,
    }


def run_zhihu_native_search(query: str, limit: int, search_type: str = "all") -> dict[str, Any]:
    return asyncio.run(
        run_zhihu_native_search_async(
            query=query,
            limit=limit,
            search_type=search_type,
        )
    )


async def zhihu_extract_question_detail(page: Any) -> dict[str, Any]:
    title_el = page.locator("h1.QuestionHeader-title").first
    title = await title_el.inner_text() if await title_el.count() > 0 else ""
    detail_el = page.locator(".QuestionRichText, .QuestionHeader-detail").first
    detail = await detail_el.inner_html() if await detail_el.count() > 0 else ""
    answer_count_el = page.locator(".List-headerText").first
    answer_count = 0
    if await answer_count_el.count() > 0:
        answer_count = parse_comment_count(await answer_count_el.inner_text())
    return {
        "title": title.strip(),
        "detail_html": detail,
        "detail_text": strip_tags(detail),
        "answer_count": answer_count,
    }


async def zhihu_extract_answer_content(item: Any) -> dict[str, Any]:
    author_el = item.locator(".AuthorInfo-name").first
    author = await author_el.inner_text() if await author_el.count() > 0 else ""
    content_el = item.locator(".RichContent-inner").first
    content_html = await content_el.inner_html() if await content_el.count() > 0 else ""
    vote_el = item.locator(".VoteButton--up").first
    vote_count = parse_vote_count(await vote_el.inner_text()) if await vote_el.count() > 0 else 0
    comment_el = item.locator('button:has-text("评论")').first
    comment_count = parse_comment_count(await comment_el.inner_text()) if await comment_el.count() > 0 else 0
    return {
        "author": author.strip(),
        "content_html": content_html,
        "content_text": strip_tags(content_html),
        "vote_count": vote_count,
        "comment_count": comment_count,
        "preview": html_to_text_snippet(content_html, limit=240),
    }


async def zhihu_extract_all_answers(page: Any, answer_limit: int) -> list[dict[str, Any]]:
    answers: list[dict[str, Any]] = []
    try:
        await page.wait_for_selector(".List-item", timeout=10000)
    except Exception:
        return answers
    items = await page.locator(".List-item").all()
    for item in items[:answer_limit]:
        answer = await zhihu_extract_answer_content(item)
        if answer.get("content_text"):
            answers.append(answer)
    return answers


async def zhihu_extract_answer_page(page: Any) -> dict[str, Any]:
    author_el = page.locator(".AuthorInfo-name").first
    author = await author_el.inner_text() if await author_el.count() > 0 else ""
    question_title_el = page.locator("h1.QuestionHeader-title").first
    question_title = await question_title_el.inner_text() if await question_title_el.count() > 0 else ""
    content_el = page.locator(".RichContent-inner").first
    content_html = await content_el.inner_html() if await content_el.count() > 0 else ""
    vote_el = page.locator(".VoteButton--up").first
    vote_count = parse_vote_count(await vote_el.inner_text()) if await vote_el.count() > 0 else 0
    comment_el = page.locator('button:has-text("评论")').first
    comment_count = parse_comment_count(await comment_el.inner_text()) if await comment_el.count() > 0 else 0
    return {
        "question_title": question_title.strip(),
        "author": author.strip(),
        "content_html": content_html,
        "content_text": strip_tags(content_html),
        "vote_count": vote_count,
        "comment_count": comment_count,
        "preview": html_to_text_snippet(content_html, limit=320),
    }


async def zhihu_extract_article(page: Any) -> dict[str, Any]:
    title_el = page.locator("h1.Post-Title, .Post-Title").first
    title = await title_el.inner_text() if await title_el.count() > 0 else ""
    author_el = page.locator(".AuthorInfo-name").first
    author = await author_el.inner_text() if await author_el.count() > 0 else ""
    content_el = page.locator(".Post-RichText").first
    content_html = await content_el.inner_html() if await content_el.count() > 0 else ""
    vote_el = page.locator(".VoteButton--up").first
    vote_count = parse_vote_count(await vote_el.inner_text()) if await vote_el.count() > 0 else 0
    comment_el = page.locator('button:has-text("评论")').first
    comment_count = parse_comment_count(await comment_el.inner_text()) if await comment_el.count() > 0 else 0
    return {
        "title": title.strip(),
        "author": author.strip(),
        "content_html": content_html,
        "content_text": strip_tags(content_html),
        "vote_count": vote_count,
        "comment_count": comment_count,
        "preview": html_to_text_snippet(content_html, limit=320),
    }


async def run_zhihu_detail(
    url: str,
    state: str | None,
    headed: bool,
    timeout: int,
    wait_ms: int,
    answer_limit: int,
    output_dir: Path,
) -> dict[str, Any]:
    from playwright.async_api import async_playwright

    parsed = parse_zhihu_url(url)
    if not parsed.get("type"):
        raise RuntimeError(f"无法解析知乎链接: {url}")

    headers = HEADER_PROFILES["desktop"]
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=not headed,
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
        if state:
            context_kwargs["storage_state"] = state
        context = await browser.new_context(**context_kwargs)
        page = await context.new_page()
        await apply_stealth_if_available(page)
        await page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)
        await page.wait_for_timeout(wait_ms)

        kind = parsed["type"]
        if kind == "question":
            question = await zhihu_extract_question_detail(page)
            answers = await zhihu_extract_all_answers(page, answer_limit)
            detail = {
                "type": "question",
                "title": question.get("title", ""),
                "detail_text": question.get("detail_text", ""),
                "detail_html": question.get("detail_html", ""),
                "answer_count": question.get("answer_count", 0),
                "answers": answers,
            }
        elif kind == "answer":
            answer = await zhihu_extract_answer_page(page)
            detail = {
                "type": "answer",
                "question_title": answer.get("question_title", ""),
                "author": answer.get("author", ""),
                "content_text": answer.get("content_text", ""),
                "content_html": answer.get("content_html", ""),
                "vote_count": answer.get("vote_count", 0),
                "comment_count": answer.get("comment_count", 0),
            }
        else:
            article = await zhihu_extract_article(page)
            detail = {
                "type": "article",
                "title": article.get("title", ""),
                "author": article.get("author", ""),
                "content_text": article.get("content_text", ""),
                "content_html": article.get("content_html", ""),
                "vote_count": article.get("vote_count", 0),
                "comment_count": article.get("comment_count", 0),
            }

        screenshot = output_dir / "detail.png"
        html_file = output_dir / "detail.html"
        await page.screenshot(path=str(screenshot), full_page=True)
        html_file.write_text(await page.content(), encoding="utf-8")
        await context.close()
        await browser.close()

    return detail

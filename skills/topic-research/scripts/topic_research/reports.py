from __future__ import annotations


def render_research_markdown(topic: str, report: dict[str, object]) -> str:
    lines = [f"# Research Pack: {topic}", ""]
    lines.append("## Source Inventory")
    lines.append("")
    for idx, source in enumerate(report.get("sources", []), 1):  # type: ignore[arg-type]
        source = source  # type: ignore[assignment]
        lines.append(f"### {idx}. {source.get('title', 'Untitled')}")
        lines.append(f"- backend: {source.get('backend', '')}")
        lines.append(f"- url: {source.get('url', '')}")
        if source.get("author"):
            lines.append(f"- author: {source.get('author')}")
        if source.get("pub_date"):
            lines.append(f"- pub_date: {source.get('pub_date')}")
        if source.get("snippet"):
            lines.append(f"- snippet: {source.get('snippet')}")
        if source.get("body_preview"):
            lines.append("")
            lines.append(source.get("body_preview"))
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_zhihu_detail_markdown(url: str, detail: dict[str, object]) -> str:
    kind = detail.get("type", "")
    lines = [f"# Zhihu Detail: {detail.get('title') or detail.get('question_title') or url}", ""]
    lines.append(f"- type: {kind}")
    lines.append(f"- url: {url}")
    if detail.get("author"):
        lines.append(f"- author: {detail.get('author')}")
    if detail.get("vote_count"):
        lines.append(f"- vote_count: {detail.get('vote_count')}")
    if detail.get("comment_count"):
        lines.append(f"- comment_count: {detail.get('comment_count')}")
    if detail.get("answer_count"):
        lines.append(f"- answer_count: {detail.get('answer_count')}")
    lines.append("")

    if detail.get("detail_text"):
        lines.append("## Question Detail")
        lines.append("")
        lines.append(str(detail["detail_text"]))
        lines.append("")

    if detail.get("content_text"):
        lines.append("## Content")
        lines.append("")
        lines.append(str(detail["content_text"]))
        lines.append("")

    answers = detail.get("answers", []) or []
    if answers:
        lines.append("## Answers")
        lines.append("")
        for idx, answer in enumerate(answers, 1):
            lines.append(f"### {idx}. {answer.get('author', '')}")
            lines.append(f"- vote_count: {answer.get('vote_count', 0)}")
            lines.append(f"- comment_count: {answer.get('comment_count', 0)}")
            lines.append("")
            lines.append(answer.get("content_text", ""))
            lines.append("")

    return "\n".join(lines).strip() + "\n"

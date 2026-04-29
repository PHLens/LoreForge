"""CLI entrypoint for the topic-research skill."""

from __future__ import annotations

import argparse
import asyncio

from topic_research.commands import (
    detail_command,
    extract_command,
    login_command,
    probe_command,
    research_command,
    search_command,
)
from topic_research.config import DEFAULT_OUTPUT_ROOT, HEADER_PROFILES, ZHIHU_SEARCH_TYPES


def build_parser() -> argparse.ArgumentParser:
    default_output_help = f"输出目录。默认写到 {DEFAULT_OUTPUT_ROOT}/<timestamp>/"
    parser = argparse.ArgumentParser(
        description="Research topics across Chinese and general web sources."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    probe = subparsers.add_parser("probe", help="运行 HTTP + 浏览器探测")
    probe.add_argument("url", help="目标 URL")
    probe.add_argument(
        "--profile",
        choices=sorted(HEADER_PROFILES),
        default="desktop",
        help="请求头和浏览器 profile",
    )
    probe.add_argument("--state", help="可选的 storage state JSON 文件")
    probe.add_argument("--headed", action="store_true", help="使用有头浏览器")
    probe.add_argument("--requests-only", action="store_true", help="仅运行 requests 探测")
    probe.add_argument("--timeout", type=int, default=30, help="超时秒数")
    probe.add_argument("--wait-ms", type=int, default=3000, help="页面打开后的额外等待时间（毫秒）")
    probe.add_argument(
        "--capture-pattern",
        action="append",
        default=[],
        help="仅保存匹配该正则的响应，可重复传入",
    )
    probe.add_argument("--output-dir", help=default_output_help)

    search = subparsers.add_parser("search", help="做 top-k 搜索并返回候选链接")
    search.add_argument("query", help="搜索关键词")
    search.add_argument("--site", help="可选站点过滤，例如 zhihu.com")
    search.add_argument("--limit", type=int, default=3, help="返回结果数量")
    search.add_argument(
        "--source",
        choices=["auto", "zhihu", "wechat", "generic"],
        default="auto",
        help="搜索后端：自动分发，或显式指定",
    )
    search.add_argument(
        "--zhihu-type",
        choices=sorted(ZHIHU_SEARCH_TYPES),
        default="all",
        help="Zhihu 搜索类型过滤，仅在 Zhihu native 搜索时生效",
    )
    search.add_argument("--region", default="wt-wt", help="generic 搜索后端的区域参数")
    search.add_argument("--output", help="可选 JSON 输出文件")

    research = subparsers.add_parser("research", help="围绕一个主题收集多来源参考材料并生成 research pack")
    research.add_argument("topic", help="调研主题")
    research.add_argument(
        "--source",
        choices=["auto", "zhihu", "wechat", "generic"],
        default="auto",
        help="搜索后端：自动分发，或显式指定",
    )
    research.add_argument(
        "--zhihu-type",
        choices=sorted(ZHIHU_SEARCH_TYPES),
        default="all",
        help="Zhihu 搜索类型过滤，仅在 Zhihu native 搜索时生效",
    )
    research.add_argument("--site", help="generic 搜索时可选站点过滤")
    research.add_argument("--limit", type=int, default=3, help="每个搜索源取前 N 条")
    research.add_argument("--min-refs", type=int, default=3, help="最少保留的参考数")
    research.add_argument("--max-refs", type=int, default=5, help="最多处理的参考数")
    research.add_argument(
        "--profile",
        choices=["auto", *sorted(HEADER_PROFILES)],
        default="auto",
        help="运行 extract 时使用的 profile；auto 会按站点推断",
    )
    research.add_argument("--state", help="可选的 storage state JSON 文件")
    research.add_argument("--headed", action="store_true", help="使用有头浏览器")
    research.add_argument("--timeout", type=int, default=30, help="超时秒数")
    research.add_argument("--wait-ms", type=int, default=3000, help="页面打开后的额外等待时间（毫秒）")
    research.add_argument("--region", default="wt-wt", help="generic 搜索后端的区域参数")
    research.add_argument("--output-dir", help=default_output_help)

    detail = subparsers.add_parser("detail", help="展开 Zhihu 对象细节，支持问题页多回答")
    detail.add_argument("url", help="Zhihu 问题 / 回答 / 文章 URL")
    detail.add_argument("--state", help="可选的 storage state JSON 文件")
    detail.add_argument("--headed", action="store_true", help="使用有头浏览器")
    detail.add_argument("--timeout", type=int, default=30, help="超时秒数")
    detail.add_argument("--wait-ms", type=int, default=3000, help="页面打开后的额外等待时间（毫秒）")
    detail.add_argument("--answer-limit", type=int, default=5, help="问题页展开的回答数量")
    detail.add_argument("--output-dir", help=default_output_help)

    extract = subparsers.add_parser("extract", help="用浏览器提取可访问页面的正文")
    extract.add_argument("url", help="目标 URL")
    extract.add_argument(
        "--profile",
        choices=sorted(HEADER_PROFILES),
        default="desktop",
        help="请求头和浏览器 profile",
    )
    extract.add_argument("--state", help="可选的 storage state JSON 文件")
    extract.add_argument("--headed", action="store_true", help="使用有头浏览器")
    extract.add_argument("--timeout", type=int, default=30, help="超时秒数")
    extract.add_argument("--wait-ms", type=int, default=3000, help="页面打开后的额外等待时间（毫秒）")
    extract.add_argument("--output-dir", help=default_output_help)

    login = subparsers.add_parser("login", help="人工登录/验证后保存浏览器态")
    login.add_argument("url", help="打开的起始 URL")
    login.add_argument("--state", default="auth/session.json", help="保存 storage state 的路径")
    login.add_argument(
        "--profile",
        choices=sorted(HEADER_PROFILES),
        default="desktop",
        help="浏览器 profile",
    )
    login.add_argument("--wait-ms", type=int, default=1500, help="初始打开页面后的等待时间（毫秒）")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "probe":
        asyncio.run(probe_command(args))
    elif args.command == "search":
        search_command(args)
    elif args.command == "research":
        asyncio.run(research_command(args))
    elif args.command == "detail":
        asyncio.run(detail_command(args))
    elif args.command == "extract":
        asyncio.run(extract_command(args))
    elif args.command == "login":
        asyncio.run(login_command(args))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

from __future__ import annotations

import os
from pathlib import Path


HEADER_PROFILES: dict[str, dict[str, str]] = {
    "desktop": {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    },
    "mobile_safari": {
        "User-Agent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 "
            "Mobile/15E148 Safari/604.1"
        ),
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    },
    "wechat_android": {
        "User-Agent": (
            "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36 "
            "MicroMessenger/8.0.54.2800(0x28003639) WeChat/arm64 Weixin "
            "NetType/WIFI Language/zh_CN ABI/arm64"
        ),
        "Referer": "https://weixin.qq.com/",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    },
    "wechat_ios": {
        "User-Agent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 "
            "MicroMessenger/8.0.54(0x1800362c) NetType/WIFI Language/zh_CN"
        ),
        "Referer": "https://weixin.qq.com/",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    },
}

SCRIPT_DIR = Path(__file__).resolve().parent.parent
SKILL_ROOT = SCRIPT_DIR.parent
DEFAULT_OUTPUT_ROOT = Path(
    os.environ.get("TOPIC_RESEARCH_OUTPUT_ROOT", "/tmp/topic-research")
).expanduser()
AUTH_DIR = SCRIPT_DIR / "auth"
ZHIHU_AUTH_STATE = AUTH_DIR / "zhihu.json"
ZHIHU_SEARCH_API_URL = "https://www.zhihu.com/api/v4/search_v3"
ZHIHU_SEARCH_TYPES = {"all", "question", "answer", "article", "people"}

CAPTCHA_PATTERNS = [
    r"captcha",
    r"verify",
    r"verification required",
    r"验证码",
    r"人机验证",
    r"安全验证",
    r"完成验证后即可继续访问",
    r"环境异常",
    r"tcaptcha",
    r"tjcaptcha",
    r"turnstile",
    r"cf[_-]?clearance",
    r"g-recaptcha",
    r"hcaptcha",
    r"geetest",
    r"wappoc_appmsgcaptcha",
]

LOGIN_PATTERNS = [
    r"登录",
    r"sign in",
    r"log in",
    r"扫码登录",
    r"继续访问请登录",
]

BLOCK_PATTERNS = [
    r"access denied",
    r"forbidden",
    r"too many requests",
    r"rate limit",
    r"robot",
    r"unusual traffic",
    r"risk",
    r"风控",
    r"访问受限",
]

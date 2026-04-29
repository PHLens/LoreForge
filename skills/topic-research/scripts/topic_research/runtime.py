from __future__ import annotations

from urllib.parse import urlparse

from .config import ZHIHU_AUTH_STATE


def infer_runtime_profile(target: str, source: str, profile: str) -> str:
    if profile != "auto":
        return profile
    target = target.lower()
    if source == "wechat" or "mp.weixin.qq.com" in target or "weixin.sogou.com" in target:
        return "wechat_android"
    return "desktop"


def resolve_runtime_state(target: str, source: str, state: str | None) -> str | None:
    if state:
        return state
    target = target.lower()
    if source == "zhihu" or "zhihu.com" in target or "zhihu.com" in urlparse(target).netloc:
        if ZHIHU_AUTH_STATE.exists():
            return str(ZHIHU_AUTH_STATE)
    return None

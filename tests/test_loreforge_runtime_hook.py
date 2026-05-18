#!/usr/bin/env python3
"""Validate LoreForge runtime hook behavior."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HOOKS_PATH = REPO_ROOT / "hooks.json"
HOOK_SCRIPT = REPO_ROOT / "scripts" / "loreforge-prompt-hook.sh"


def run_hook(payload: object | str) -> subprocess.CompletedProcess[str]:
    if isinstance(payload, str):
        input_text = payload
    else:
        input_text = json.dumps(payload)
    return subprocess.run(
        ["bash", str(HOOK_SCRIPT)],
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )


def assert_hooks_contract() -> None:
    hooks = json.loads(HOOKS_PATH.read_text(encoding="utf-8"))
    user_prompt = hooks["hooks"]["UserPromptSubmit"]
    assert user_prompt[0]["hooks"][0]["command"] == "./scripts/loreforge-prompt-hook.sh"

    session_start = hooks["hooks"]["SessionStart"]
    assert session_start[0]["matcher"] == "startup|resume|clear|compact"
    assert session_start[0]["hooks"][0]["command"] == "./scripts/loreforge-prompt-hook.sh"


def assert_prompt_detection() -> None:
    session_start = run_hook({"hook_event_name": "SessionStart", "cwd": "/tmp/wiki"})
    assert session_start.returncode == 0
    assert "loreforge-runtime-hook" in session_start.stdout

    positive = run_hook({"prompt": "capture and ingest this arxiv paper into wiki"})
    assert positive.returncode == 0
    assert "loreforge-runtime-hook" in positive.stdout
    parsed = json.loads(positive.stdout)
    ctx = parsed["hookSpecificOutput"]["additionalContext"]
    assert "Use the public `loreforge` entrypoint" in ctx
    assert "loreforge-paper" in ctx
    assert "loreforge-domain" in ctx

    negative = run_hook({"prompt": "please rename this local variable in app.py"})
    assert negative.returncode == 0
    assert negative.stdout == ""


def main() -> int:
    assert_hooks_contract()
    assert_prompt_detection()
    print("LoreForge runtime hook tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

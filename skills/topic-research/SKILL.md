---
name: topic-research
description: Research a topic across Chinese and general web sources, gather at least 3 references when possible, extract accessible content, and prepare a source-backed research pack for synthesis. Also use when the user sends one or more links and wants article details, structured content extraction, Zhihu answer/question expansion, or a source-grounded summary from the linked content.
---

# Topic Research

Use this skill to gather source material for a topic, reuse human-provided browser state when needed, and prepare a source-backed research pack before writing a synthesized report.

When this skill is used with `loreforge-wiki`, treat its outputs as capture
inputs. Durable raw source records and attachments belong under the wiki-level
`Shared/SourceRecords/` and `Shared/Raw/` directories. Domain-specific source
lenses belong under the selected domain's `Sources/` directory. Do not leave
final wiki notes pointing at `/tmp/topic-research/...`.

## Environment Setup

The runtime entrypoint is `scripts/main.py`. All commands below assume you start from the skill root and then enter `scripts/`.

Recommended bootstrap on a fresh machine:

```bash
cd scripts
uv sync
./.venv/bin/python -m playwright install chromium
```

If `uv` is not on `PATH` but `scripts/.venv` already exists, reuse the local environment directly:

```bash
cd scripts
./.venv/bin/python -m playwright install chromium
./.venv/bin/python main.py --help
```

If you prefer activating the environment first:

```bash
cd scripts
source .venv/bin/activate
python -m playwright install chromium
python main.py --help
```

Operational rule:

- Prefer `uv sync` to create or refresh the environment.
- Prefer `./.venv/bin/python main.py ...` when `uv` is unavailable in the current shell.
- Browser-based commands such as `probe`, `extract`, `detail`, and `login` require Playwright Chromium to be installed once in that environment.
- Default artifacts no longer live under the skill directory. Unless `--output-dir` is specified, outputs go to `/tmp/topic-research/<timestamp>/`.
- Local browser state may live in `scripts/auth/`, for example
  `scripts/auth/zhihu.json`. Auth JSON files can contain reusable cookies and
  tokens; keep them machine-local and out of git.

## Quick Start

Install dependencies once:

```bash
cd scripts && uv sync && ./.venv/bin/python -m playwright install chromium
```

When the goal is research rather than a single page, use the research pack workflow:

```bash
cd scripts && ./.venv/bin/python main.py research "CUDA" --min-refs 3
```

Run a first-pass probe:

```bash
cd scripts && ./.venv/bin/python main.py probe "https://example.com"
```

Search top-k candidate URLs before probing when you only have a topic or need alternate sources:

```bash
cd scripts && ./.venv/bin/python main.py search "CUDA" --site zhihu.com --limit 5
```

The search backend is source-aware:

- `zhihu.com` or `--source zhihu`: use the skill's integrated Zhihu-native search path
- `mp.weixin.qq.com` or `--source wechat`: use WeChat-specific article search via Sogou Weixin
- anything else: fall back to the generic search-engine path

When direct access is already suspicious on mobile or in-app traffic, try a profile closer to the real client:

```bash
cd scripts && ./.venv/bin/python main.py probe "https://mp.weixin.qq.com/..." --profile wechat_android
```

If the site needs a human login or challenge completion, open a headed browser, complete the interaction manually, and save state:

```bash
cd scripts && ./.venv/bin/python main.py login "https://example.com/login" --state auth/example.json
cd scripts && ./.venv/bin/python main.py probe "https://example.com/protected-page" --state auth/example.json
```

For Zhihu, reuse a local state file when available:

```bash
cd scripts && ./.venv/bin/python main.py detail "https://zhuanlan.zhihu.com/p/577412348" --state auth/zhihu.json
```

When the browser path can already access the page, extract structured content:

```bash
cd scripts && ./.venv/bin/python main.py extract "https://mp.weixin.qq.com/..." --profile wechat_android
```

When you already picked a Zhihu URL and want richer structure than generic extraction, use `detail`:

```bash
cd scripts && ./.venv/bin/python main.py detail "https://www.zhihu.com/question/123/answer/456" --answer-limit 5
```

## Workflow

1. Start with `research` when the user asks for a topic investigation, expects at least 3 references, or wants a synthesized report grounded in multiple sources.
2. For direct-link requests, default to `detail` or `extract` before summarizing, so the summary is grounded in fetched content rather than title-only inference.
3. Use `search` when you need candidate URLs, alternate mirrors, or a top-k shortlist for a topic/site.
   Prefer native/source-specific search when available instead of forcing every site through the same generic engine.
4. Run `probe` and inspect the generated `summary.json`, `page.html`, `page.png`, and `matched-responses.json`.
5. Classify the outcome:
   - `content_accessible`: extract content directly, or prefer structured API responses if the probe captured them.
   - `login_required`: save browser state with `login`, then rerun `probe` with `--state`.
   - `captcha_or_challenge`: switch to a headed browser and let a human complete the challenge, or ask for an alternate source.
   - `blocked_http`: assume IP/rate/WAF/network factors until proven otherwise.
   - `unclear`: inspect the saved artifacts and adjust profile, wait time, or capture patterns.
6. Prefer network responses over DOM extraction when structured JSON is available.
7. Fall back to saved HTML only when network capture is insufficient.
8. Stop claiming success once the site requires interactive proof, backend token validation, or opaque server-side scoring.
9. Once `browser_probe` is `content_accessible`, use `extract` to dump structured metadata and正文 artifacts.
10. After `research`, read the generated `research-report.json` and `research-pack.md`, then synthesize a concise report for the user instead of dumping raw sources.
11. For Zhihu question pages where multiple answers matter, use `detail` to expand the question plus top answers instead of relying only on generic `extract`.

## What The Integrated Workflow Reuses

- Persist browser state to disk and reuse it across runs.
- Use Playwright request/response events to observe what the page actually loads.
- Prefer API/network data over brittle DOM scraping.
- Keep DOM parsing as a fallback, not the primary path.
- Allow human-assisted login or verification when the barrier is interactive.

## What Does Not Transfer Universally

- Endpoint shapes, auth cookies, GraphQL schemas, and selectors are site-specific.
- CAPTCHA vendors such as Tencent Captcha, Turnstile, reCAPTCHA, and GeeTest typically depend on interactive proof plus backend validation.
- Bot decisions can depend on IP reputation, TLS and browser fingerprints, timing, historical session signals, or WAF rules.
- A generic skill can detect and classify these barriers, and can often recover content after a human provides valid browser state, but it should not promise an automatic bypass.

## Recommended Operating Rules

- Save auth state outside version control; it can contain reusable cookies or tokens.
- Use headed mode for manual verification and headless mode for repeatable probes.
- Keep the investigation vendor-neutral first. Add site-specific code only after the probe reveals a stable path worth automating.
- If the user only needs the content, prefer alternate accessible sources over escalating the automation complexity.
- For theme research, aim for at least 3 references and prefer multiple source families instead of 3 links from the same site.
- Prefer `--zhihu-type` when you want cleaner Zhihu candidate sets, and `detail` when you want deeper question-page structure.

## Resources

- Read `references/workflow.md` for the decision tree, limits, and official-Docs-backed rationale.
- Use `scripts/main.py` for research, top-k search, Zhihu detail expansion, probing, browser-state capture, and content extraction.

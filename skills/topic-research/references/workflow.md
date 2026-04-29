# Topic Research Reference

## Purpose

This skill is a reusable topic-research workflow for collecting source material from sites that may involve login walls, anti-bot middleware, captcha, or other risk-control flows.

Its goal is not "universal bypass". Its goal is:

1. Identify what kind of gate exists.
2. Capture enough evidence to pick the next viable path.
3. Reuse human-authenticated browser state when that is allowed and effective.
4. Stop escalating once the problem is clearly backend validation or server-side scoring.

## Why The Source-Aware Flow Works

The integrated workflow succeeds because it combines four specific ideas:

1. Persist authenticated browser state to disk.
2. Reuse that state in Playwright.
3. Observe network responses instead of scraping blindly.
4. Fall back to DOM extraction only when the network path is insufficient.

Those ideas transfer well.

What does not transfer well is everything site-specific:

- API endpoints
- request signatures
- GraphQL operations
- DOM selectors
- cookie semantics
- challenge vendor integration

## Decision Tree

### 1. Probe the URL

Run the generic probe first. It produces:

- `summary.json`: classification, final URL, title, profile, recommendations
- `page.html`: raw saved HTML
- `page.png`: screenshot for visual inspection
- `matched-responses.json`: captured network responses that matched the configured patterns

### 2. Interpret the classification

#### `content_accessible`

The page is reachable. Next actions:

- extract directly from HTML, or
- prefer captured JSON/API responses if they contain cleaner data.

#### `login_required`

The page likely needs an authenticated session. Next actions:

- open a headed browser,
- let a human log in,
- save `storage_state`,
- rerun the probe with `--state`.

#### `captcha_or_challenge`

The page shows an interactive challenge or verification flow. Next actions:

- use headed mode and let a human solve it, or
- request exported content / screenshots / alternate sources.

Do not claim a silent workaround unless repeated probes prove one exists.

#### `blocked_http`

The page returned 401, 403, 429, or similar block behavior. Next actions:

- treat it as network/WAF/rate-limit/IP policy until proven otherwise,
- reduce request volume,
- reuse a real browser session if appropriate,
- or switch to alternate sources.

#### `unclear`

The page did not cleanly match the known cases. Next actions:

- inspect saved HTML and screenshot,
- widen the wait time,
- capture more response patterns,
- test another profile.

## Vendor and Middleware Limits

### Tencent Captcha

Tencent's captcha product is explicitly a behavior-based verification system with device and behavior checks. That means a generic client-side script should assume interactive proof and server-side validation are part of the flow, not optional extras.

Official reference:
- <https://cloud.tencent.com/product/captcha>
- <https://cloud.tencent.com/document/product/1110/36841>

### Cloudflare Turnstile and Challenges

Turnstile issues tokens that the site must validate server-side, and some flows also rely on clearance cookies or Cloudflare-managed challenge decisions. This means "load the widget" is not enough; a generic skill can detect the challenge and preserve browser state after a human passes it, but not replace the site's backend validation.

Official reference:
- <https://developers.cloudflare.com/turnstile/get-started/server-side-validation/>
- <https://developers.cloudflare.com/cloudflare-challenges/challenge-types/turnstile/>
- <https://developers.cloudflare.com/bots/reference/javascript-detections/>

## Playwright Techniques That Generalize

These are the officially documented capabilities this skill relies on:

- Save and reload browser auth state with `storageState`.
- Listen to `request`, `response`, and `requestfailed` events.
- Use isolated browser contexts so each investigation is reproducible.

Official reference:
- <https://playwright.dev/docs/auth>
- <https://playwright.dev/docs/network>
- <https://playwright.dev/docs/events>
- <https://playwright.dev/docs/api/class-browsercontext>

## Practical Heuristics

- If final URL changes to a vendor challenge endpoint, treat that as a strong classification signal.
- If HTML contains `captcha`, `verify`, `TCaptcha`, `turnstile`, `g-recaptcha`, `geetest`, or explicit risk-control wording, classify as `captcha_or_challenge`.
- If HTML contains obvious sign-in prompts and no content signal, classify as `login_required`.
- If the browser page is reachable but the content is empty while API responses contain the real data, automate against the captured response pattern instead of the rendered DOM.
- If every profile still reaches a challenge page, stop pretending the issue is just headers.

## Output Expectations

A good run should leave behind enough evidence that another agent can continue without repeating the whole investigation:

- exact URL probed
- header profile used
- whether a saved state file was used
- final URL
- document status and title
- saved screenshot and HTML
- challenge indicators
- clear recommendation for the next step

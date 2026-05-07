# Card and Atlas Boundary

## Core Rule

Cards are shared knowledge objects. Atlas/MOC pages are project or view objects.

Use Cards to preserve reusable facts, definitions, mechanisms, comparisons,
patterns, tradeoffs, corrections, and source-backed viewpoint changes. Use
Atlas/MOC pages to connect Cards into a current research question, proposal,
project frame, argument, evaluation plan, or open decision list.

## Use Cards When

- The content can be reused by unrelated projects or views.
- A concept, method, mechanism, pattern, tradeoff, comparison, or decision
  framework is durable enough to cite later.
- The update changes a source-backed claim, adds provenance, fixes an error, or
  clarifies the stable viewpoint.
- The question is simply "what is it" or "what is it useful for" in a reusable
  sense.

Do not put project-specific commentary, proposal phrasing, personal comments, or
"how this helps my current paper" text in Cards unless that text is itself a
durable domain claim. A Card can explain general usefulness; it should not try
to become a live discussion thread.

## Use Atlas/MOC When

- The page is a proposal view, project frame, or question-driven synthesis.
- The page asks for an explicit discussion, interpretation, or stance about a
  particular problem.
- The value comes from relating multiple Cards, not from defining one reusable
  concept.
- The page needs the current argument, interpretation, evaluation questions,
  open decisions, or research-specific comments.

Atlas pages can cite Cards and raw sources. They are the right place to say why
a Card matters for a specific proposal.

## Default Card Template

Keep Card templates close to the concise Obsidian concept shape:

```markdown
---
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: concept
tags: []
confidence: medium
status: active
contested: false
contradictions: []
---

related:: [[related-page]]

# Page Title

One-sentence lead.

## Why

## What is

[^1]: [[Shared/Raw/source-id/manifest.md]]
```

Add optional sections only when needed, such as `## Mechanism`, `## Example`,
`## Limits`, or `## Open Questions`. Do not reserve a mandatory proposal section
inside Cards.

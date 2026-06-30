---
name: plan-docomposer
description: Internal LoreForge workflow for decomposing long-term personal, research, study, career, or project goals into concrete weekly and daily Obsidian note plans. Use through the LoreForge wiki role when the user asks to make a plan from a big goal, break a proposal or milestone into weekly/daily work, schedule medium-term progress, write a weekly plan, project tasks into daily notes, or review and re-plan from daily/weekly notes.
user-invocable: false
version: 0.1.0
---

# Plan Docomposer

Turn a large goal into executable weekly and daily note content inside a
LoreForge wiki.

This is an internal LoreForge planning workflow for the wiki role. It plans
from outcomes backward, then writes only the near-term slices that belong in
`Calendar/weeklynotes/` and `Calendar/dailynotes/`. It is not a generic
writeback router, task board, memory system, or source ingest workflow.

## Core Boundary

- Use daily notes for today's concrete actions, quick capture, and small TODOs.
- Use weekly notes for focus, outcomes, work blocks, risks, decisions, and review.
- Use topic rollups only when the plan needs a durable project state page.
- Link to wiki pages, repos, tasks, or threads instead of copying large artifacts.
- Keep private/personal plans out of public domains or shared memory unless the user explicitly asks.
- Do not put agent behavior rules or reusable preferences here; route those through memory governance.
- Do not expose this as a global role skill; call it through `loreforge` after wiki resolution.

## Workflow

1. **Intake the goal**
   - Identify objective, deadline or horizon, current state, constraints, available time, source artifacts, and privacy level.
   - If a blocking input is missing, ask one concise question. Otherwise make a reasonable assumption and state it.

2. **Backplan milestones**
   - Work backward from the deadline or review date.
   - Define 2-6 milestones with concrete deliverables.
   - Include evidence of completion for each milestone.

3. **Allocate the current week**
   - Pick the few milestones or work blocks that fit this week.
   - Keep the weekly plan small enough to review: focus, outcomes, 3-5 work blocks, risks, decisions, review criteria.
   - Prefer deliverables over vague activity labels.

4. **Project into daily notes**
   - Write only the next 1-3 days by default.
   - Put 1-3 actionable TODOs per day.
   - Each TODO should include a plan tag such as `[plan/stateful-llm]`, a verb, an artifact, and a done condition.

5. **Review and re-plan**
   - At weekly review time, compare outcomes against completed daily notes.
   - Carry forward unfinished work deliberately; do not blindly duplicate stale TODOs.
   - Update risks and next week's focus.

## Obsidian Defaults

When working in the current LoreForge wiki, use these defaults unless the user
or config says otherwise:

- daily folder: `Calendar/dailynotes`
- daily template: `Extras/Templates/diary`
- weekly folder: `Calendar/weeklynotes`
- weekly naming format: `gggg-[W]ww`, such as `2026-W21`
- weekly template path: `Extras/Templates/weekly`

If weekly folders or templates are missing and the user asked you to implement
the skill's note support, run the LoreForge wiki initialization/repair flow so
the wiki instance owns `Calendar/weeklynotes/` and
`Extras/Templates/weekly.md`. Preserve an existing wiki template unless the
user explicitly asks to rewrite it. Do not keep note templates bundled inside
this skill. If the user only asked for a plan draft, output the Markdown blocks
without editing files.

## Writing Notes

Before editing notes:

- Resolve the wiki root through `loreforge-config`.
- Inspect the target note if it exists.
- Preserve existing personal content.
- Insert under the matching heading; create the heading only if missing.
- Avoid rewriting unrelated sections.
- For daily notes, use `## TODO` for executable tasks and `## Memos` for context.
- For weekly notes, adapt to the wiki-owned `Extras/Templates/weekly.md`
  headings. If a section is missing, prefer adding a small `This Week`,
  `Daily Notes`, or `Review` section over rewriting the template.
- Treat daily-note links as navigation. Put concrete day-level actions in the
  linked daily note `## TODO` sections instead of duplicating them in the weekly
  note.

## Writing Style

- Write note content for the human who will read and edit it later.
- Daily notes are execution surfaces: use short factual memos and concrete
  TODOs only.
- Do not write agent reasoning, process narration, detailed explanations, or
  "why I chose this structure" text into daily notes.
- Keep daily `## Memos` to brief context, usually one line. Put rationale,
  tradeoffs, risks, and review criteria in the weekly note or linked project
  page when they are useful.
- TODOs should be imperative and artifact-oriented: verb, object, done
  condition. Avoid abstract tasks such as "research X" without an output.
- Do not mention the skill, routing, validator behavior, or internal planning
  mechanics inside the notes.

## Output Contract

When drafting in chat, return:

- goal assumptions
- milestone backplan
- weekly note block
- daily note TODO blocks
- review cadence

When editing files, report:

- files changed
- dates covered
- remaining assumptions
- sync result
- any reminders or follow-up checks created

## Quality Bar

- Plans should be executable by a tired human.
- Prefer "run X and record Y in Z" over "research X".
- Keep work blocks independent where possible.
- Keep daily actions small enough to finish in one sitting.
- Put uncertainty into risks or questions, not into vague tasks.
- Never generate a long calendar full of fragile future TODOs when a weekly review loop would be more robust.

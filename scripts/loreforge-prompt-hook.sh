#!/usr/bin/env bash
# Runtime hook for keeping the LoreForge public entrypoint in context.
# Reads hook JSON or plain prompt text on stdin and emits a compact reminder
# only when the user prompt looks like LoreForge work.

set -euo pipefail

INPUT="$(cat || true)"

if command -v jq >/dev/null 2>&1 && [ -n "$INPUT" ]; then
  EVENT="$(printf '%s' "$INPUT" | jq -r '
    .hook_event_name? // .hookEventName? // .event? // .eventName? // empty
  ' 2>/dev/null || true)"
  PROMPT="$(printf '%s' "$INPUT" | jq -r '
    .prompt? // .user_prompt? // .userPrompt? // .message? // .input? // .text? // empty
  ' 2>/dev/null || true)"
else
  EVENT=""
  PROMPT=""
fi

if [ -z "$PROMPT" ]; then
  PROMPT="$INPUT"
fi

if [ "$EVENT" != "SessionStart" ] && ! printf '%s' "$PROMPT" | grep -Eiq \
  '(^|[^[:alnum:]_-])(loreforge|#wiki|wiki|capture|ingest|sync|raw package|Shared/Raw|Domains/|SCHEMA\.md|index\.md|log\.md|arxiv|doi|paper|pdf|preprint|论文|文献|抓取|同步|知识库)([^[:alnum:]_-]|$)'; then
  exit 0
fi

CONTEXT='[loreforge-runtime-hook] This looks like LoreForge work. Use the public `loreforge` entrypoint before acting. Re-anchor on operation, wiki root, primary domain, secondary write candidates, and write policy. Delegate paper-like sources to `loreforge-paper`, raw capture to `loreforge-capture`, durable domain writes to `loreforge-domain`, checks to `loreforge-check`, and sync/config to `loreforge-config`. Before final report verify raw package handling, domain boundaries, index/log updates, validation, sync, and unresolved limits. Keep this as an internal routing reminder; show a routing plan only when ambiguity affects a write.'
OUTPUT_EVENT="${EVENT:-UserPromptSubmit}"

if command -v jq >/dev/null 2>&1; then
  jq -n --arg event "$OUTPUT_EVENT" --arg ctx "$CONTEXT" '{
    hookSpecificOutput: {
      hookEventName: $event,
      additionalContext: $ctx
    }
  }'
else
  printf '%s\n' "$CONTEXT"
fi

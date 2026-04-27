# Philosophy

LoreForge is a framework for LLM-wiki style professional knowledge bases.

It is not agent memory.

The goal is to reduce repeated raw search and summarization by compiling useful source material into durable, queryable, human-readable knowledge.

## Separation

```text
pamem
  local agent/workspace memory
  preferences
  current task state
  agent-local experience

LoreForge wiki instance
  professional knowledge
  source-grounded notes
  concepts
  maps and indexes

LoreForge framework repo
  templates
  schema
  task views
  skills
  adapters
```

## First Principle

The wiki should make both humans and agents smarter without forcing either to scan raw sources every time.


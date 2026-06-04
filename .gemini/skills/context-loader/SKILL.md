---
name: context-loader
description: Load project context from .claude/ directory at the start of every task. This ensures Gemini CLI has the same coding rules and project context as Claude Code.
---

# Context Loader Skill for Gemini

## Purpose

Load shared project context from `.claude/` so Gemini CLI operates with the same knowledge as Claude Code and Codex CLI.

## When to Activate

**ALWAYS** — run at the beginning of research or analysis tasks.

## Workflow

### Step 1: Load Coding Rules

Read relevant files from `.claude/rules/`:

```
.claude/rules/
├── coding-principles.md    # Simplicity, single responsibility, early return
├── language.md             # Think in English, respond in Korean
├── codex-delegation.md     # When/how Codex is used
└── gemini-delegation.md    # When/how Gemini is used (this agent)
```

### Step 2: Load Project Context

Read the root `CLAUDE.md` (and `AGENTS.md`) for project goals, stack, and constraints.

### Step 3: Check Prior Research

If the task relates to earlier work, scan `.claude/docs/research/` for existing findings before re-investigating.

### Step 4: Execute Research Task

With the loaded context, execute the requested research/analysis following the project coding principles and existing decisions.

## Language Protocol

- **Thinking/Reasoning**: English
- **Code examples**: English (variables, functions, comments)
- **Output**: Structured markdown, suitable for documentation

## Output Guidelines

- Structure with clear headings
- Include code examples when relevant
- Cite sources from web search
- Save comprehensive findings to `.claude/docs/research/{topic}.md`

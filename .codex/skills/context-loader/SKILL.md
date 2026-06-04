---
name: context-loader
description: ALWAYS activate this skill at the start of every task. Load project context from .claude/ directory including coding rules and project documentation before executing any task.
---

# Context Loader Skill

## Purpose

Load shared project context from `.claude/` so Codex CLI has the same knowledge as Claude Code.

## When to Activate

**ALWAYS** — run at the beginning of every task to load project context.

## Workflow

### Step 1: Load Coding Rules

Read relevant files from `.claude/rules/`:

```
.claude/rules/
├── coding-principles.md    # Simplicity, single responsibility, early return
├── language.md             # Think in English, respond in Korean
└── gemini-delegation.md    # When/how Gemini is used
```
(Skip `codex-delegation.md` — that describes how Claude calls *you*.)

### Step 2: Load Project Context

Read the root `CLAUDE.md` (and `AGENTS.md`) for project goals, stack, architecture decisions, and constraints.

### Step 3: Check Prior Research

If the task relates to earlier work, scan `.claude/docs/research/` for existing findings.

### Step 4: Execute Task

With the loaded context, execute the requested task following the coding principles and existing decisions.

## Key Rules to Remember

1. **Simplicity first** — choose readable code over complex
2. **Single responsibility** — one function/class does one thing
3. **Type hints required** — all functions need annotations (typed languages)
4. **Security** — no hardcoded secrets, validate input, parameterize SQL

## Language Protocol

- **Thinking/Reasoning**: English
- **Code**: English (variables, functions, comments)
- **User communication**: Korean (when reporting back through Claude Code)

## Output

After loading context, briefly confirm: rules loaded, project context status, ready to execute.

---
name: startproject
description: |
  Start a new project/feature implementation with multi-agent collaboration.
  Includes multi-session review workflow for quality assurance.
metadata:
  short-description: Project kickoff with multi-agent collaboration
---

# Start Project

**멀티 에이전트 협업으로 프로젝트를 시작한다.**

## Overview

이 스킬은 Claude + Codex + Gemini를 협조시켜 프로젝트 개시부터 구현후 리뷰까지를 커버한다.

> **2026-05-27 Phase 1 하이브리드 정책 (3단 폴백)**: 자동 리서치는 **Gemini CLI(`gemini -p`, stdout 캡처 정상)** 를 모델 명시(`-m`)로 호출 → 실패 시 단계 폴백한다: **① gemini-3-flash-preview(Flash 풀) → ② gemini-3.1-flash-lite-preview(별도 gemini-3.1 풀) → ③ Codex(gpt-5.5)**. 쿼터는 풀별 분리라 Pro 풀(소진)을 피하고 두 Flash 계열 풀을 갈아타며, 둘 다 막히면 Codex가 받는다. 구 Gemini CLI는 **2026-06-18 종료** 예정(이후 Codex 단독 또는 agentapi 브리지로 전환).
>
> **Antigravity CLI(`agy`) 참고**: Gemini CLI의 후속이지만 `agy --print`가 응답을 대체 화면 TUI로만 렌더링하고 리다이렉트/파이프 stdout에 출력하지 않는 버그(v1.0.2 Windows, 트랜스크립트도 비어 디스크 복구 불가)로 **서브에이전트 자동 캡처가 불가능**하다. 따라서 agy는 1M 컨텍스트·멀티모달 심층 리서치 시 **사용자가 대화형으로 직접 실행**하는 선택 경로로만 둔다. agy print-stdout 버그가 고쳐지거나 `agentapi` 브리지가 생기면 Phase 1 기본을 agy로 올릴 수 있다.

## Workflow

```
Phase 1: Research (gemini-3-flash → gemini-3.1-flash-lite → Codex; agy optional manual)
    ↓
Phase 2: Requirements & Planning (Claude)
    ↓
Phase 3: Design Review (Codex via Subagent)
    ↓
Phase 4: Task Creation (Claude)
    ↓
Phase 5: CLAUDE.md Update (Claude)
    ↓
[Implementation...]
    ↓
Phase 6: Multi-Session Review (New Session + Codex)
```

---

## Phase 1: Research — 3단 폴백 (Gemini → Gemini-Lite → Codex) (Background)

**Task tool에서 하위 에이전트를 시작하고 리포지토리를 분석한다. 모델을 매 호출 `-m`으로 명시해 소진된 Pro 풀을 회피하고, 실패 시 단계적으로 폴백한다.** (하이브리드 정책 — 위 메모 참조)

> **쿼터 풀 설계 근거 (2026-05-27)**: Gemini 쿼터는 풀별 분리(Flash / gemini-3.1 / Pro). Pro 풀은 소진(100%), Flash·gemini-3.1 풀은 여유. `gemini-3-flash-preview`(Flash 풀, 1M 컨텍스트, 최고 성능)를 1차로, 소진 시 `gemini-3.1-flash-lite-preview`(**별도 gemini-3.1 풀**, Thinking Mode)로 풀을 갈아타고, 그래도 실패하면 Codex로 넘어간다. `.gemini/settings.json` 기본 모델도 `gemini-3-flash-preview`로 변경됨(인터랙티브 포함 baseline).

```
Task tool parameters:
- subagent_type: "general-purpose"
- run_in_background: true
- prompt: |
    Research for: {feature}

    공통 프롬프트(아래 P): "Analyze this repository for: {feature}
       Provide:
       1. Repository structure and architecture
       2. Relevant existing code and patterns
       3. Library recommendations
       4. Technical considerations"

    실패 판정: 출력이 비었거나 'quota'/'exhausted'/'capacity'/'429'/'error'/'Error'/'404' 포함 시.

    1. TIER 1 (PRIMARY) — Gemini 3 Flash (Flash 풀, 1M 컨텍스트, 최고 성능):
       gemini -m gemini-3-flash-preview -p "{P}" --include-directories . 2>&1
       → 성공하면 이 결과 사용. 실패 판정이면 TIER 2로.

    2. TIER 2 (FALLBACK 1) — Gemini 3.1 Flash-Lite (별도 gemini-3.1 풀로 갈아타기, Thinking Mode):
       gemini -m gemini-3.1-flash-lite-preview -p "{P}" --include-directories . 2>&1
       → 성공하면 이 결과 사용. 실패 판정이면 TIER 3로.

    3. TIER 3 (FALLBACK 2) — Codex (model은 .codex/config.toml 기본값 gpt-5.5,
       read-only 샌드박스가 현재 작업 디렉토리(레포)를 자동 포함).
       ⚠️ codex CLI는 Bash(codex:*)로 사전 허용됨 — 반드시 아래 codex exec를 실제 Bash로 실행할 것.
          (자체 파일 읽기/자체 분석으로 대체하지 말 것):
       codex exec --sandbox read-only --skip-git-repo-check "{P}" 2>/dev/null

    4. Save the successful tier's full output to: .claude/docs/research/{feature}.md
       (어느 도구·모델인지 머리말에 명시: '## Source: gemini-3-flash-preview' /
        '## Source: gemini-3.1-flash-lite-preview' / '## Source: Codex (gpt-5.5)')

    5. Return CONCISE summary (5-7 bullet points) + which tier/model produced it
```

### (선택) Antigravity CLI 심층 리서치 — 수동 대화형

1M 컨텍스트·멀티모달·웹 그라운딩이 필요한 큰 리서치는 사용자가 직접 `agy`를 대화형으로 실행한다(자동 캡처 불가 — 위 이식 메모 참조). 결과는 사용자가 `.claude/docs/research/{feature}.md`에 붙여넣고 알려준다.

```bash
# 바이너리: C:\Users\dt585\AppData\Local\agy\bin\agy.exe  (PATH 미등록 시 전체 경로 또는 `agy install`)
# 대화형(현 워크스페이스 컨텍스트 포함):
agy -i "Analyze this repository for: {feature}" --add-dir .

# 헤드리스 플래그(stdout 캡처는 v1.0.2 Windows 빌드에서 미동작):
#   --print / -p      단일 프롬프트 비대화형 실행 (alias --prompt)
#   --add-dir DIR     워크스페이스에 디렉토리 추가 (구 --include-directories 대체)
#   --print-timeout   print 대기 타임아웃 (기본 5m)
#   --dangerously-skip-permissions   툴 권한 자동 승인
```

---

## Phase 2: Requirements Gathering (Claude)

**사용자에게 질문하여 요구 사항을 명확히 한다.**

Ask in Korean:

1. **목적**: 무엇을 달성하고 싶습니까?
2. **스코프**: 포함하거나 제외하는 것은?
3. **기술적 요건**: 특정 라이브러리, 제약은?
4. **성공기준**: 완료의 판단기준은?

**Draft implementation plan based on Phase 1 research + user answers.**

---

## Phase 3: Codex Design Review (Background)

**Task tool에서 하위 에이전트를 시작하고 Codex에서 계획 검토한다.**

```
Task tool parameters:
- subagent_type: "general-purpose"
- run_in_background: true
- prompt: |
    Review plan for: {feature}

    Draft plan: {plan from Phase 2}

    1. Call Codex CLI:
       codex exec --sandbox read-only --skip-git-repo-check "
       Review this implementation plan:
       {plan}

       Analyze:
       1. Approach assessment
       2. Risk analysis
       3. Implementation order
       4. Improvements
       " 2>/dev/null

    2. Return CONCISE summary:
       - Top 3-5 recommendations
       - Key risks
       - Suggested order
```

---

## Phase 4: Task Creation (Claude)

**서브에이전트 요약을 통합하고 작업 목록을 작성한다.**

Use TodoWrite to create tasks:

```python
{
    "content": "Implement {specific feature}",
    "activeForm": "Implementing {specific feature}",
    "status": "pending"
}
```

---

## Phase 5: CLAUDE.md Update (IMPORTANT)

**프로젝트 관련 정보를 CLAUDE.md에 추가한다.**

Add to CLAUDE.md:

```markdown
---

## Current Project: {feature}

### Context
- Goal: {1-2 sentences}
- Key files: {list}
- Dependencies: {list}

### Decisions
- {Decision 1}: {rationale}
- {Decision 2}: {rationale}

### Notes
- {Important constraints or considerations}
```

**This ensures context persists across sessions.**

---

## Phase 6: Multi-Session Review (Post-Implementation)

**구현 완료 후 다른 세션에서 리뷰를 실시한다.**

### Option A: New Claude Session

1. Start new Claude Code session
2. Run: `git diff main...HEAD` to see all changes
3. Ask Claude to review the implementation

### Option B: Codex Review (via Subagent)

```
Task tool parameters:
- subagent_type: "general-purpose"
- prompt: |
    Review implementation for: {feature}

    1. Run: git diff main...HEAD
    2. Call Codex CLI:
       codex exec --sandbox read-only --skip-git-repo-check "
       Review this implementation:
       {diff output}

       Check:
       1. Code quality and patterns
       2. Potential bugs
       3. Missing edge cases
       4. Security concerns
       " 2>/dev/null

    3. Return findings and recommendations
```

### Why Multi-Session Review?

- **Fresh perspective**: New session has no bias from implementation
- **Different context**: Can focus purely on review, not implementation details
- **Codex strength**: Deep analysis without context pollution

---

## User Confirmation

Present final plan to user (in Korean):

```markdown
## 프로젝트 계획 : {feature}

### 조사 결과 (Gemini 또는 Codex)
{Key findings - 3-5 bullet points}

### 설계 정책 (Codex 검토)
{Approach with refinements}

### 작업 목록 ({N}개)
{Task list}

### 위험과 주의사항
{From Codex analysis}

### 다음 단계
1. 이 계획으로 진행하시겠습니까?
2. 구현 완료 후 다른 세션에서 검토를 수행한다.

---
이 계획으로 진행하시겠습니까?
```

---

## Output Files

| File | Purpose |
|------|---------|
| `.claude/docs/research/{feature}.md` | Phase 1 research output (Gemini→Codex fallback; or manual agy) |
| `CLAUDE.md` | Updated with project context |
| Task list (internal) | Progress tracking |

---

## Tips

- **All Gemini/Codex work through subagents** to preserve main context (deep agy research is manual/interactive)
- **Codex 역할**: 진단·리뷰·설계·터미널/로그 분석은 Codex read-only 주력. 구현은 Claude 단독 작성자. Codex `workspace-write`는 격리 파일만 — 라이브/공유 파일은 diff 반환받아 Claude 적용, 실행 후 반드시 Claude가 Read() 재로드 (상세: `.claude/rules/codex-delegation.md`)
- **Update CLAUDE.md** to persist context across sessions
- **Use multi-session review** for better quality assurance
- **Ctrl+T**: Toggle task list visibility

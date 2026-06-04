# Codex Delegation Rule

**Codex CLI (gpt-5.5)** — 설계·디버깅·코드리뷰 + **터미널/로그/grep 진단·회귀 수리 계획**(read-only 주력). 출력이 클 것으로 예상되면 서브에이전트 경유.

> 모델은 `--model` 플래그 없이 호출하여 `.codex/config.toml`의 기본값(`gpt-5.5`)을 따른다. SSOT는 config.toml 한 곳.

> **역할 분배 원칙**: Codex는 **진단·조사·리뷰의 주력**으로 쓴다. 단 **라이브 작업 트리의 능동 작성자로는 쓰지 않는다** — Claude가 단일 작성자(하니스가 파일 상태를 소유). 이유는 아래 two-writer 데싱크 참조.

## When to Consult

| 상황 | 트리거 |
|------|--------|
| 설계 결정 | "어떻게 설계?", "아키텍처", "design", "architecture" |
| 디버깅 | "왜 안 돼?", "에러", "debug", "not working" |
| 트레이드오프 | "어느 쪽이 좋아?", "compare", "which is better" |
| 구현 계획 | "어떻게 구현?", "implement", "build" |
| 코드리뷰 | "리뷰해줘", "review", "check this" |
| **터미널/로그 진단** | "로그 분석", "grep 추적", "왜 느려?", "trace", "diagnose" |
| **회귀 수리 계획** | "여러 번 고쳤는데 또", "재발", "regression", "stuck" (read-only 루프) |

**Skip**: 단순 파일 편집, git 작업, 테스트 실행, 명확한 단일 해결책이 있는 경우.

## ⚡ Critical Gotchas (운영 확정)

Codex CLI가 멈추지 않고 빠르게 도는 데 **다음 3가지가 필수**다.

### 1. `< /dev/null` 필수 — stdin 닫지 않으면 무한 대기 (결정적)

Codex는 프롬프트 인자를 받아도 별도로 stdin을 추가로 읽는다 (실행 시 `Reading additional input from stdin...` 표시). foreground면 곧 EOF라 끝나지만, **백그라운드/하니스로 넘어가면 stdin이 안 닫혀 무한 대기**한다.

```bash
codex exec --sandbox read-only ... "프롬프트" < /dev/null
                                              ^^^^^^^^^^^^ 항상 추가
```

### 2. 검토 코드는 프롬프트에 인라인 — Codex에게 파일 직접 읽기 금지

"foo.py 열어서 검토해"식으로 시키면 Codex가 파일 I/O로 느려진다. 큰 블록은 미리 로컬에서 떠서 프롬프트에 끼워 전달한다(특히 원격/네트워크 드라이브 작업 트리에서 치명적).

### 3. effort 명시 + summary 축소

`.codex/config.toml` 기본값은 `high + detailed`라 무겁다. 호출별 오버라이드 권장:

| effort | 대략 시간 | 용도 |
|---|---|---|
| `low` | ~10s | 트리비얼 sanity (yes/no, 단순 계산) |
| `medium` | ~70s | **일반 컴파일·SQL·런타임 검증 — 기본 권장** |
| `high` | ~230s | Non-trivial · adversarial · 누락 발굴 (FP도 같이 옴, 사람 필터 필요) |

`reasoning_summaries=detailed`면 출력이 부풀어 후처리 비용 증가. verdict만 필요할 땐 `-c model_reasoning_summary=auto` 추가.

### 백그라운드 서브에이전트 한계

백그라운드 서브에이전트는 비대화형이라 권한 프롬프트가 자동 deny된다 → **복합 Bash · Write가 거부**된다. 단일 `codex exec "...인라인..."` 만 허용.

```
✅ 서브에이전트 OK: 한 줄 codex exec, 모든 컨텍스트 인라인 영어
❌ 서브에이전트 NG: cat "$CLAUDE_JOB_DIR/..." / git diff $(...) / Write 임시파일
```

**큰 코드 인라인 전달은 메인 세션에서** 수행한다(heredoc + sed로 로컬에서 떠서 prompt.txt 생성 → cat substitution).

---

## How to Call

### 기본 레시피 — 큰 블록 코드 리뷰 (메인 세션)

```bash
cd "<repo>" && {
cat <<'HDR'
<English review prompt with the check-list inline>
=== CODE ===
HDR
sed -n 'START,ENDp' path/to/file
} > _codex_prompt.txt && start=$(date +%s) && \
codex exec --sandbox read-only --skip-git-repo-check \
  -c model_reasoning_effort=medium "$(cat _codex_prompt.txt)" < /dev/null 2>&1; \
rc=$?; end=$(date +%s); echo "=== rc=$rc ELAPSED $((end-start))s ==="; \
rm -f _codex_prompt.txt
```

### 짧은 질문 (메인 직접 호출)

```bash
codex exec --sandbox read-only --skip-git-repo-check \
  -c model_reasoning_effort=low "Brief question in English" < /dev/null 2>&1
```

### 서브에이전트 (단순 인라인 질문만 — 큰 파일·diff 전달 불가)

```
Task tool:
- subagent_type: "general-purpose"
- run_in_background: true
- prompt: |
    Run via Bash (codex pre-approved). Do NOT use $CLAUDE_JOB_DIR, cat external files, or git diff substitutions — those get auto-denied here:
    codex exec --sandbox read-only --skip-git-repo-check \
      -c model_reasoning_effort=medium \
      "{question in English with all needed context inline}" < /dev/null 2>/dev/null
    Return CONCISE verdict only.
```

복잡한 파일/diff 전달이 필요하면 서브에이전트 대신 **메인 세션**의 "기본 레시피"를 사용한다.

## Sandbox Modes

| Mode | Use Case |
|------|----------|
| `read-only` | 분석, 리뷰, 디버깅 조언, 터미널/로그 진단, 회귀 수리 계획 (기본) |
| `workspace-write` | **격리 산출물 전용** (새 초안 파일, 마이그레이션 스크립트 등). 라이브 트리 직접 편집 금지 |

## ⚠️ workspace-write 안전 프로토콜 (two-writer desync 방지)

> Claude 하니스는 세션 내내 파일 상태를 추적한다. Codex가 `workspace-write`로 같은 트리를 뒤에서 수정하면, Claude의 다음 `Edit`이 stale 기준으로 작동해 **조용한 로직 손상**이 날 수 있다. 그래서:

1. **라이브·공유·규칙민감 파일은 `workspace-write` 금지** → Codex가 **diff/patch를 반환**하고 **Claude가 적용**한다.
2. `workspace-write`는 **완전 격리 작업**에만 (새 파일·임시 경로·Claude가 안 건드리는 파일).
3. 위임 시 허용/금지 파일·관련 규칙을 프롬프트에 **인라인 명시**(Codex는 매 호출 fresh-context).
4. Codex 실행 중 Claude는 해당 파일 편집 중단.
5. 실행 후 Claude는 결과 파일을 **반드시 `Read()`로 재로드**한 뒤에만 다음 편집.
6. Codex 산출물은 그대로 배포하지 않고 Claude가 규칙 검토 후 통합.

## 역할 매트릭스 (요약)

| 영역 | 주력 |
|------|------|
| 라이브 코드 구현·통합 | **Claude** (단일 작성자) |
| 터미널/로그/grep 진단, 디버깅, 코드리뷰, 설계 | **Codex** (read-only) |
| 격리 산출물 초안 | Codex `workspace-write`(조건부) → Claude 검토 |

**언어**: Codex에게는 English → 사용자에게는 Korean으로 보고.

# Gemini Delegation Rule

**Gemini CLI (gemini-3-flash-preview)** — 리서치·대규모 분석 전담. 출력이 크므로 서브에이전트 경유 권장.

> ⚠️ **모델 명시(`-m`) 필수**: 쿼터는 풀별 분리이고 소진된 풀로 라우팅되면 `"exhausted capacity"`가 난다. 기본은 `gemini-3-flash-preview`(Flash 풀). 실패 시 **3단 폴백**: → `gemini-3.1-flash-lite-preview`(별도 풀) → `codex`(gpt-5.5). 모델명은 정보용 라벨이며 실제 모델은 CLI 바이너리가 선택한다. 시크릿 파일은 `.geminiignore`로 제외한다(`--include-directories .` 사용 시).

## Gemini vs Codex

| Task | 담당 |
|------|------|
| 설계 결정, 디버깅, 코드리뷰 | Codex |
| 리서치, 문서 조사, 코드베이스 전체 분석, 멀티모달 | **Gemini** |

## When to Consult

트리거: "조사해", "리서치해", "최신 문서", "PDF/영상/오디오", "코드베이스 전체", "research", "investigate", "latest docs"

**Skip**: 설계 결정, 코드 구현, 디버깅, 단순 파일 작업 (→ Codex 또는 직접 처리).

## How to Call

**서브에이전트 (권장):**
```
Task tool:
- subagent_type: "general-purpose"
- run_in_background: true
- prompt: |
    1. gemini -m gemini-3-flash-preview -p "{research question in English}" 2>&1
       (실패[빈출력/quota/exhausted/429/error/404] 시 → -m gemini-3.1-flash-lite-preview
        → 그래도 실패면 codex exec --sandbox read-only --skip-git-repo-check "..." < /dev/null)
    2. Save full output to: .claude/docs/research/{topic}.md (출처 모델 머리말 명시)
    3. Return CONCISE summary (5-7 bullet points).
```

## CLI Commands

```bash
gemini -m gemini-3-flash-preview -p "{question}" 2>&1                          # 리서치
gemini -m gemini-3-flash-preview -p "{question}" --include-directories . 2>&1  # 코드베이스 분석
gemini -m gemini-3-flash-preview -p "{prompt}" < file.pdf 2>&1                 # 멀티모달
```

**언어**: Gemini에게는 English → 결과는 .claude/docs/research/ 저장 → 사용자에게는 Korean.

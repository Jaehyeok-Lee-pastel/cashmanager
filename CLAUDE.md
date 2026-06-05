# CLAUDE.md — Project Template (FastAPI · React · Supabase)

> **이 파일은 인덱스/포인터다.** 본문 상세는 `.claude/rules/`·`docs/`에 두고, 여기에는 핵심 규칙과 링크만 둔다.
> 이 저장소는 **다양한 프로젝트의 베이스 템플릿**이다 — 멀티 CLI 오케스트레이션 + FastAPI/React/Supabase 모노레포 스캐폴딩.

## 🧱 스택 & 모노레포 구조

| 영역 | 스택 | 위치 |
|---|---|---|
| API | Python 3 · FastAPI · pydantic-settings · supabase-py · OpenAI | `apps/api/` |
| Web | React 19 · Vite 6 · TypeScript(strict) · supabase-js | `apps/web/` |
| DB | Supabase(Postgres) · RLS · migrations | `supabase/` |
| 설계문서 | 번호 폴더 체계 | `docs/` |

```
apps/api    FastAPI backend (app/{api,core,schemas,services,repositories,tests})
apps/web    React+Vite frontend (src/{app,components,features,lib,styles})
supabase    migrations/ + seed.sql
docs        00_overview … 08_coding_guidelines
```
로컬 실행: 루트 [`README.md`](README.md) 참조.

## 🤖 멀티 CLI 오케스트레이션

이 프로젝트는 Claude Code를 오케스트레이터로, Codex·Gemini CLI를 전문 위임 대상으로 쓴다.

| 에이전트 | 역할 | 호출 |
|---|---|---|
| **Claude Code** (main) | 오케스트레이터 + **단일 작성자**(파일 편집·통합) | 사용자 프롬프트 |
| **Codex CLI** (`gpt-5.5`) | 설계·디버깅·코드리뷰·로그/터미널 진단 (read-only 주력) | [`rules/codex-delegation.md`](.claude/rules/codex-delegation.md) · `/codex-system` |
| **Gemini CLI** (`gemini-3-flash-preview`) | 리서치·대규모 분석·멀티모달 | [`rules/gemini-delegation.md`](.claude/rules/gemini-delegation.md) · `/gemini-system` |

**원칙**: 무거운 작업(리서치·심층추론)은 서브에이전트로 위임해 메인 컨텍스트를 보존한다. 라이브 파일의 실제 편집은 항상 Claude가 한다(two-writer desync 방지 — 상세는 codex-delegation.md).

## 🪝 활성 훅 (advisory, `.claude/settings.json`)

| 훅 | 이벤트 | 역할 |
|---|---|---|
| `agent-router.py` | UserPromptSubmit | 키워드 감지 → Codex/Gemini 위임 힌트 주입 |
| `guard-bash.py` | PreToolUse(Bash) | **유일한 차단 훅** — 파괴적 명령·SQL·시크릿 누출 차단 |
| `check-codex-before-write.py` | PreToolUse(Edit/Write) | 고위험 영역(auth/payment 등) 편집 시 Codex 리뷰 권유 |
| `log-cli-tools.py` | PostToolUse(Bash) | Codex/Gemini 호출을 `.claude/logs/cli-tools.jsonl`에 기록 |
| `lint-on-save.py` | PostToolUse(Edit/Write) | `.py` 저장 시 ruff/ty (uv 또는 ruff 있을 때만) |

> opt-in 훅(미연결, 노이즈 우려로 기본 비활성): `check-codex-after-plan.py`, `suggest-gemini-research.py`, `post-implementation-review.py`. 필요하면 `settings.json`에 와이어링한다.

## 📐 규칙 (`.claude/rules/`)

- [`language.md`](.claude/rules/language.md) — 사고는 영어, 사용자 응답은 한국어, 코드는 영어
- [`coding-principles.md`](.claude/rules/coding-principles.md) — 단순성·단일책임·early return·타입힌트
- [`codex-delegation.md`](.claude/rules/codex-delegation.md) / [`gemini-delegation.md`](.claude/rules/gemini-delegation.md) — 위임 규칙
- **스택 규칙**: [`stack-python-fastapi.md`](.claude/rules/stack-python-fastapi.md) · [`stack-react-typescript.md`](.claude/rules/stack-react-typescript.md) · [`stack-supabase.md`](.claude/rules/stack-supabase.md)
- 상세 가이드라인: [`docs/08_coding_guidelines/`](docs/08_coding_guidelines/) · 품질 체크리스트 [`05_quality_checklist.md`](docs/08_coding_guidelines/05_quality_checklist.md)

## 🚀 스킬

- `/startproject` — 멀티에이전트 협업으로 신규 기능 착수(리서치→요구사항→설계리뷰→구현→리뷰)
- `/codex-system`, `/gemini-system` — 위임 호출 패턴 참조

## 📁 산출물 위치

| 위치 | 용도 |
|---|---|
| `.claude/docs/research/{topic}.md` | Gemini/Codex 리서치 결과 |
| `.claude/logs/cli-tools.jsonl` | Codex/Gemini 호출 로그 |

---

## 🎯 Current Project — 캐시매니저 (AI 자연어 가계부 MVP)

**제품명**: 캐시매니저 (CashManager) — 기존 업무툴 "워크매니저"와 패밀리 톤.
**목표**: "입력이 안 귀찮은, 단순하고 똑똑한 개인 가계부". 핵심 무기 = **AI 입력 마찰 0**(자연어 한 줄 → LLM 파싱 → 1탭 confirm → 저장). 범용 소비자 타깃, dogfooding 우선. 뱅크샐러드/토스의 자동연동과 정면승부하지 않고 "수동인데 안 아픈 입력"으로 우회.

**핵심 결정** (상세: `.claude/docs/research/mvp-design-final.md`, 경쟁분석: `budget-app-competitors.md`)
- 데이터: `transactions` 단일 ledger + `source` enum(nl_text/manual/receipt/voice/import) + `raw_input`/`parse_meta`. 금액 `amount_minor` bigint(KRW 정수원). `merchant_category_map` = 상호→카테고리 **학습 루프 활성화**(저장 시 upsert, parse 시 LLM 전 조회).
- NL: 정규식 선처리(`nl_preprocess`, 한글 금액·날짜, 유닛테스트 강커버) → fast-path 또는 LLM 1회(Structured Outputs strict, `max_retries=0`) → 미저장 미리보기 → confirm. 실패는 `needs_manual` 200 폴백.
- 보안: 전 테이블 RLS(`user_id=auth.uid()`), 백엔드 service_role이라 service 레이어 소유권 재검증 + `enforce_category_owner` 트리거.
- MVP 스코프: 기본 가계부 + 자연어 입력 1채널. (영수증 OCR·음성·CSV·예산은 v2)

**핵심 파일**
- API: `apps/api/app/services/{nl_preprocess,nl_service,openai_service,tx_service,category_service,summary_service}.py`, `repositories/`, `api/routes/{me,categories,transactions,summary}.py`, `core/{timeutils,ratelimit}.py`
- DB: `supabase/migrations/202606020900_init_ledger.sql`
- Web: `apps/web/src/app/AuthProvider.tsx`, `features/{auth,ledger,categories,summary}/`, `lib/{budget,types,money}.ts`

**상태**: MVP 완성·dogfooding 중. 디자인 토큰 시스템·Lucide 아이콘·요약 고도화·반응형 보정 완료. 분류 QA 176케이스 100%.

**진행 기록 (의사결정은 `.claude/docs/research/`에 수치 근거 저장)**
- 영수증 OCR v2 → **검증 결과 보류**(CONDITIONAL 23.5/60: 리텐션·수요 약함, 이미 레드오션). 조건부 GO는 "카드연동 마트거래 품목 enrichment"로 극단 축소 시.
- 차기 기능 발굴 → **F1 월 예산** 만장일치 1위(40/50). `/startproject`로 착수.

**F1 월 예산 (구현 완료, 마이그레이션 적용 대기)**
- 카테고리별 월 한도(반복) + 직전 3개월 평균 자동제안 + 요약 진행바에 실적/한도·임계색(80%amber/100%red)·초과 배지.
- 신규: `supabase/migrations/202606040900_add_budgets.sql`(category_budgets, RLS+with check+소유권 트리거), api `schemas/budget.py`·`repositories/budget_repo.py`·`services/budget_service.py`·`routes/budgets.py`, summary에 limit_minor 병합(테이블 없을 때 방어). web `features/budgets/`, summary 진행바 예산화, 예산 nav 탭.
- pytest, `npm run build` 통과. 마이그레이션 `202606040900_add_budgets.sql` 적용 완료(라이브 동작 확인).

**F2 AI 자연어 질의 + F3 인사이트/경고 (구현 완료, 마이그레이션 불필요 — 읽기전용)**
- "분석" 탭 신설(5번째). F2=POST `/assistant/query`(요약+예산 컨텍스트→LLM 한국어 답변, rate-limit+threadpool, 데이터/지시 분리로 인젝션 방지, 실패 시 고정 폴백). F3=GET `/insights?month`(규칙기반: 예산 80%/초과 경고·전월대비·최다지출 + LLM 한 줄 코치 best-effort).
- 신규: api `schemas/analysis.py`·`services/{insights,assistant}_service.py`·`routes/{insights,assistant}.py`, `openai_service.complete()`, `timeutils.prev_month()`. web `features/analysis/AnalysisScreen.tsx`, lib 래퍼.
- pytest 57 passed, build 통과. Codex 설계리뷰 반영(F3 선구현·전월0 처리·인젝션 분리·LLM 폴백).
- 권장 로드맵 F1→F2/F3 완료. 푸시 알림은 인프라 필요로 후속.

**버전 v1.0 스냅샷** (`main_ver1.0` 브랜치 + `v1.0.0` 태그): 개인 사용·지인 공유용 기본 안정 버전. 이후 main은 기능 추가·실험. 보안 감사(인젝션·비용통제)·최종점검 A−(93)·CSV 백업·비밀번호 재설정·구글 로그인 완비.

**고도화 F4~F6 (forward-looking 예산 3종, 구현 완료 — 마이그레이션 불필요)**
- 후보 리서치/점수화: `.claude/docs/research/feature-advancement-ranking.md`(14후보 다관점 채점, ML류는 단일사용자 데이터 희소로 보류).
- **F4 월말 지출 페이스 예측(1위 85)**: `timeutils.month_progress`(경과/총일수), summary에 `projected_*`(경과7일+진행중 달만), insights '이 속도면 초과 예상' warn(예상≥한도×1.05·0.8경고 중복회피), 요약 '월말 예상'·'예상 초과' 배지. Codex 설계리뷰 반영.
- **F5 달력 뷰(2위 79)**: 내역 탭 리스트↔달력 토글, `CalendarView`(일별 지출 격자, 날짜탭→일자필터 드릴다운). 순수 프론트.
- **F6 Safe-to-Spend(3위 78)**: summary에 `budget_total/safe_to_spend/daily_allowance`(당월·예산설정 시만), 요약 상단 '오늘 쓸 수 있어요' 카드(초과 시 분기). recurring 차감은 데이터모델 부재로 제외(Codex 권고).
- 신규 테스트: month_progress 엣지 8 + safe_to_spend 4. pytest 71 통과, build 통과.

**콜드스타트 예산 초안 (구현 완료)**: 신규 사용자(3개월 데이터 없음)용. `GET /budgets/template?income_minor=` → 소비예산(소득×0.70) 통계청 비율 배분, 카드대금 0%. BudgetScreen '소득으로 초안 만들기'. 근거 `cold-start-budget.md`.

**신용카드 처리 = 이체(transfer) 방향 (구현 완료, 마이그레이션 적용 필요)**: 카드대금 이중계산 방지. 결제시점=expense, 월 카드대금=transfer(지출/예산/인사이트 제외). 근거 `credit-card-handling.md`(YNAB·Monarch·뱅크샐러드 등).
- 마이그레이션 `202606050900_add_transfer_direction.sql`(direction check에 transfer 추가). **Supabase SQL Editor에 적용 필요.**
- direction Literal+transfer, `nl_preprocess.is_card_payment`(카드대금/카드값/신용카드 결제·자동이체 감지, 개별 카드결제는 제외), `nl_service._transfer_result`(카드대금→transfer fast-path), LLM 스키마/규칙 transfer, `_learn_merchant`는 expense만. web: 이체 옵션·중립 표기. 요약/내역/달력은 expense만 합산이라 자동 제외.
- pytest 82 통과, build 통과.

**오타 견고성 — 결정론 계층 (구현 완료)**: 근거 `typo-robustness.md`(4관점 리서치). 두 문제 분리.
- `hangul.py`(무의존 순수파이썬): NFC + 자모 오토마타 복원. "기ㅁ밥"→김밥, "비해ㅇ기"→비행기(떠다니는 호환자모를 앞 음절 종성으로, 보수 가드: 종성 비었음+ㅋㅋ/연속자모 아님). NFC 단독으론 불가(Unicode가 호환자모 합성 안 함).
- `nl_preprocess.restore_amount_units`: 금액 단위 오타 변이표(처넌→천원, 마누언→만원…) **숫자 인접 시에만** 발동(과교정 0). "3처넌"→3000, "12마누언"→120000.
- `nl_service.parse`는 wrapper로 `hangul.clean` 적용 후 파싱, **원문은 raw_input 보존** + `parse_meta.corrected_from` 기록. memo=정규화형, raw_input=원문.
- "뱅기"류 구어축약은 결정론 불가 → LLM/학습맵(이미 처리). 로드맵 4(퍼지매칭)·5(LLM normalized 필드)는 보류.
- test: hangul 6 + 금액오타 5. pytest 93 통과.

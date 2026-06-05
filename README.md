# 캐시매니저 (CashManager)

> **"입력이 안 귀찮은, 단순하고 똑똑한 개인 가계부"** — 자연어 한 줄("스벅 아메리카노 4900")이면 기록 끝.

AI가 자연어 한 줄을 금액·카테고리·날짜로 파싱해 저장하는 개인 가계부. 카드 자동연동(MyData) 대신 **"수동인데 안 아픈 입력"** 으로 승부한다.

<!-- 스크린샷: docs/images/ 에 png를 넣으면 아래가 표시됩니다 -->
<!--
| 기록 | 요약(예산) | 분석(AI) |
|---|---|---|
| ![home](docs/images/home.png) | ![summary](docs/images/summary.png) | ![analysis](docs/images/analysis.png) |
-->

- **스택**: React 19 + Vite + TypeScript / FastAPI / Supabase(Postgres) / OpenAI
- **상태**: 작동하는 MVP (개인 dogfooding 가능). 분류 정확도 QA 176케이스 **100%**, 백엔드 pytest 59 통과.
- **개발 방식**: Claude Code 오케스트레이션 + Codex/Gemini 위임 + Workflow 다중에이전트 설계/리뷰 (상세 [`CLAUDE.md`](CLAUDE.md))

### 버전 & 브랜치
- **`v1.0.0` / `main_ver1.0`** — **기본 버전(개인 사용 · 지인 공유용)**. 본인이 직접 쓰고 지인에게 공유하려고 간단하게 만든 안정 스냅샷. 자연어 입력·예산·요약·AI 분석·인증 3종·CSV 백업까지 갖춘 완결 버전.
- **`main`** — 이후 **기능 추가 및 실험적 작업**을 진행하는 개발 브랜치.

---

## ✨ 기능

| 기능 | 설명 |
|---|---|
| **자연어 한 줄 입력** | "맥날 만이천원" → 금액 12,000·식비 자동 분류 → 1탭 confirm → 저장 |
| **결정론 선처리** | 한글 금액 수사(만이천원·3만2천·백만원), 상대날짜(어제·지난주 금요일) 정규식 파싱 → LLM 비용·오류 절감 |
| **학습 루프** | 상호→카테고리 매핑 저장(merchant_category_map). 한 번 고치면 다음부턴 LLM 없이 즉시 분류 |
| **카테고리** | 기본 12종 자동 시드 + Lucide 아이콘. 추가/수정/보관 |
| **요약** | 월별 도넛 차트(중앙 총액) + 카테고리 진행바 + 수입/잔액 |
| **월 예산** | 카테고리별 한도 + 최근 3개월 평균 자동제안 + 진행바 임계색(80%/100%)·초과 배지 |
| **AI 분석** | 자연어 질의("이번 달 카페 얼마 썼어?") + 인사이트 카드(예산경고·전월대비·최다지출·AI코치) |
| **인증** | Supabase Auth (이메일/Google) |
| **디자인** | plain CSS 3계층 토큰 시스템, 다크 핀테크 톤, Pretendard, 반응형 |
| **PWA** | 폰 홈화면 추가 시 앱처럼 실행 (manifest + 서비스워커, 새 의존성 0) |

---

## 🏗️ 아키텍처

```txt
apps/
  api/   FastAPI — app/{api/routes, services, repositories, schemas, core, tests}
         라우터 얇게 · 로직 services/ · DB repositories/ · 타입 schemas/(Pydantic)
  web/   React+Vite — src/{app, features, components, lib, styles}
         features/{auth, ledger, categories, summary, budgets, analysis}
supabase/migrations/   init_ledger.sql, add_budgets.sql
docs/                  설계·규약 + 리서치/의사결정 (.claude/docs/research/)
```

**데이터 모델**: `transactions`(단일 ledger, `amount_minor` bigint KRW, `source` enum, `raw_input`/`parse_meta`) · `categories` · `category_budgets` · `merchant_category_map`. 전 테이블 RLS(`user_id = auth.uid()`) + 백엔드 service_role이라 서비스 레이어에서 소유권 재검증 + DB 트리거 방어.

**NL 파이프라인**: `정규식 선처리 → 학습맵 조회 → (필요시) LLM 1회(Structured Outputs) → 미저장 미리보기 → 1탭 confirm → 저장`. LLM 실패는 `needs_manual` 폴백(막다른 길 없음).

---

## 🚀 로컬 실행

> 포트는 예시. 다른 앱과 충돌하면 비어 있는 포트로 바꾸면 된다(웹의 `VITE_API_BASE_URL`·API의 `CORS_ORIGINS`를 맞출 것).

### 1) Supabase
프로젝트 생성 → **SQL Editor**(PostgreSQL, SSMS 아님)에서 `supabase/migrations/`의 `.sql`을 **시간순 적용**:
1. `202606020900_init_ledger.sql`
2. `202606040900_add_budgets.sql`
- 적용 후 필요시 `notify pgrst, 'reload schema';`

### 2) Backend (apps/api)
```powershell
cd apps/api
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env   # SUPABASE_URL/SERVICE_ROLE_KEY/JWT_SECRET, OPENAI_API_KEY
uvicorn app.main:app --reload --port 8001
```
`http://localhost:8001/health` · `/docs` · 테스트: `python -m pytest app/tests`

### 3) Frontend (apps/web)
```powershell
cd apps/web
npm install
Copy-Item .env.example .env.local   # VITE_API_BASE_URL, VITE_SUPABASE_URL/ANON_KEY
npm run dev -- --port 6173
```
`http://localhost:6173` — 회원가입(가입 시 트리거가 기본 카테고리 12종 시드) → 한 줄 입력 테스트.

> 분류 품질 회귀 점검: `apps/api/scripts/eval_categorization.py` (실 OpenAI 호출, 176케이스).

---

## 📊 현재 수준 & 로드맵

자세한 점검·의사결정은 [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md) 참고.

- **나 혼자/지인용**: 충분히 작동 (배포만 하면 매일 사용 가능)
- **공개 출시**: 미흡 — 배포·비용가드·리텐션 검증 필요
- **보류**: 영수증 OCR (검증 CONDITIONAL 23.5/60 — 리텐션·수요 약함)
- **완료 로드맵**: F1 월예산 → F2 AI질의 → F3 인사이트 (ROI 발굴 1~3위)
- **배포**: [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) (Vercel+Render+Supabase, 무료~소액 → 폰 PWA)
- **다음 후보**: 배포 → 지인 베타(리텐션 실측)

---

## 🤖 AI 오케스트레이션 (개발 시)
Claude Code가 Codex(설계·리뷰·진단, read-only)·Gemini(리서치)를 위임 호출하고, Workflow로 다중에이전트 설계 토너먼트·다차원 리뷰·수치 채점을 돌린다. 상세 [`CLAUDE.md`](CLAUDE.md).

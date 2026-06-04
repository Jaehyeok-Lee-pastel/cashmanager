# AI 자연어 가계부 MVP — 최종 설계 (설계 토너먼트 합성안)

> 확정일: 2026-06-02 · 산출: Workflow 설계 토너먼트(3안 생성 → 판정단 3명 → 합성)
> 베이스: "Source-Tagged Ledger"(clean-extensible) + 1안 fast-path + 3안 결정론 선처리 그래프트 → **"2.5안"**

## 판정 요약
- 심판 표결 1-1-1 (mvp-speed→1안 / simplicity→2안 / ai-accuracy→3안)
- **7개 공통 합의(무조건 채택)**: ① bigint KRW 정수원 ② raw_input+parse_meta(jsonb) ③ fast-path 로컬 정규식 ④ handle_new_user 시드 트리거 ⑤ needs_manual 200 폴백 ⑥ config.openai_model SSOT ⑦ profiles.email(seed.sql 정합)
- **유일 논쟁(정정=학습 루프 merchant_category_map)**: MVP 시스템에선 제외, 단 **빈 테이블 + 데이터 수집 훅만** 심어 v2가 "데이터 있는 상태"로 시작하게 절충.

## 데이터 모델 (단일 마이그레이션 `init_ledger.sql`)
- 테이블: `profiles`(id,email,display_name) / `categories`(user별, soft delete archived_at) / `transactions`(단일 ledger) / `merchant_category_map`(v2 예약, MVP 미참조)
- `transactions`: `amount_minor bigint(>0)`, `direction(expense|income)`, `category_id`(set null), `occurred_on date`, `source(tx_source enum: nl_text|manual|receipt|voice|import)`, `raw_input`, `parse_meta jsonb`, updated_at 트리거
- **RLS**: 모든 테이블 단일 for-all `user_id = auth.uid()`. 백엔드는 service_role이므로 service 레이어에서 소유권 재검증(이중 방어).
- 인덱스: `(user_id, occurred_on desc)`, `(user_id, category_id, occurred_on)`, categories partial(`where archived_at is null`)
- 가입 트리거: profile + 한국형 기본 카테고리 12종 자동 시드

## NL 파이프라인 (parse/save 분리, stateless)
1. **결정론 선처리**(`nl_preprocess.py`, LLM 0원, 유닛테스트 강커버): 한글 수사 금액("3만2천","만원","4,900") + 상대날짜("어제","지난주 금요일") KST 파싱
2. **fast-path**: 자명 입력은 LLM 무호출 → 무료 미리보기
3. **LLM 1회**(`openai_service.py`): OpenAI Structured Outputs strict, `settings.openai_model`(gpt-5.4-mini), temp=0, max_tokens≈150. 정적 system 블록(지침+few-shot)으로 prompt caching, 동적 주입(오늘날짜 KST + 사용자 카테고리 enum → 환각/없는 카테고리 차단)
4. **미저장 미리보기 반환** → confidence>=0.8이면 초록 확정 카드(저장 1탭), 아니면 `ambiguous_fields`만 노란 강조 + 칩 1탭 교체. 항상 1탭 confirm(자동저장 X)
5. **폴백**: OpenAI 타임아웃(6s)/에러/스키마 위반 → 422 아닌 **200 + needs_manual:true**(amount는 정규식 결과로 채움) → 같은 카드를 수기 폼으로 재사용. 막다른 길 없음
6. **비용 가드**: mini 고정 / 입력 200자 캡 / 서버 rate-limit / 동일 raw_input 단기 캐시 / parse_meta에 confidence·model·latency 기록(v2 학습 자산)

## API (FastAPI, 라우터 얇게)
- `GET/PATCH /me` · `GET/POST/PATCH/DELETE /categories`(DELETE=soft) · `POST /transactions/parse`(저장X 미리보기) · `GET/POST/PATCH/DELETE /transactions`(month/cursor) · `GET /summary?month=`
- services: nl_service, nl_preprocess, openai_service, tx_service, category_service, summary_service, profile_service
- repositories: tx_repo, category_repo, profile_repo (모든 쿼리 `.eq("user_id", user_id)`)

## 프론트 (React19/TS strict)
- `lib/api.ts` 일원화(+apiPatch/Delete 도메인 래퍼), `lib/supabase.ts`(anon only), `lib/money.ts`(KRW 포맷)
- 핵심: `HomeScreen` 상단 고정 `QuickInputBar`(한 줄 입력) → `ParseConfirmCard`(confidence 분기, 칩 1탭 수정, needs_manual 수기폼 재사용) → 저장 시 낙관적 삽입 + 자동 재포커스(연속 입력)
- `TransactionList/Item/EditSheet`, `CategoryScreen`, `SummaryScreen`+`CategoryChart`(recharts 도넛 1개)
- 상태: 로컬 state + Supabase session (전역 라이브러리 v2), 모든 화면 loading/error/empty 3상태

## 구현 순서 (13단계)
1. DB 마이그레이션 → 2. schemas/repos 골격 → 3. **권한검증 테스트 먼저(RED)** → 4. 카테고리+프로필 슬라이스 → 5. 거래 CRUD(AI 없이도 동작) → 6. NL 결정론 선처리(유닛테스트) → 7. OpenAI 파싱 → 8. 비용/안전 가드 → 9. 프론트 기반 → 10. 핵심 입력 UX → 11. 카테고리 화면 → 12. 월별 요약+차트 → 13. 통합검증·도그푸딩
- 고위험 영역(OpenAI/인증/소유권)은 편집 전 Codex read-only 리뷰 1회 권장

## 열린 질문 (구현 전 사용자 확정 필요)
1. 소셜 로그인 제공자 범위(이메일만 시작 가능)
2. OpenAI 모델/월 호출 상한(circuit breaker) 둘지
3. fast-path 공격성(자명 입력 LLM 생략 vs 항상 category는 LLM)
4. confidence 0.8 / 타임아웃 6s 시작값
5. 수입(income) UX — 같은 리스트 혼합 vs 지출 중심
6. merchant_category_map 빈 테이블을 MVP에 둘지 vs v2로
7. 페이징 — month 단위 단순 로드로 시작 가능 여부
8. 차트 — recharts vs 경량 SVG 직접 구현
9. 한글 금액 수사 커버 범위 fixtures
10. seed.sql 더미 데이터 추가 여부

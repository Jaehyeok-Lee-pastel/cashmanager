## SCORER 1 top=F1
  F1: 40/50 (UV9 DOG9 EASE9 AI4 RET9)
  F2: 38/50 (UV8 DOG8 EASE6 AI9 RET7)
  F3: 37/50 (UV8 DOG7 EASE5 AI9 RET8)
  F4: 35/50 (UV8 DOG7 EASE6 AI7 RET7)
  F5: 27/50 (UV5 DOG7 EASE9 AI2 RET4)
  F6: 31/50 (UV7 DOG8 EASE4 AI6 RET6)
  F7: 21/50 (UV4 DOG6 EASE7 AI1 RET3)
  F8: 27/50 (UV6 DOG5 EASE5 AI4 RET7)

## SCORER 2 top=F1
  F1: 40/50 (UV9 DOG9 EASE9 AI4 RET9)
  F2: 37/50 (UV8 DOG7 EASE6 AI9 RET7)
  F3: 36/50 (UV8 DOG7 EASE5 AI9 RET7)
  F4: 35/50 (UV8 DOG7 EASE6 AI7 RET7)
  F5: 26/50 (UV5 DOG7 EASE9 AI2 RET3)
  F6: 29/50 (UV6 DOG8 EASE4 AI6 RET5)
  F7: 20/50 (UV4 DOG5 EASE7 AI1 RET3)
  F8: 27/50 (UV6 DOG4 EASE6 AI4 RET7)


## RANKING

F1 월 예산 + 카테고리별 진행바 + 초과 경고 — 평균 40/50
  기준: UV9 DOG9 EASE9 AI4 RET9 (양 채점단 동일 40/40)
  판정: 만장일치 1위. 두 채점단 모두 40점 동점 최고. 한국 가계부 최대 미충족 수요(토스 카테고리별 예산 부재)를 정조준하고, 능동 예산(YNAB/엔벨로프)이 수동 추적 대비 lock-in·습관형성이 압도적. 결정타는 ROI: MonthlySummary.by_category(sum_minor 실적)·도넛/진행바 UI·자동분류 QA100%·카테고리관리를 거의 그대로 재사용 → '한도(limit) 값'과 임계 계산만 추가. AI 직접활용만 낮으나(자동 예산제안 정도) 나머지 전 축 최상. 습관루프의 reward 축을 완성해 day30 급락 방어.

F2 AI 자연어 질의 (카페에 얼마 썼어?) — 평균 37.5/50
  기준: UV8 DOG7~8 EASE6 AI9 RET7 (38/37)
  판정: AI 차별화 최강 후보(AI9). 기존 LLM 파싱 파이프라인을 역방향(저장거래→질의/답변)으로 재사용해 핵심 자산과 정합. 도넛/진행바를 답변 시각 컴포넌트로 재사용 시 ROI 상승. 단 cue 부재(능동적으로 물어봐야 열림)로 단독 리텐션 약하고, 환각/정확도 검증 공수가 예산보다 큼. F1 위에 얹어 '예산 왜 초과?'에 답하면 시너지 최대. 2순위·F1 후속 확장으로 권고.

F3 AI 소비 인사이트 + 주간 리포트 + 과소비 알림 — 평균 36.5/50
  기준: UV8 DOG7 EASE5 AI9 RET8~7 (37/36)
  판정: AI 코칭 공백(토스는 '많이 쓴 순서'만) 정조준 + 알림이 핀테크 리텐션 최고 ROI 레버(푸시 open 50~60%). LLM 강점 직접 활용. 단 핵심 함정: 인사이트 단독은 '안다는 느낌'만, 공격적 절감 권고는 6주 내 이탈. F1(예산 임계치)이 있어야 알림 트리거가 의미를 가짐 → F1 의존적. 푸시 인프라+주간 배치+넛지 톤 설계 공수로 EASE 중간. F1 뒤 2순위 패키지.

F4 반복/정기 지출 자동 등록 — 평균 35/50
  기준: UV8 DOG7 EASE6 AI7 RET7 (35/35)
  판정: MyData 불가 제약을 정면 우회 — 카드연동 없이 저장된 거래에서 반복패턴(가맹점·금액·주기) 탐지, merchant_category_map 학습루프 재사용. '구독 같은데 등록할까요?' 제안으로 단순 CRUD 대비 차별화. F3 알림과 결합 시 '결제 임박' cue 시너지. 단 본인 거래량 적으면 초기 탐지 신뢰도 약하고, 다음결제일 스케줄링 공수 중간. 견고한 2순위 묶음.

F6 은행/카드 CSV 가져오기 — 평균 30/50
  기준: UV6~7 DOG8 EASE4 AI6 RET5~6 (31/29)
  판정: 카드 자동연동 못 하는 빈틈을 'CSV+AI 자동분류'로 메우는 전략 후보. 한국 카드사/뱅크샐러드 CSV 추출이 표준이라 현실적이고, CSV 행 자동 카테고리화는 보유 강점이 빛나는 지점. dogfooding 본인 백필에 즉시 효용. 단 파서·필드매핑·중복제거 공수가 가장 큼(EASE4), 일회성 배치형이라 재방문 리텐션 약함. F1/F2보다 뒤.

F8 저축 목표 + 진행 추적 — 평균 27/50
  기준: UV6 DOG4~5 EASE5~6 AI4 RET7 (27/27)
  판정: 게임화/streak의 리텐션 효과는 정량적으로 강함(+22%, +41%). 단 핵심 미스매치: '지출 기록' 앱이라 저축목표는 잔액/이체 데이터 토대 부재(MyData 불가)로 자동 진행계산 소스 빈약 → 또 수동입력. '입력 streak'·'예산달성 streak'으로 변형해야 적합하나 그건 F1의 보강 게임화 레이어. 단독 차기기능으론 토대 부족.

F5 검색 + 필터 — 평균 26.5/50
  기준: UV5 DOG7 EASE9 AI2 RET3~4 (27/26)
  판정: 위생요인(hygiene): 작동하면 당연시, 없으면 불만이나 '가치 높다' 근거 없음. 거래리스트 보유로 클라이언트측 필터는 최저 공수(EASE9). 단 차별화 0·'한 번 보고 마는' 기능이라 재방문 트리거 약함. 자연어 질의(F2)로 흡수하면 격상 가능하나 그건 F2 몫. 데이터 쌓인 뒤 dogfooding 보조기능.

F7 라이트/다크 토글 + 홈위젯 UI 편의 — 평균 20.5/50
  기준: UV4 DOG5~6 EASE7 AI1 RET3 (21/20)
  판정: 최하위. 디자인 토큰·Lucide로 이미 충족한 영역 위 얇은 레이어라 추가 임팩트 최저. AI 차별화 전무, 재방문 트리거 없음, 습관루프와 무관. '있으면 좋은' 미용 기능으로 차기 핵심기능 자격 미달. 여력 생길 때 폴리시.

## RECOMMENDATION
1순위 추천: F1(월 예산 + 카테고리별 진행바 + 초과 경고) — 두 채점단 만장일치 40점, ROI·시장갭·리텐션 전 축 최상이며 보유 자산 재사용으로 신규 인프라 거의 0. 2순위(즉시 후속) 추천: F2(AI 자연어 질의) 또는 F3(AI 코칭/알림) — F1으로 구조화된 예산/실적 데이터 위에 얹어 캐시매니저의 AI 차별화를 살리는 단계적 확장. 권고 로드맵: F1 → (F2 또는 F3). F2는 AI 해자가 더 직접적, F3는 알림 cue로 리텐션 ROI가 더 강함.

## RATIONALE
타이브레이커(ROI + AI 차별화 적합) 기준으로도 F1이 흔들림 없는 1위다. (1) ROI: 코드 확인 결과 budget.ts는 실제로 budget 전용 엔드포인트 없는 범용 API 래퍼이고(D:\\이재혁\\project\\apps\\web\\src\\lib\\budget.ts), types.ts의 MonthlySummary.by_category[].sum_minor가 카테고리별 실적을 이미 제공한다(59,68행). features/summary의 도넛/진행바 UI, categories 라우트·기능, 자동분류 QA100%가 모두 존재해 '한도(limit) 값 + 임계 계산'만 얹으면 되는 최저급 공수가 검증됐다. (2) 시장갭·리텐션: 양 채점단 모두 한국 토스의 대표 미충족(카테고리별 예산 부재)과 능동 예산의 lock-in을 1순위 근거로 독립 수렴, 습관루프의 reward 축으로 day30 리텐션을 직접 방어한다. F1의 유일 약점인 AI 직접활용(AI4)은 차기 F2/F3로 보완되며, 오히려 F1이 만드는 구조화된 예산/실적 데이터가 F2(자연어 질의 답변)·F3(초과 AI 설명/알림)·F4(정기지출 알림)의 토대가 되어 단일 무거운 기능보다 누적 ROI가 높다. F1 채택장벽인 '직접 설정 friction'은 merchant 학습루프 기반 '과거지출 자동 예산제안'으로 보유자산만으로 저공수 우회 가능 — 이 제안은 사실상 AI 강점을 F1에 주입하는 경로이기도 하다.

## STARTPROJECT SCOPE
## /startproject 착수 초안 — F1: 월 예산 + 카테고리별 진행바 + 초과 경고\n\n### 목표\n캐시매니저에 카테고리별 월 예산(한도)을 설정하고, 기존 월요약 진행바에 '실적/한도' 비율을 매핑해 시각적 소진감(엔벨로프)과 초과 경고를 제공한다. 습관루프의 reward 축을 완성해 매일 '한도 남았나' 재방문 동기를 만든다.\n\n### 스코프 (MVP, 인디 1인)\n포함:\n- 카테고리별 월 예산 한도 설정/수정 (category_id + month + limit_minor)\n- 월 시작일(급여일) 옵션은 v1에서 1일 고정, 설정은 후속\n- 기존 도넛/진행바에 실적(sum_minor)/한도(limit_minor) 비율 오버레이 + 임계(예: 80%/100%) 색상·경고 배지\n- '과거지출 기반 예산 자동제안'(직전 N개월 카테고리 평균을 초기 한도로 제안) — friction 제거 핵심, merchant/자동분류 자산 재사용\n제외(후속): 푸시 알림(F3), 자연어 질의(F2), 급여일 커스텀 시작일.\n\n### 핵심 파일\nDB:\n- supabase/migrations/YYYYMMDDhhmm_add_budgets.sql (신규) — category_budgets 테이블: id, user_id(또는 workspace), category_id FK, month(date/text), limit_minor int, created_at. RLS enable + 소유자 policy, (user_id, category_id, month) unique 인덱스. 기존 202606020900_init_ledger.sql는 건드리지 않고 신규 파일로.\n\nBackend (FastAPI):\n- apps/api/app/api/routes/budgets.py (신규) — GET/PUT 예산 (얇게: HTTP·deps만)\n- apps/api/app/services/ (신규 budget 서비스) — 한도 CRUD + 자동제안 계산(과거 N개월 평균)\n- apps/api/app/schemas/ (신규 Pydantic: BudgetCreate/BudgetRead/BudgetSuggestion)\n- apps/api/app/api/routes/summary.py (수정) — 월요약 응답에 카테고리별 limit_minor 조인/병합(또는 별도 budgets 엔드포인트로 프론트 병합)\n\nFrontend (React/TS):\n- apps/web/src/lib/budget.ts (수정) — getBudgets/upsertBudget/getBudgetSuggestion API 래퍼 추가 (URL 흩뿌리기 금지, api.ts 경유)\n- apps/web/src/lib/types.ts (수정) — Budget, CategorySummary에 limit_minor?/over 여부 등 타입 추가\n- apps/web/src/features/summary/ (수정) — 진행바 컴포넌트에 실적/한도 비율·임계 색상·초과 배지\n- apps/web/src/features/ budgets (신규) — 예산 설정 화면 + 자동제안 수락 UI, loading/error/empty 3상태, label/aria-label 접근성\n\n### 검증\n- 권한검증(타 사용자 예산 격리/RLS) → 자동제안 계산 정확도 → 진행바 임계 경계(99%/100%/초과) → 응답 schema. npm run build / typecheck 통과, ruff + py_compile.

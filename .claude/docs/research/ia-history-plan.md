## verdict

사용자 제안(예산·카테고리·설정 → 더보기, 내역 탭 신설)은 2026 트렌드에 부합한다. 단 한 가지 핵심 보정이 필요하다: 현재 5탭에 내역을 그냥 더하면 6탭이 되어 명백한 안티패턴(NN/g·HIG·Material 공통 sweet spot 3~5, 4가 이상적)이다. 따라서 "빼기와 넣기를 동시에" 해서 탭 수를 유지/축소하는 것이 트렌드의 진짜 요구다.

세부 검증:
1) 내역(상세조회) 탭 신설 = 정당. 거래내역 조회는 잔액/요약 다음 2순위 핵심 시나리오이고, Monarch·YNAB·뱅크샐러드 모두 Transactions를 1급으로 둔다. 현재 캐시매니저의 가장 큰 IA 구멍(과거 거래를 월이동/검색/필터로 찾는 1급 진입점 부재)을 정확히 메운다.
2) 카테고리·설정을 overflow로 = 정당. 관리성·저빈도 항목은 overflow 정석. 단 숨김 메뉴는 작업완료율 -21%(NN/g)이므로, 햄버거(좌상단 숨김)가 아니라 라벨이 보이는 하단 "더보기" 탭으로 두는 것이 발견율·thumb-zone·접근성에서 우월(PWA 설치 사용이라 더더욱).
3) 예산은 경계선 항목 = 보정 포인트. 예산은 가계부 핵심 동기라 카테고리/설정보다 빈도가 높다. 완전한 overflow보다 "요약 화면의 예산진행바에서 깊은 예산 화면으로 진입(준-primary)" 또는 더보기 상단 고정이 안전. 본안에서는 더보기에 두되 요약에서도 진입점을 남기는 이중 진입을 권장.
4) 상단 ⚙️설정 처리 = 뱅크샐러드도 설정을 홈 우상단 메뉴에 두므로 현재 상단 ⚙️ 유지가 한국 사용자 멘탈모델에 부합. 다만 IA 일관성을 위해 ⚙️를 제거하고 더보기로 흡수하는 안과, ⚙️ 유지+더보기에는 카테고리/예산만 담아 중복 진입을 피하는 안 두 가지가 가능 → open_questions로 남김.

결론: 제안 방향 채택하되 "4탭 + 중앙 입력 액션" 구성으로 정규화한다.

## nav_primary

권장 IA (본안, 4탭 + 중앙 입력 액션):

순서: [홈] · [내역] · ➕(중앙 입력 FAB/버튼) · [분석] · [더보기]

- 탭 1 홈(구 "기록"): 이번 달 지출 요약 + 최근 거래 + 자연어 입력 dock. 라벨을 "기록"→"홈"으로(탭바 라벨은 동작 동사가 아닌 목적지 명사가 정석, HIG/NN/g). 입력 동작은 dock/FAB로 분리.
- 탭 2 내역(신설): 월이동·검색·카테고리/유형 필터·정렬로 과거 거래 탐색. 홈=이번 달·입력, 내역=과거 탐색/감사로 단일책임 분리.
- 중앙 ➕: 자연어 입력의 단일 최우선 액션. 탭이 아닌 액션 버튼이므로 탭 슬롯을 차지하지 않음(FAB는 Add/Create 단일 액션의 2026 정석). 단 기존 홈 입력 dock이 이미 있으므로, 1차 MVP에서는 ➕를 생략하고 홈 dock 유지 → 순수 4탭([홈][내역][분석][더보기])으로 시작해도 무방. ➕는 "입력을 어느 탭에서나 띄우는" 글로벌 진입이 필요해질 때 후속 추가.
- 탭 3 분석: AI 질의·인사이트(기존 유지, 명사화 OK).
- 탭 4 더보기: 예산·카테고리(·설정) 진입 컨테이너.

요약(도넛·예산진행바) 처리: 별도 탭 폐지 후 (a) 홈 상단 미니 요약으로 흡수 또는 (b) 분석 화면 상단 위젯으로 흡수. 5탭→4탭 압축의 핵심 레버. (현재 SummaryScreen은 폐기 아닌 "홈/분석 내부 섹션"으로 재배치 — 컴포넌트 재사용.)

근거: bottom tab sweet spot 4(상한 5), 빈도 기반 분리(고빈도=primary, 저빈도 관리=overflow), More 탭>햄버거(PWA thumb-zone), 라벨은 명사·icon+label 병행, 입력 동사는 탭바 금지.

대안안(예산 중시): [홈][내역][예산][더보기] — 분석을 더보기 또는 홈 인사이트 섹션으로 흡수. 사용자가 예산을 매우 자주 본다면 채택. 본안은 분석이 AI 차별화 기능이므로 분석을 primary에 둠.

## more_menu

형태: 하단 "더보기" 탭 → 탭하면 풀스크린 라우트(별도 화면)가 아니라 기존 뷰전환 패턴 안에서 "리스트형 메뉴 화면"으로 표시. 바텀시트 대신 뷰전환 리스트를 권장하는 이유: 기존 setView 패턴·토큰 재사용으로 외부 모달/드로어 의존성 0, 각 항목 탭 시 해당 화면(BudgetScreen/CategoryScreen/SettingsScreen)으로 다시 setView. (바텀시트는 후속 폴리시 옵션.)

항목(아이콘 = Lucide, 라벨 한국어):
- 예산 (Wallet/PiggyBank): BudgetScreen 진입. + 요약/홈의 예산진행바에서도 진입(이중 진입, 발견율 보강).
- 카테고리 (Tags): CategoryScreen 진입. 관리성·저빈도 → overflow 정석.
- 설정 (Settings): SettingsScreen 진입. ⚙️ 상단 버튼을 여기로 흡수하거나, 상단 ⚙️ 유지 시 더보기에서는 생략(중복 제거) — open_questions 참조.

더보기 화면 자체 디자인: 단순 리스트(아이콘+라벨+chevron-right), 다크 토큰 재사용, 각 행은 실제 <button> + aria-label. 풀스크린 리스트라 발견율·접근성이 햄버거 드로어보다 우월.

## history_spec

화면명: 내역(HistoryScreen). 책임: 조회 전용(입력·삭제는 홈 책임과 분리, 단 행 탭→상세에서 삭제/수정은 후속).

레이아웃(위→아래):
1) 상단 sticky bar:
   - 월 네비게이터: [◀ 2026년 6월 ▶] — 기존 SummaryScreen의 .month-nav + shiftMonth(money.ts) 그대로 재사용. (좌우 chevron + 월 표시. 휠 피커·캘린더 모달은 후속.)
   - 검색 입력: 메모/원문(raw_input) 텍스트 검색. AI 자연어 입력 특성상 머천트 정규화가 약하므로 memo+raw_input 모두 검색 대상.
   - 필터/유형 컨트롤: 수입/지출 세그먼트 토글 + 카테고리 필터(칩).
2) 활성 필터 칩 row(리스트 직상단, 제거 가능): "무엇으로 좁혔는지" 항상 가시화, 레이아웃 시프트 회피.
3) 날짜 그룹 타임라인: occurred_on 기준 날짜별 섹션, 섹션 헤더 position:sticky(CSS만, 무의존성). 헤더에 그날 지출 합계 표기(가계부 가치↑). 행은 기존 TransactionList 행 디자인 재사용([카테고리 아이콘][메모/머천트]—[카테고리·날짜]—[부호+금액, 수입/지출 색+부호 병기]).
4) 3상태: 스켈레톤 N행(로딩) / 에러 재시도(기존 ThreeState) / 빈 상태 2종 구분 — "이 달엔 거래가 없어요(+추가 유도)" vs "필터 결과 0건(필터 초기화 버튼)".

MVP 범위(1차):
- 월 이동(◀▶) + 월 단위 페이징(기존 listTransactions(month) 그대로 — 월=청크 경계, 가계부 멘탈모델·메모리에 최적).
- 검색(memo+raw_input, 클라이언트 필터).
- 수입/지출 토글 + 카테고리 필터 칩(클라이언트 필터, 다중선택).
- 날짜 그룹 + sticky 헤더 + 일자 합계.
- 정렬: 기본 최신순(occurred_on desc). 금액순은 후속.
- 3상태(스켈레톤/에러/2빈상태).

후속(MVP 제외):
- 행 탭 → 상세 바텀시트(결제수단·메모·수정/삭제, progressive disclosure). 현재 모델에 결제수단 필드 없음 → 후속.
- 월 선택 휠 바텀시트 / 좌우 스와이프 제스처 / 기간 프리셋(Last 30d)·커스텀 date range.
- 금액·머천트 정렬, 가상화(react-window급)·Load more(한 달 거래 과다 시).
- 영수증 링크(현재 source에 receipt 있으나 첨부 저장 미구현).

주의: 검색/필터/정렬은 전부 클라이언트 측(이미 받은 월 단위 transactions 배열 가공)으로 시작 → 신규 API·의존성 0. 한 달 거래가 매우 많아지면 후속에서 서버 쿼리 파라미터로 승격.

## implementation_plan

전제: 기존 setView 뷰전환 패턴·다크 토큰·listTransactions·TransactionList·.month-nav(shiftMonth)·ThreeState/EmptyState 전부 재사용. 신규 npm 의존성 0(sticky 헤더는 CSS position:sticky).

1. apps/web/src/App.tsx — IA 재구성(핵심):
   - View 타입: "home" | "history" | "analysis" | "more" | "budgets" | "categories" | "settings" (summary는 홈/분석 내부로 흡수하며 탭에서 제거).
   - bottom-nav 버튼: 기록→"홈"(라벨 변경, view="home"), "내역"(view="history") 신설, "분석" 유지, "더보기"(view="more") 신설. 예산·카테고리 버튼 제거.
   - main 렌더 분기: history→<HistoryScreen>, more→<MoreScreen>, budgets/categories/settings는 더보기에서 setView로 진입(분기는 유지).
   - 상단 ⚙️: 유지 또는 더보기 흡수(결정 후 반영).

2. apps/web/src/features/more/MoreScreen.tsx — 신규(소형):
   - props: onNavigate(view) 받아 예산/카테고리/설정 행 클릭 시 App의 setView 호출. 단순 리스트(Lucide 아이콘+라벨+ChevronRight), <button>+aria-label.

3. apps/web/src/features/history/HistoryScreen.tsx — 신규(주력):
   - props: { month, onMonthChange }. useTransactions(month) + useCategories 재사용.
   - 상단 .month-nav(SummaryScreen에서 추출 또는 복제), 검색 input, 수입/지출 세그먼트, 카테고리 필터 칩 row.
   - 클라이언트 필터 파이프라인: search(memo|raw_input) → direction → categoryIds. useMemo로.
   - 날짜 그룹핑 헬퍼 + sticky 섹션 헤더(일자 합계). 행은 TransactionList 셀 디자인 재사용(읽기전용 변형 or 기존 컴포넌트에 onDelete 옵셔널화).
   - ThreeState로 로딩/에러/빈상태, 빈상태 2종 분기.

4. apps/web/src/features/history/groupByDate.ts — 신규 헬퍼(타입힌트·단일책임): Transaction[] → {date, sum, items}[] (occurred_on desc).

5. apps/web/src/features/summary/月nav 추출(선택): .month-nav 마크업을 공용 컴포넌트(components/MonthNav.tsx)로 빼서 Summary·History 공유 → 중복 제거. 소규모면 복제도 허용.

6. apps/web/src/features/summary/SummaryScreen.tsx — 탭 제거에 따른 재배치: 컴포넌트는 보존하되 홈 상단 미니요약 또는 분석 상단 위젯으로 호출 위치 이동(도넛/진행바 흡수). MVP에서는 일단 분석 상단에 마운트하거나 별도 진입 보류 가능.

7. styles(전역 css) — .history-*, sticky 헤더, 필터 칩 활성 상태, 세그먼트 토글, 스켈레톤 행. 기존 토큰(--cat-1..8, --color-*, success/danger) 재사용.

품질 게이트: npm run typecheck / npm run build 통과, icon-only 버튼 aria-label, 금액 색+부호 병기, 한글 깨짐 확인. 파일 150~200줄 초과 시 분리(HistoryScreen에서 필터바·리스트 컴포넌트 분리 검토).

순서: (1)App IA 골격+빈 History/More 스텁 → 빌드 통과 확인 → (2)History 필터/그룹핑 → (3)Summary 재배치 → (4)스타일 폴리시.

## open_questions

1. 상단 ⚙️설정 처리: (A) 상단 ⚙️ 유지 + 더보기에는 예산·카테고리만(뱅크샐러드식, 중복 제거) vs (B) ⚙️ 제거 + 더보기로 설정 흡수(상단바 비움, IA 일관성↑). 어느 쪽? (기본 권장: B, 더보기에 설정 통합으로 진입점 단일화.)

2. 중앙 ➕ 입력 FAB 도입 여부: 현재 홈 dock 입력으로 충분한가, 아니면 "어느 탭에서나 입력"이 필요한가? MVP는 홈 dock 유지(순수 4탭)로 시작하고 ➕는 후속 제안. 동의?

3. 요약(도넛·예산진행바) 흡수 위치: 홈 상단 vs 분석 상단? (예산진행바는 예산 진입의 이중 진입점 역할 가능 → 홈 상단이 발견율 유리.)

4. 예산을 더보기 vs 준-primary: 사용자 본인의 예산 화면 사용 빈도는? 매주 여러 번이면 primary 잔류([홈][내역][예산][더보기]) 대안 채택 고려.

5. 내역 검색/필터 클라이언트 처리 한계: 한 달 거래 건수 상한 추정치는? (수백 건까지는 클라이언트 필터 무문제. 수천 건 규모면 서버 쿼리 파라미터로 승격 필요 → 후속.)

6. 행 탭 상세(수정/삭제): 내역 행에서 삭제/수정을 MVP에 넣을지, 조회 전용으로 시작하고 후속에 둘지? (단일책임 관점에선 조회 전용 시작 권장.)


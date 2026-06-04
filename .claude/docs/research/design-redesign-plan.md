## direction_name

"토스의 여백 × 다크 elevation × emerald 성장 시그널" — plain CSS 3계층 토큰만으로 도달하는 2026 모던 핀테크 (의존성은 Pretendard 폰트 1개 + AutoAnimate 3KB만 선별 추가)

## rationale

핵심 판단 3가지.

(1) Tailwind 도입 안 함. 현재 이미 styles.css 단일 파일 + :root 변수 패턴을 쓰고 있어, 토큰화의 핵심 이점(런타임 CSS 변수 기반 디자인 시스템, 무료 다크/라이트 전환)을 plain CSS의 3계층 커스텀 프로퍼티로 100% 동일하게 얻는다. 인디 MVP에서 Tailwind는 빌드 의존성·클래스 폭주·학습비용만 추가하고 효과 중복. 리서치 3개 출처(tailwind v4 / frontendtools / uxpin)와 money-ux·react-styling 양쪽이 같은 결론.

(2) "기본 디자인" 인상의 절반은 토큰 부재에서 온다. 현재 :root에 색 6개뿐, spacing/radius/type/elevation 토큰 0개, 하드코딩 px·hex가 styles.css 전반에 흩어져 있다. 토큰 레이어 1개만 도입하고 기존 하드코딩을 alias로 교체하면 컴포넌트 구조를 1줄도 안 바꾸고 룩이 바뀐다. 이게 비용 대비 효과 1순위라 implementation_plan의 Phase 1로 둔다.

(3) 의존성은 효과가 분명한 2개만. 한글 가독성은 Pretendard Variable(한국 핀테크/정부 표준, CDN @font-face 1줄, woff2 동적 서브셋이라 비용≈0)이 즉효이고 영문·숫자·통화 표기 일관성까지 잡는다 → 채택. TransactionList의 추가/삭제 모션은 AutoAnimate(~3KB, 한 줄 적용)가 Framer Motion(~50KB) 대비 압도적이라 채택. 그 외 모션(탭 전환 crossfade, ParseConfirmCard 등장)은 CSS transition + View Transitions API로 라이브러리 0.

구조 보존 원칙: 모든 화면 컴포넌트 파일명·props·상태 로직은 그대로 두고, className/마크업 보강과 CSS 토큰화 중심으로 개선한다. recharts도 교체하지 않고 props(cornerRadius/paddingAngle/gradient)와 중앙 오버레이만 추가한다.

접근성 반영: 본문은 순백(#fff) 대신 off-white로 할레이션 완화, accent on 다크 대비 4.5:1 확보, 모든 인터랙티브 요소에 :focus-visible, 터치타깃 --tap-target:44px 토큰화(현 nav 14px·버튼 10px 패딩은 44px 미달이라 상향), ambiguous는 색만이 아니라 색+아이콘+텍스트 병행. 라이트모드는 토큰 구조만 잡고 [data-theme=light] 블록은 후속(MVP 우선순위).

## styling_approach

결정: plain CSS 토큰화 유지 (Tailwind 미도입). styles.css 상단을 3계층 토큰 레이어로 재구성하고 컴포넌트 CSS는 semantic alias만 참조한다.

근거: 현 스택이 이미 단일 styles.css + :root 변수라 마이그레이션 비용 0이고, CSS 변수가 곧 디자인 토큰 기반(런타임 테마 전환·단일 진입점)이라 Tailwind의 핵심 이점이 중복된다. 인디 MVP에 Tailwind는 비용>효과.

3계층 구조:
- (1) primitive: raw hex/px. 예) --c-zinc-950:#0B0F19, --c-blue-500:#4f7cff, --c-emerald-500:#10B981, --c-teal-500:#14B8A6, --c-amber-500:#F59E0B, --space-unit 4px 배수.
- (2) semantic alias: --color-bg, --color-surface-1/2/3, --color-border, --color-text-1/2/3, --color-accent, --color-income, --color-expense, --color-warn(ambiguous), --radius-sm/md/lg/full, --space-1~8, --shadow-1/2, --tap-target.
- (3) component(소수만): --confirm-card-bg 등 정말 필요할 때만. 과설계 금지.

새 의존성 (2개, 선별):
- Pretendard Variable (CDN @font-face, woff2 dynamic-subset, 라이선스 무료) — 한글+영문+숫자 통일, 비용≈0.
- @formkit/auto-animate (~3KB) — TransactionList 추가/삭제 모션 한 줄 적용.
미도입: Tailwind, Framer Motion, recharts 대체 라이브러리, react-loading-skeleton(CSS shimmer로 대체).
무라이브러리 기법: View Transitions API(탭 crossfade), CSS transition(카드 등장·버튼 press), div+width% 진행바, position:fixed radial-gradient orb.

## design_tokens

styles.css :root에 추가할 토큰 (다크 = 기본). 라이트는 [data-theme=light]에서 surface/text만 오버라이드 (후속).

=== PRIMITIVE (raw) ===
색 그레이(zinc 계열 elevation):
--c-bg:#0B0F19; --c-surface-1:#161B26; --c-surface-2:#20283A; --c-surface-3:#2A3346;
--c-border:#2A3346; --c-border-soft:rgba(255,255,255,0.07);
--c-text-1:#F4F6FB; --c-text-2:#9BA6BC; --c-text-3:#6B7689;
브랜드/시맨틱:
--c-blue-500:#4f7cff; --c-blue-600:#3d63d8; (accent + hover)
--c-emerald-500:#10B981; --c-teal-500:#14B8A6; (성장/저장 그라데이션)
--c-amber-500:#F59E0B; (ambiguous/주의)
--c-red-500:#F87171; (error)
--c-green-500:#22C55E; (income/positive)
카테고리 팔레트(채도 통일 8색, 인덱스 기반 고정 배정):
--cat-1:#5B8DEF; --cat-2:#34C7A8; --cat-3:#F4B740; --cat-4:#E06C9F;
--cat-5:#9B7BE0; --cat-6:#5BC0DE; --cat-7:#7BC86C; --cat-8:#E8836B;

=== SEMANTIC ALIAS ===
--color-bg:var(--c-bg);
--color-surface-1:var(--c-surface-1);  /* 카드, tx-item, 요약 카드 */
--color-surface-2:var(--c-surface-2);  /* ParseConfirmCard(한 단 띄움), hover */
--color-surface-3:var(--c-surface-3);  /* 바텀시트/모달(후속) */
--color-border:var(--c-border);
--color-hairline:var(--c-border-soft); /* 카드 1px 빛반사 보더 */
--color-text-1:var(--c-text-1); --color-text-2:var(--c-text-2); --color-text-3:var(--c-text-3);
--color-accent:var(--c-blue-500); --color-accent-hover:var(--c-blue-600);
--color-income:var(--c-green-500); --color-expense:var(--c-text-1); /* 지출은 색 빼고 중립 */
--color-warn:var(--c-amber-500);  /* ambiguous */
--color-error:var(--c-red-500);
--grad-growth:linear-gradient(135deg,#10B981,#14B8A6); /* 저장 버튼/긍정 배지 */

=== TYPE SCALE (16px base, ~1.25) ===
--font-sans:'Pretendard Variable',Pretendard,-apple-system,system-ui,sans-serif;
--text-xs:13px; --text-sm:14px; --text-base:16px; --text-lg:20px;
--text-xl:25px; --text-2xl:31px; --text-display:40px; /* 요약 총지출 hero */
--lh-body:1.5; --lh-tight:1.2;
가중치 3단: 400(본문)/600(라벨·금액)/700(헤딩·hero).
금액 클래스 공통: font-variant-numeric:tabular-nums lining-nums; text-align:right;

=== SPACING (4px base) ===
--space-1:4px; --space-2:8px; --space-3:12px; --space-4:16px;
--space-5:20px; --space-6:24px; --space-8:32px;
규칙: 카드 내부 padding var(--space-4~5), 카드 간 gap var(--space-3), 섹션 간 var(--space-6), 화면 좌우 var(--space-5).

=== RADIUS ===
--radius-sm:8px(버튼·입력); --radius-md:12px(tx-item·confirm 필드);
--radius-lg:16px(카드·요약 위젯·바텀시트); --radius-full:9999px(칩·배지).

=== ELEVATION / SHADOW (다크는 표면 명도 + 옅은 그림자 병행) ===
--shadow-1:0 1px 2px rgba(0,0,0,.4);
--shadow-2:0 8px 24px rgba(0,0,0,.45), 0 1px 3px rgba(0,0,0,.3);
카드 분리는 그림자보다 1px var(--color-hairline) 보더 우선.

=== GLASS (탭바·sticky 입력바 한정) ===
--glass-bg:rgba(22,27,38,0.72); --glass-blur:blur(12px);
--glass-border:1px solid rgba(255,255,255,0.08);

=== MOTION ===
--motion-fast:150ms; --motion-base:220ms; --ease-out:cubic-bezier(0.16,1,0.3,1);
버튼 active: transform:scale(0.97). prefers-reduced-motion 가드 필수.

=== A11Y ===
--tap-target:44px; (nav/버튼 min-height·min-width)
--focus-ring:0 0 0 2px var(--color-bg),0 0 0 4px var(--color-accent); (:focus-visible)
safe-area: 탭바 padding-bottom:max(var(--space-2),env(safe-area-inset-bottom)).

=== AMBIENT ORB (홈/요약 배경) ===
body::before radial-gradient(circle at 20% 0%,rgba(79,124,255,0.13),transparent 42%);
body::after radial-gradient(circle at 85% 90%,rgba(20,184,166,0.10),transparent 45%);
position:fixed; filter:blur(80px); pointer-events:none; z-index:-1.

=== FONT (CDN, @font-face 1줄) ===
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@latest/dist/web/variable/pretendardvariable-dynamic-subset.css');

## screen_specs

[로그인 LoginScreen] .auth .card를 surface-1 + --radius-lg + --shadow-2 + 1px hairline으로 떠있게. h1 캐시매니저는 --text-2xl/700, 서브카피 --text-2. 입력 폰트 16px(모바일 줌 방지). 기본 로그인 버튼은 --color-accent, "Google로 계속하기"는 ghost 유지. 배경에 ambient orb 적용. 버튼 min-height:44px.

[홈 HomeScreen] (a) month-header: "{month} 지출" 라벨을 --text-xs/--color-text-3, 금액은 --text-xl/700/tabular-nums anchor로. (b) QuickInputBar(.quick-input): sticky top + glass 표면(--glass-bg+blur)로 승격, placeholder 자연어 예시("예: 점심 김밥 4500원"), 전송 버튼 min 44px·active scale, busy 시 "분석…" 마이크로 상태 유지. 저장 후 입력창 autoFocus 유지(연속 입력). 모바일에선 하단 floating 입력바 검토(엄지존)—선택. (c) 빈 상태: 현 emptyMessage 텍스트를 states.tsx에서 강화—"아직 기록이 없어요" + 큰 이모지 + 예시 칩 3개(탭→QuickInputBar 자동 채움). (d) TransactionList에 AutoAnimate.

[홈 ParseConfirmCard] (a) surface-2로 한 단계 띄워 'confirm 위계' 부여 + --radius-lg + --shadow-2, 등장은 220ms ease-out fade+slide-up. (b) confidence를 상단 작은 배지로 명시: high=emerald "확실", low=amber "AI 추정". 카드 보더색을 high=emerald, low=--color-warn(amber). (c) .ambiguous를 현 빨강(--error,#2a1b1b)에서 amber 토큰으로 변경(파싱 애매=에러 아님) + 경고 아이콘+라벨 병행(색만 구분 금지). (d) needs_manual 마이크로카피 유지하되 톤 보강("카테고리를 추측했어요, 맞나요?"). (e) confirm 버튼 문구 구체화: "저장"→"{formatKRW(amount)} 기록하기", 배경 --grad-growth. 모든 입력/버튼 min 44px.

[TransactionList] 현 텍스트 나열을 머니앱 행 구조로: (a) 좌측 36px 원형 카테고리 칩(배경=해당 카테고리색 12% 틴트, 이모지). 색은 Category에 color 필드가 없으므로 카테고리 인덱스/id 해시→--cat-1~8 결정적 배정(헬퍼 colorForCategory). (b) tx-main 2줄 위계 재배치: 메모(--text-base/600/text-1) 위, 카테고리·날짜(--text-xs/text-3) 아래—현재 카테고리가 위라 역전 수정. (c) tx-amount: tabular-nums + text-align:right + min-width로 우측 끝선 일직선, 지출은 --color-expense(중립), 수입만 --color-income(녹). (d) 행 구분선 1px var(--color-border)(현 #1e293b는 배경과 안 보임). (e) × 버튼 유지(aria-label='삭제', min 44px). 스와이프-투-딜리트+실행취소 토스트는 후속(Phase 4).

[카테고리 CategoryScreen] category-row를 surface-1 카드 톤 + hairline 구분선, 좌측 카테고리색 점(--cat-n). category-form 입력 16px·버튼 44px. emoji-input 64px 유지. 빈 상태 동일 패턴(예시/CTA).

[요약 SummaryScreen] 뱅크샐러드식 bento 위계로 재배치: (1) 최상단 총지출 hero number(--text-display/700/tabular-nums) + "이번 달 총지출" 라벨(--text-xs/text-3) + 전월 대비 증감(있으면) 한 줄 데이터 스토리. (2) summary-totals 두 카드를 surface-1 + --radius-lg, 수입은 --color-income. (3) CategoryChart 도넛 중앙 홀에 총지출 오버레이(절대배치 div, tabular-nums). (4) summary-breakdown 각 행: 카테고리색 점(--cat-n, 차트와 동일색) + 이름 + 금액(tabular-nums) + %(가로 진행바 div+width%로 시각화). (5) 상위 6개+'기타' 묶기는 데이터 가공 후속. month-nav 버튼 min 44px. budget.ts 기반 예산 진행바(녹→amber→적)는 후속.

[CategoryChart] recharts 유지. Pie에 cornerRadius={6}, paddingAngle={3} 추가, COLORS를 --cat-1~8 토큰값과 일치(차트·칩·리스트 점 동일색). <defs> linearGradient(세로, opacity 변주)로 각 Cell gradient(선택). 중앙 총지출 오버레이는 SummaryScreen 측 절대배치 div로.

[하단 네비 bottom-nav] glass 바(--glass-bg+blur+top hairline), 각 탭 min-height:44px, active는 --color-text-1/600 + accent 인디케이터(상단 2px bar 또는 점), 비활성 --color-text-3. safe-area-inset-bottom 패딩. 탭 전환에 View Transitions API crossfade.

[상태 UI states.tsx] (a) Spinner: 텍스트 대신 CSS shimmer 스켈레톤(tx 행 모양, 라이브러리 0). (b) ErrorState: 아이콘+제목 위계 + 재시도 CTA. (c) EmptyState: 이모지+제목+설명+CTA/예시 칩 슬롯(children) 받도록 확장.

## implementation_plan

현 컴포넌트 구조(파일명·props·상태 로직)는 유지하고 CSS 토큰화 + className/마크업 보강 중심. 효과 큰 순서.

Phase 1 — 토큰 기반 (구조 변경 0, 룩 절반 개선)
1. D:/이재혁/project/apps/web/src/styles.css — :root를 3계층 토큰 레이어로 재작성(primitive→semantic→component). 기존 --bg/--card 등 6색을 semantic alias로 매핑, 하드코딩 #334155(4곳)·#475569·#0b1220·#1e293b·#2a1b1b·raw px를 토큰 참조로 전량 교체. spacing/radius/type/elevation/motion/a11y 토큰 추가. body font-family를 Pretendard로. 본문 텍스트 off-white(text-1), 금액 클래스에 tabular-nums, :focus-visible, prefers-reduced-motion, ambient orb(body::before/::after), button active scale, --tap-target 적용. @import Pretendard CDN.
2. D:/이재혁/project/apps/web/index.html — (CDN @import를 styles.css에 넣지 않을 경우) <link> preconnect+Pretendard. 단 @import 1줄로 처리하면 이 단계 생략 가능.

Phase 2 — 컴포넌트 마크업 보강 (구조 유지, className·요소만 추가)
3. D:/이재혁/project/apps/web/src/features/ledger/TransactionList.tsx — 카테고리 칩(원형) 추가, tx-main 2줄 순서 수정(메모↑/카테고리·날짜↓), 금액 className 정리. colorForCategory 헬퍼 호출.
4. D:/이재혁/project/apps/web/src/lib/money.ts — colorForCategory(id|index)→--cat-n 결정적 배정 헬퍼 추가(Category에 color 필드 없으므로). 필요 시 formatKRW 트레일링 처리 검토.
5. D:/이재혁/project/apps/web/src/features/ledger/ParseConfirmCard.tsx — confidence 배지 추가, .ambiguous를 amber+아이콘으로(클래스만), confirm 버튼 문구 "{금액} 기록하기"로, confident 클래스 유지.
6. D:/이재혁/project/apps/web/src/features/summary/SummaryScreen.tsx — hero number 마크업, 도넛 중앙 오버레이 wrapper(position:relative), breakdown 행에 색 점 + 가로 진행바 div 추가.
7. D:/이재혁/project/apps/web/src/features/summary/CategoryChart.tsx — COLORS를 --cat 토큰값과 일치, Pie에 cornerRadius/paddingAngle, (선택)<defs> gradient.
8. D:/이재혁/project/apps/web/src/components/states.tsx — EmptyState에 이모지/제목/CTA·예시칩 slot 확장, Spinner→CSS shimmer 스켈레톤, ErrorState 재시도 CTA.
9. D:/이재혁/project/apps/web/src/features/ledger/HomeScreen.tsx — 빈 상태에 예시 칩(탭→입력 자동 채움) 연결, month-header 위계 클래스.
10. D:/이재혁/project/apps/web/src/features/ledger/QuickInputBar.tsx — sticky/glass 클래스, placeholder 예시, 저장 후 focus 유지.
11. D:/이재혁/project/apps/web/src/App.tsx — bottom-nav glass·active 인디케이터 클래스, 탭 전환 View Transitions(startViewTransition) 래핑.
12. D:/이재혁/project/apps/web/src/features/auth/LoginScreen.tsx, features/categories/CategoryScreen.tsx — 카드/칩/터치타깃 클래스 보강.

Phase 3 — 선별 의존성
13. package.json + TransactionList.tsx — @formkit/auto-animate 설치 후 useAutoAnimate 한 줄.

Phase 4 — 후속(선택, MVP 이후)
14. styles.css [data-theme=light] 블록 + useTheme 훅(localStorage+matchMedia) → 라이트모드.
15. 스와이프-투-딜리트 + 실행취소 토스트(TransactionList + 토스트 컴포넌트).
16. 예산 진행바(budget.ts 연동), 상위6+기타 묶기, 전월 대비 추세.

검증: 각 Phase 후 npm run build(tsc -b && vite build) / npm run typecheck 통과, 한글 깨짐·대비(4.5:1)·44px 터치타깃 확인.

## open_questions

사용자 확정 필요:
1. 기본 테마: 다크 기본 유지(핀테크 다크 선호 강함) + 라이트는 Phase 4 후속으로 OK인가? 아니면 라이트/다크 토글을 초기에 넣을지.
2. Pretendard 도입 승인: CDN @import 방식(간편, 외부 의존) vs 폰트 woff2 셀프호스팅(오프라인/속도). MVP는 CDN 권장.
3. accent 색 정책: 현 블루(#4f7cff, 토스톤 신뢰) 유지 + 긍정 신호에만 emerald→teal 그라데이션 — 이 분리 OK인가? 아니면 브랜드 메인을 emerald로 통일할지.
4. 카테고리 색: Category 타입에 color 필드가 없다. (a) 인덱스/id 해시로 --cat-1~8 결정적 자동 배정(코드만, 마이그레이션 0) vs (b) DB에 color 컬럼 추가해 사용자 지정. MVP는 (a) 권장 — 확정 필요.
5. QuickInputBar 위치: 현 홈 상단 sticky 유지 vs 모바일 하단 floating(엄지존). 후자가 한손 입력 유리하나 레이아웃 변경 동반.
6. AutoAnimate(~3KB) 추가 승인 여부(미승인 시 CSS transition만으로 대체 가능).
7. ParseConfirmCard를 인라인 카드 유지 vs 바텀시트 전환 — 바텀시트는 마찰0 가치에 더 맞지만 마크업 변경 큼(후속 권장). 초기엔 인라인 유지 OK인지.
8. formatKRW 표기: 현 "4,900원" 유지 vs "₩4,900" 전환(리서치는 ₩ 예시). 한국 사용자는 "원"이 친숙 — 유지 권장이나 확인.


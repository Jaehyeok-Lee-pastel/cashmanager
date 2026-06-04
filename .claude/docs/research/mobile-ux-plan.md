# RANKED

1. iOS apple-touch-icon 180x180 PNG (불투명) 교체  [value 9/10, effort low]
  왜: 현재 index.html의 apple-touch-icon이 /icon.svg를 가리켜 iOS가 SVG를 무시하고 기본(흰바탕) 아이콘으로 떨어지는 정확한 원인. 매일 홈화면에서 보는 첫인상이라 '진짜 앱' 체감 ROI가 가장 큼. 공수는 PNG 1장+link 1줄.
  어떻게: icon.svg를 1024로 래스터화 후 180x180 불투명 PNG(다크 배경 #0b0f19 합성, 둥근모서리 X)로 public/apple-touch-icon.png 생성. apps/web/index.html에서 `<link rel="apple-touch-icon" href="/icon.svg">`를 `href="/apple-touch-icon.png"`로 교체. 192/512 PNG도 같이 떠두면 다음 항목에 재사용.

2. 키보드 속성 묶음 — QuickInputBar enterkeyhint/autocorrect/autocapitalize + 금액 inputmode 통일  [value 8/10, effort low]
  왜: 매 기록마다 닿는 핵심 입력. 현재 QuickInputBar는 일반 text라 iOS 자동수정이 '커피 4500'을 망가뜨릴 수 있고 엔터 라벨도 기본값. ParseConfirmCard 금액은 type=number+inputMode=numeric이라 한글/콤마/iOS 키패드 일관성 이슈. JSX 속성만 추가하는 무위험 변경.
  어떻게: QuickInputBar.tsx input에 enterKeyHint="send" autoCapitalize="off" autoCorrect="off" spellCheck={false} 추가. ParseConfirmCard.tsx 금액 input을 type="text" inputMode="decimal"로 변경(type=number 제거해 leading-zero/콤마 이슈 회피). 자연어 input은 text 유지가 정답.

3. 터치 네이티브 감각 묶음 (touch-action/tap-highlight/user-select/callout) 전역 베이스 CSS  [value 8/10, effort low]
  왜: 5탭 네비·기록 버튼·칩 탭 시 회색 하이라이트·300ms 지연·롱프레스 콜아웃 같은 '웹 티'를 한 번에 제거. 매 탭마다 체감되는데 전역 CSS 몇 줄이라 공수 최저. 이미 토큰 시스템이 있어 base 레이어에 얹기 쉬움.
  어떻게: styles.css 베이스에 button,.chip,.bottom-nav button,.icon-btn { touch-action:manipulation; -webkit-tap-highlight-color:transparent; user-select:none; -webkit-touch-callout:none } 추가. input,textarea,.tx-memo 등 텍스트엔 user-select:text; -webkit-touch-callout:default 예외로 복붙 보존.

4. safe-area 토큰화 + 전수 적용 (상단 top-bar/입력바/스낵바까지)  [value 8/10, effort low]
  왜: viewport-fit=cover는 이미 있고 bottom-nav만 부분 적용 상태. black-translucent status bar를 이미 켜둬서 top-bar 콘텐츠가 노치 밑으로 들어가는데 padding-top 보정이 없음 → 현재 노치 겹침 가능성. 토큰화하면 이후 모든 신규 요소가 자동 일관.
  어떻게: styles.css :root에 --safe-top: env(safe-area-inset-top); --safe-bottom: env(safe-area-inset-bottom) 정의. .top-bar에 padding-top: max(var(--space-3), var(--safe-top)); .bottom-nav padding-bottom을 max(var(--space-2), var(--safe-bottom))로. content의 하드코딩 96px도 calc(96px + var(--safe-bottom)) 검토.

5. Android maskable 아이콘 분리 + theme-color 정합  [value 7/10, effort low]
  왜: manifest가 단일 SVG에 'any maskable'을 합쳐둔 정확한 안티패턴(둘 다 어중간). 안드로이드 적응형 마스크에서 로고 잘림. theme-color는 이미 #0b0f19로 잘 잡혀 status bar 정합은 OK라 아이콘만 보강하면 됨.
  어떻게: rank1에서 만든 192/512 any PNG와 별도로 10% safe-zone(중앙 80% 로고)+다크배경 패딩 maskable 192/512 PNG 생성. manifest.webmanifest icons를 any PNG 2개 + purpose:"maskable" PNG 2개로 분리(SVG any 추가 유지 가능). Chrome DevTools>Manifest로 검증.

6. dvh 전환 + interactive-widget=resizes-content (키보드 대응)  [value 7/10, effort low]
  왜: 자연어 입력 PWA의 생명. 100vh 사용처가 키보드/주소창 변화를 못 따라가 입력 시 레이아웃 깨짐. interactive-widget 한 줄로 키보드가 dvh에 반영돼, rank7(하단 입력바)의 키보드 동기화 기반이 됨.
  어떻게: index.html viewport meta에 interactive-widget=resizes-content 추가. styles.css의 .app-shell 등 100vh→100dvh, min-height:100vh→100dvh로 치환. svh/lvh는 필요시 추가.

7. QuickInputBar 하단 고정(채팅형) + 키보드 위 동기화  [value 9/10, effort medium]
  왜: 현재 가장 큰 원핸드 마찰점: 핵심·최빈 액션인 자연어 입력이 상단 sticky(레드존)에 있음. 하단(키보드 바로 위)으로 내리면 엄지존 정석이 되어 매일의 기록 루프 체감이 질적으로 바뀜. value 최상위지만 레이아웃 재배치라 effort medium.
  어떻게: styles.css .quick-input을 position:sticky top→position:fixed bottom:calc(네비높이+safe-bottom), 좌우 0, z-index 네비 위. HomeScreen에서 입력바를 리스트 아래/네비 위 레이어로 이동(JSX 순서는 유지하되 CSS fixed). rank6의 interactive-widget으로 키보드 위 자동 정착, 필요시 visualViewport resize로 bottom 미세보정. 리스트 하단 패딩을 입력바 높이만큼 확보.

8. Undo 스낵바 — 삭제 즉시확인 제거 + 낙관적 저장 보강  [value 8/10, effort medium]
  왜: TransactionList가 이미 낙관적 삭제를 하지만 되돌릴 길이 없어 오삭제 시 손실. 빈도 높고 실수비용 낮은 개인 가계부에 Undo 스낵바가 정석. AutoAnimate 보유로 슬라이드 구현이 가볍고, 외부 의존성 0.
  어떻게: App 또는 HomeScreen 레벨에 Snackbar 컴포넌트(기존 dark surface+accent 토큰) + useSnackbar 훅(3~5초 타이머, 보류 중인 삭제 보관). TransactionList.remove를 onDeleted 후 '실삭제 API 호출 예약'으로 바꿔 Undo 시 prepend 복구. ParseConfirmCard 고신뢰(highConfidence)건은 저장 후 '방금 저장됨 +금액' 스낵바로 피드백.

9. 저장 후 포커스/키보드 유지 — 연속 기록  [value 7/10, effort low]
  왜: '아침에 몰아 3건' 시나리오의 탭 수 급감. 현재 submit이 setText('')만 하고 refocus 안 함 → iOS에서 키보드가 닫혀 다음 입력에 재탭 필요. rank7(하단 입력바)과 결합 시 채팅처럼 연속 타이핑.
  어떻게: QuickInputBar에 inputRef 추가, submit 성공(setText('') 직후) inputRef.current?.focus() 호출, blur 금지. 항상 켜진 autoFocus는 홈 진입 시에만 의미 있으니 유지하되 다른 탭에서 강제 포커스 안 나게 조건부 검토.

10. 고신뢰 파싱 1탭화 — confirm 단계 압축  [value 7/10, effort medium]
  왜: 5초룰 핵심 루프. ParseConfirmCard에 이미 highConfidence(confidence>=0.8 && !needs_manual) 신호가 있음 → 이 경우 확인 카드를 건너뛰고 자동저장+Undo로 '입력+엔터=기록'을 달성. 모호할 때만 카드 노출(점진적 마찰).
  어떻게: HomeScreen onParsed에서 result.confidence>=0.8 && !needs_manual && amount/category 충족 시 ParseConfirmCard 렌더 대신 즉시 createTransaction→prepend→Undo 스낵바. 그 외에는 기존 카드 유지. rank8 스낵바 인프라 재사용.

11. 최근/자주쓰는 항목 칩 1탭 재입력  [value 7/10, effort medium]
  왜: 수동입력 60%+ 절감 가능. 빈 입력 상태에서 '스벅 5000' 칩 1탭 재입력. EXAMPLES 칩 패턴과 chip 토큰이 이미 있어 데이터만 로컬 거래이력 groupBy로 교체하면 됨. 단 빈도집계·정렬 로직 추가라 medium.
  어떻게: useTransactions 데이터로 lib에 recentChips(transactions): {label,raw}[] (memo+amount groupBy, top 5~6). HomeScreen 빈 입력 상태(현 EMPTY EXAMPLES 자리)에 노출, 탭 시 QuickInputBar 값 채우기 또는 즉시 parse. 기존 .chip/.empty-chips 토큰 재사용.

12. 하단 네비 탭타깃 48px화 + 큰 터치타깃 토큰  [value 6/10, effort low]
  왜: 이미 --tap-target:44px라 바닥은 충족. 한 손·이동 중 입력 앱이라 48dp 권장치로 올리고 인접 간격을 토큰화하면 오탭 감소. 변경 폭 작음.
  어떻게: styles.css :root에 --tap-target를 48px로 상향(또는 --tap-target-nav:48px 추가)하고 --tap-gap:8px 토큰화. .bottom-nav button min-height, ParseConfirmCard .actions 버튼, .icon-btn에 일괄 적용. Lucide/× 아이콘 버튼 aria-label 점검(× 삭제는 이미 있음).

13. overscroll-behavior로 pull-to-refresh/바운스 억제  [value 6/10, effort low]
  왜: 매일 쓰는 입력앱에서 실수 새로고침·고무줄 바운스 억제로 앱 느낌 상승. html+body 두 줄. 단 iOS standalone은 완전 제어 안 되는 알려진 한계라 value는 중간.
  어떻게: styles.css html,body { overscroll-behavior:none }. .tx-list 등 내부 스크롤 영역 overscroll-behavior:contain. iOS 잔여 바운스 거슬리면 app-shell fixed+내부 overflow:auto는 공수 상승하니 보류.

14. 햅틱 유틸 (~20줄, navigator.vibrate + iOS 숨김 checkbox)  [value 6/10, effort medium]
  왜: 저장/삭제/확정 시 미세 진동이 네이티브 체감을 올림. 단 iOS Safari는 vibrate 미지원이라 숨김 checkbox 트릭이 필요하고 효과가 미묘. progressive enhancement라 안전하지만 우선순위는 중하.
  어떻게: lib/haptics.ts: navigator.vibrate 있으면 vibrate(10), 없으면 화면밖 1px checkbox 토글(iOS 기본 햅틱). 외부 라이브러리 대신 인라인 ~20줄(무거운 의존성 지양 제약 부합). ParseConfirmCard 저장 성공·TransactionList 삭제에서 호출.

15. 스와이프 액션(좌=삭제/우=수정) + 보이는 버튼 병행  [value 5/10, effort high]
  왜: TransactionList에 즐거운 제스처지만, 2026 원칙상 보이는 버튼을 대체 못하고 보완만 가능 → 이미 × 버튼이 있어 한계효용이 낮음. 무라이브러리 자작 시 터치 추적·iOS 좌엣지 뒤로가기 충돌 회피가 까다로워 effort high. rank8 Undo가 삭제 UX를 이미 해결하므로 후순위.
  어떻게: 별도 라이브러리 없이 pointer 이벤트로 translateX 추적, 임계값 넘으면 삭제(빨강+휴지통)/수정 노출. 좌측 엣지 시작점 제외로 PWA 뒤로가기 충돌 회피. 우측 … 메뉴 버튼 병행 유지. 비용 대비 가치 낮아 tier 밖.

16. 카테고리/날짜 선택 바텀시트 (자작 fixed+translateY)  [value 5/10, effort high]
  왜: ParseConfirmCard의 select(카테고리)/date input은 OS 기본 피커로 이미 한 손 조작 가능 → 자작 바텀시트의 한계효용이 낮음. detent·드래그핸들·접근성까지 제대로 하려면 공수 큼. 진짜 가치는 거래 상세/수정 화면이 생길 때.
  어떻게: 필요해지면 fixed+transform translateY+AutoAnimate로 단일 detent부터, 순수 CSS 드래그핸들, 임계값 닫기. 지금 OS 기본 피커로 충분하므로 보류.

17. iOS 스플래시 (apple-touch-startup-image 생성기)  [value 4/10, effort medium]
  왜: 흰 깜빡임 제거는 좋지만 기기/방향 조합 25+장 생성+meta 주입이라 1인 운영부담. 빌드 1회성이나 가치 대비 우선순위 낮음. 아이콘(rank1)부터 끝낸 뒤 여유 시.
  어떻게: npx pwa-asset-generator로 logo+다크배경 → public/splash/*.png + head link 묶음 생성해 index.html에 주입. 1회성.

18. standalone 감지 → 설치 배너 분기  [value 4/10, effort low]
  왜: 공수는 낮으나, 매일 쓰는 1인이 이미 standalone 설치 완료 상태라 설치 유도 UI 자체의 실익이 거의 없음. 군더더기 제거 효과만 미미.
  어떻게: lib/useStandalone.ts (matchMedia('(display-mode: standalone)') OR iOS navigator.standalone). 설치 안내 컴포넌트가 생길 때만 미설치 분기. 지금은 불필요.

19. 자체 음성입력(Web Speech) 버튼  [value 3/10, effort low]
  왜: 함정 항목: standalone iOS WebKit에서 SpeechRecognition이 조용히 실패. 직접 마이크 버튼은 오히려 신뢰를 깸. 가치는 placeholder 한 줄 수정뿐.
  어떻게: 자체 버튼 금지. QuickInputBar placeholder를 음성친화 문구('말하거나 입력: 어제 김밥 4500')로 바꿔 iOS 키보드 받아쓰기 유도. 자체 Web Speech는 if('SpeechRecognition' in window) 가드로 안드로이드 한정 PE만.

20. 중앙 FAB(+) 추가  [value 3/10, effort low]
  왜: 앱의 단일 주요 액션이 '입력'이고 rank7로 하단 입력바를 항상 띄우면 별도 FAB는 중복. 다른 탭에서의 빠른 기록 점프 정도만 실익이라 가치 낮음.
  어떻게: 굳이 한다면 다른 탭에서만 하단-중앙 +버튼→home 탭+QuickInputBar 포커스 점프. 우상단 배치는 레드존이라 금지. 사실상 skip 권장.

## tier1
지금 바로(높은가치×저공수, 거의 무위험 — 하루 안에 일괄): rank1 apple-touch-icon PNG 교체(현재 iOS 기본아이콘 증상 직접 해결), rank2 키보드 속성 묶음(enterkeyhint/autocorrect off + 금액 inputmode=decimal), rank3 터치 네이티브 감각 전역 CSS(탭 하이라이트/300ms지연/콜아웃 제거), rank4 safe-area 토큰화+상단까지 전수 적용, rank6 dvh 전환+interactive-widget=resizes-content. 추가로 rank5 maskable 아이콘 분리(rank1에서 PNG 같이 떠두면 거의 공짜). 이 묶음만으로 '진짜 앱' 체감이 크게 오르고 라이브 로직 변경이 거의 없음.

## tier2
그다음(원핸드·빠른기록 루프의 질적 개선 — 약간의 로직/레이아웃 변경): rank7 QuickInputBar 하단 고정(채팅형, tier1의 dvh/interactive-widget 위에 얹기), rank9 저장 후 포커스 유지(연속 기록), rank8 Undo 스낵바(낙관적 삭제 복구), rank10 고신뢰 파싱 1탭 자동저장(rank8 스낵바 인프라 재사용), rank11 최근/자주쓰는 칩, rank12 네비 48px화, rank13 overscroll-behavior. rank7~10은 서로 시너지(채팅형 입력+연속 포커스+1탭 저장+Undo가 하나의 매끄러운 루프).

## skip
지금은 보류/생략: rank14 햅틱(iOS 미지원·효과 미묘, 여유 시), rank15 스와이프 삭제/수정(이미 × 버튼+Undo로 해결돼 한계효용 낮고 자작 공수 high), rank16 자작 바텀시트(OS 기본 select/date 피커로 충분, 거래 상세 화면 생기면 재검토), rank17 iOS 스플래시(25+장 생성 부담), rank18 standalone 분기(이미 설치 완료라 실익 없음), rank19 자체 음성입력(standalone iOS에서 조용히 실패하는 함정 — placeholder 유도로만), rank20 중앙 FAB(하단 입력바와 중복). 핵심: 인디 1인이면 tier1 무위험 묶음을 먼저 끝내고, tier2에서 '하단 입력바+연속 포커스+1탭 저장+Undo' 루프 하나에 집중. 제스처/시트/스플래시류는 가치 대비 공수가 커서 후순위.

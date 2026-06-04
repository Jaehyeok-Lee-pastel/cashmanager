# 캐시매니저 — 프로젝트 현황 & 의사결정 로그

> 최종 갱신: 2026-06-04 · 한곳에서 보는 진행 상황·결정·근거. 상세 근거는 `.claude/docs/research/`.

## 1. 한 줄 요약
AI 자연어 한 줄 입력 개인 가계부 MVP. **작동함 · 개인/지인 사용 가능 · 공개 출시는 미흡.**

## 2. 빌드된 기능 (완료)
- 자연어 입력→LLM 파싱(Structured Outputs)→1탭 confirm→저장
- 결정론 선처리(한글 금액 수사·상대날짜) + fast-path + 학습루프(merchant_category_map)
- 카테고리(12종 시드, Lucide 아이콘, CRUD)
- 월 요약(도넛+중앙총액+카테고리 진행바+수입/잔액, 상위6+기타 그룹핑)
- 월 예산(카테고리 한도, 3개월 평균 자동제안, 임계색·초과배지)
- AI 분석(자연어 질의 + 규칙기반 인사이트 카드 + AI 코치)
- 인증(Supabase Auth), 디자인 토큰 시스템·다크 톤·반응형
- **PWA**(홈화면 설치 → 앱처럼 실행, 새 의존성 0)
- 품질: 분류 QA 176케이스 **100%**, 백엔드 pytest **57 통과**, web build/typecheck 통과
- **GitHub**: https://github.com/Jaehyeok-Lee-pastel/cashmanager (커밋·푸시 완료, 시크릿 제외)

## 3. 현재 수준 점검 (자체 평가, /10)
| 영역 | 점수 | 메모 |
|---|---|---|
| 핵심 기능 완성도 | 8.5 | 한 사이클 전부 동작 |
| 코드 품질 | 8 | 레이어 분리·RLS·테스트·Codex 리뷰 |
| 디자인/UX | 7.5 | 토큰·아이콘·반응형 |
| 출시 준비도(배포/운영) | 2.5 | localhost 수동기동, 호스팅·모니터링·비용가드 없음 |
| 시장성(리텐션/차별화 검증) | 3.5 | AI입력은 차별점이나 리텐션 미검증, 자동연동 못 이김 |
| 운영 안정성/보안 하드닝 | 4 | 기본 인증·rate-limit 있음, 공개 수준 미달 |

**단계**: 작동하는 개인용 MVP(알파) → (배포+친구베타) → 공개베타.

## 4. 시장성 판단 (정직한 결론)
- **일반 소비자 상업 제품으로는 승산 낮음(~3/10)**: MyData 불가로 핵심 편의(자동연동)를 못 줌, 수동입력 리텐션 약점, 무료 슈퍼앱(토스/뱅샐) 우위, 소비자 지불의향 낮음.
- **그러나 가치 있는 곳**: 본인 실사용(높음), 지인 공유(높음), **포트폴리오/실력 증명(매우 높음)**.
- **권고**: 상업화 판단은 보류. 지인 베타를 **공짜 리텐션 테스트**로 써서 "2주 뒤에도 쓰는 니치가 있는가"만 싸게 확인 → 데이터가 결정하게.

## 5. 의사결정 로그 (수치 근거)
| 결정 | 결과 | 근거 문서 |
|---|---|---|
| 제품 컨셉 | AI 자연어 가계부, "입력 마찰 0" | `research/product-brief-budget-app.md` |
| 경쟁 분석 | OCR 자체는 레드오션, 자동연동 강세 | `research/budget-app-competitors.md` |
| MVP 설계 | 단일 ledger + source enum 등 "2.5안" | `research/mvp-design-final.md` |
| 디자인 리디자인 | plain CSS 토큰 시스템(Tailwind 미도입) | `research/design-redesign-plan.md` |
| 폴리시 vs v2 | **D 하이브리드**(반응형 보정 후 v2) 42/50 | `research/next-step-decision.md` |
| 영수증 OCR v2 | **보류** CONDITIONAL 23.5/60 | `research/v2-receipt-ocr-validation.md` |
| 차기 기능 발굴 | **F1 월예산** 1위 40/50 → F2/F3 | `research/feature-discovery-ranking.md` |

## 6. 알려진 갭 / 다음 후보
- **비용/남용 방어**: OpenAI per-user 일일 한도·서킷브레이커
- **리텐션 장치**: 푸시 알림(ROI 1등 레버, 미구현)
- **신뢰성**: 에러 모니터링·로깅·백업
- **검증**: 지인 5~10명 2~4주 리텐션 실측
- 보류: 영수증 OCR(조건부 GO는 "카드연동 마트거래 품목 enrichment"로 극단 축소 시)

### 예정(backlog) — 만들지 않고 보류로 결정한 것
- **내역 날짜 "범위/프리셋" 필터(최근 7/30일·커스텀 기간)** — *예정/보류*. 현재는 월 이동 + 단일 일자 필터로 충분(개인 월단위 사용). 트렌드(프리셋+커스텀)상 가치는 있으나, 달을 넘는 범위는 백엔드 `GET /transactions?from=&to=` 신규 파라미터가 필요해 ROI 대비 보류. "여행기간·최근 30일을 자주 본다"는 실수요 생기면 그때 백엔드 from/to + 프리셋 UI로 구현. (근거: `research/ia-history-plan.md` 후속 항목, 2026 date-filter 트렌드 = 프리셋 우선·커스텀은 탈출구)

## 7. 권장 다음 순서
1. **배포** — 폰에서 PWA로 실제 사용 가능하게 ([`DEPLOYMENT.md`](DEPLOYMENT.md): Vercel+Render+Supabase, 무료~소액) ← **다음 관문**
2. 사용량/리텐션 로깅 + 비용 가드 → 3. 포트폴리오 정리(스크린샷·데모)
- 상업화는 지인 베타 리텐션이 긍정 신호일 때만 escalate.

## 8. 문서 맵
- [`README.md`](../README.md) — 제품·실행 · [`CASE_STUDY.md`](CASE_STUDY.md) — 결정·배운점 · [`DEPLOYMENT.md`](DEPLOYMENT.md) — 배포
- `.claude/docs/research/` — 수치 검증 근거 7건(경쟁분석·OCR검증·기능발굴·결정문서)

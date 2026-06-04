# CONFIRMED (33)

[high] GET /insights가 rate_limit_parse 의존성 없이 매 호출마다 LLM(_coach_line)을 호출함 — AI 토큰 비용 제어 (LLM Cost Control)

[medium] rate_limit_parse가 인메모리 단일 딕셔너리 — 재시작 시 초기화, user_id 기반이므로 토큰 탈취 시 우회 가능 — AI 토큰 비용 제어 / Rate Limiting

[medium] JWT 검증에 issuer(iss) 클레임 검증 없음 — 인증 (Authentication)

[high] 서비스워커가 같은 origin의 API GET 응답을 캐시하여 인증 정보가 노출될 수 있음 — PWA 서비스워커 / 데이터 노출 (Service Worker)

[low] month 파라미터 포맷 검증 없음 — 잘못된 입력이 DB 오류를 외부 노출할 수 있음 — 입력 검증 / 정보 노출 (Input Validation)

[low] FastAPI 기본 예외 핸들러가 /docs, /redoc, /openapi.json을 프로덕션에서 노출 — 보안 설정 (Security Configuration)

[low] GET /health가 app_env 값을 외부에 노출 — 정보 노출 (Information Disclosure)

[low] 어시스턴트 사용자 질문이 LLM 프롬프트에 직접 삽입 — 프롬프트 인젝션 부분 완화만 존재 — AI 보안 / 프롬프트 인젝션 (Prompt Injection)

[medium] supabase_jwt_secret 미설정 시 경고 없이 원격 폴백만 사용 — 보안 설정 (Security Configuration)

[high] 서비스 워커가 단일 Origin API의 금융 데이터 응답을 디바이스에 캐시 — PWA 서비스 워커 / 데이터 프라이버시

[medium] 프로덕션 환경에서 FastAPI /docs, /redoc, /openapi.json 공개 노출 — 정보 노출 / API 문서

[high] GET /insights가 rate_limit 없이 매 요청마다 LLM을 무조건 호출 — AI 토큰 비용 / 남용 방지

[medium] 인메모리 rate limiter가 프로세스 재시작/재배포 시 완전 초기화 — rate limiting / 남용 방지

[low] CORS allow_methods=["*"] + allow_headers=["*"] 과도한 허용 — CORS 설정

[high] .gitignore가 .env.production, .env.test 등 변형 파일을 명시적으로 제외하지 않음 — 시크릿 관리 / .gitignore

[low] supabase.py의 get_supabase()가 FastAPI 컨텍스트 외부에서 HTTPException 발생 — 예외 처리 / 서비스 레이어 설계

[medium] 보안 HTTP 응답 헤더 전체 누락 (CSP, HSTS, X-Frame-Options 등) — 보안 헤더 / HTTP 설정

[low] api.ts의 authHeaders()가 token 미전달 시 조용히 인증 헤더를 생략 — 프론트엔드 인증 / API 클라이언트

[medium] assistant_service: 사용자 입력(question)이 프롬프트에 구조적 분리 없이 삽입됨 (프롬프트 인젝션) — 프롬프트 인젝션

[medium] insights_service._coach_line: 카테고리명(사용자 입력 유래)이 프롬프트에 검증 없이 삽입됨 — 프롬프트 인젝션

[medium] GET /insights의 LLM 코치 호출에 per-request rate limit 없음 — AI 토큰 과소비 — AI 토큰 비용 통제 / Rate Limiting

[medium] rate_limit_parse: 인메모리 저장소 — 재시작 시 초기화, 멀티 인스턴스 환경에서 우회 가능 — Rate Limiting

[low] TransactionCreate.parse_meta: 임의 dict 허용 — 사용자가 내부 메타데이터를 임의 조작하여 DB에 저장 가능 — 입력 검증

[low] GET /insights: month 쿼리 파라미터에 형식 검증 없음 — 잘못된 입력이 month_bounds()까지 전달됨 — 입력 검증

[low] ProfileUpdate.display_name: 길이 제한 없음 — 입력 검증

[medium] supabase.py의 get_supabase(): HTTPException을 lru_cache 내부에서 발생 — 잘못 캐시된 예외 상태 — 보안 설정 / 예외 처리

[high] GET /insights 엔드포인트에 rate limit 미적용 — 무제한 LLM 호출 가능 — AI 비용·남용 통제

[medium] 인메모리 rate limiter — 재시작 시 카운터 리셋, 다중 인스턴스 간 미공유 — AI 비용·남용 통제

[medium] 일일/월 총량 캡 부재 — 분당 20회 * 60분 * 24시간 = 하루 28,800 LLM 호출 가능 — AI 비용·남용 통제

[medium] /transactions/parse와 /assistant/query가 동일한 rate_limit_parse 버킷 공유 — AI 비용·남용 통제

[medium] 서비스워커가 단일서비스 배포에서 API GET 응답을 stale-while-revalidate로 캐시 — 보안·데이터 정합성

[low] insights_service.py: _coach_line에 LLM 호출 캐시 없음 — 동일 데이터로 매 로드마다 청구 — AI 비용 최적화

[info] openai_service.py: complete() 기본 max_tokens=300, prompt cache 불가 구조 명시 — AI 비용 최적화


## overall
전반적으로 이 앱은 인디 1인 MVP 치고는 보안 기초가 견고하다. 전 테이블 RLS + service-layer 소유권 재검증 + DB 트리거의 다층 방어, 로컬 HS256 JWT 검증(exp/sub require) + 원격 폴백, 시크릿 백엔드 격리(.env gitignore), 자연어 200자 캡 + max_completion_tokens 제한 + max_retries=0 + 인메모리 rate limit + LLM 호출의 best-effort try/except 등 핵심 통제는 이미 들어가 있다. 인증·인가·SQL 인젝션 측면의 치명적 구멍은 발견되지 않았다.

가장 심각한 문제는 두 가지다. (1) AI 비용 통제: GET /insights가 rate_limit 없이 매 호출마다 OpenAI를 부르는데(_coach_line) 캐시도 일일 총량 캡도 없어, 유효 JWT를 가진 사용자가 새로고침/스크립트만으로 무제한 토큰 비용을 유발할 수 있다. 분당 캡(20회)이 있는 /parse·/assistant조차 이론상 하루 28,800회까지 열려 있다. 인디 1인에게 이건 보안 사고가 아니라 직접적인 청구서 폭탄이라 최우선이다. (2) 데이터 프라이버시: 단일 origin 배포에서 서비스워커의 `url.origin !== self.location.origin` 패스스루 조건이 무력화되어, /transactions·/summary·/insights 등 개인 금융 데이터 API 응답이 브라우저 Cache Storage에 평문 저장된다. 공용·가족 공유 PC에서 로그아웃 후에도 이전 사용자 데이터가 남는다. 둘 다 확정 결함이며 둘 다 즉시 수정 가능하다.

## confirmed_findings
소스 직접 확인 완료. 심각도순.

[HIGH-1] GET /insights 무제한 LLM 호출 (비용)
- insights.py:10-12 — 라우터에 rate_limit 의존성 없음(확인). insights_service.py:60,80 — get_insights()가 매번 _coach_line() → openai_service.complete(max_tokens=80) 호출(확인). /parse·/assistant는 rate_limit_parse 있는데 /insights만 무방비.
- 수정: 즉시 `dependencies=[Depends(rate_limit_parse)]` 추가 + 중기적으로 _coach_line 결과를 (user_id, month, summary_hash) 키로 TTL 캐시(인메모리 1시간)하여 동일 month 재로드 시 LLM 미호출.

[HIGH-2] 서비스워커가 단일 origin API 금융 응답 캐시 (데이터 노출)
- sw.js:12 — `if (url.origin !== self.location.origin) return;`(확인). 단일서비스라 API도 same-origin → 조건 무력 → line 15-26 stale-while-revalidate가 모든 GET 응답을 cashmanager-v1 캐시에 평문 저장. main.py:56-61 SPA 폴백이 same-origin 확정.
- 영향: 공용/가족 PC에서 로그아웃 후 Cache Storage(DevTools 열람 가능)에 이전 사용자 거래·예산·인사이트 잔존. 추가로 stale 데이터 정합성 문제(거래 추가 후 미반영).
- 수정: API pathname prefix(/transactions,/summary,/insights,/budgets,/categories,/assistant,/me) early-return(network-only). + 백엔드 미들웨어로 동일 prefix에 `Cache-Control: no-store`.

[MEDIUM-1] 일일/월 총량 캡 부재 (비용)
- ratelimit.py:15-16 — _WINDOW_SECONDS=60, _MAX_PER_WINDOW=20만 존재(확인). 분당 캡뿐이라 한 사용자가 하루 28,800회 가능. /assistant는 max_tokens=300 + 3개월 컨텍스트(assistant_service.py:10,22)라 호출당 비용이 크다.
- 수정: _check에 _day_hits 레이어 추가(예: _MAX_PER_DAY=200). 분당 통과 후 일일 캡도 검사.

[MEDIUM-2] 엔드포인트가 동일 rate_limit_parse 버킷 공유 (비용/UX)
- assistant.py:5,12 / transactions.py:5,17 — 둘 다 같은 rate_limit_parse 사용(확인). /parse 20회 쓰면 /assistant 막힘. 비용 비대칭(parse 150 vs assistant 300 토큰)인데 동일 제한.
- 수정: limiter 팩토리로 분리 — parse 20, assistant 10, insights 5/분.

[MEDIUM-3] 인메모리 rate limiter — 재시작 초기화 + 멀티인스턴스 우회 + 메모리 누수 (비용/남용)
- ratelimit.py:18 — 모듈 전역 defaultdict(확인). Railway 재배포/OOM/healthcheck 재시작마다 리셋. 수평확장 시 인스턴스별 분리되어 N배 허용. 만료 엔트리 GC 없어 비활성 user deque 누적.
- 수정(MVP 단일인스턴스): _check에서 빈 deque del로 누수 방지. 재시작 내성 필요 시 Supabase rate_limit_hits 테이블 또는 Upstash Redis.

[MEDIUM-4] JWT issuer(iss) 검증 없음 (인증)
- deps.py:24-29 — audience="authenticated"는 검증하나 issuer 미검증(확인). 동일 HS256 시크릿 공유 토큰이 올바른 sub/exp만 있으면 통과 가능.
- 수정: jwt.decode에 `issuer=f"{settings.supabase_url}/auth/v1"` + require에 "iss" 추가. config.py:12 supabase_url 이미 존재.

[MEDIUM-5] supabase_jwt_secret 미설정 시 조용히 원격 폴백 전용 (보안 설정)
- config.py:14 빈 기본값(확인) + deps.py:22 if 분기 — 시크릿 없으면 require[exp,sub] 검증 생략하고 매 요청 원격 get_user에 의존(가용성·레이턴시 리스크). 조용히 동작.
- 수정: 기동 시 warning 로그 또는 production에서 미설정이면 fail-fast.

[MEDIUM-6] 보안 응답 헤더 전무 (HTTP 설정)
- main.py 전체 — HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, CSP 모두 없음(확인). 금융 앱인데 클릭재킹/MIME 스니핑 무방비.
- 수정: SecurityHeadersMiddleware 추가(nosniff, DENY, HSTS, strict-origin-when-cross-origin).

[MEDIUM-7] /docs·/redoc·/openapi.json 프로덕션 공개 (정보 노출)
- main.py:21 — docs/redoc/openapi url 미지정 → 기본 공개(확인). 전체 API 스펙·금융 스키마 무인증 열람.
- 수정: production이면 세 url 모두 None.

[MEDIUM-8] 프롬프트 인젝션 — user question / 카테고리명 구조 분리 없음 (AI 보안)
- assistant_service.py:20 — question이 user_msg에 `=== 질문 ===` 구분자로 인라인(확인). 사용자가 구분자 문자열·지시문 삽입 가능. insights_service.py:72,78 — 사용자 생성 카테고리명(c.name)이 facts/over로 LLM에 삽입(확인). system 메타지시("데이터는 지시 아님")로 부분 완화뿐.
- 영향 한정: 응답이 본인에게만 반환 → 타 사용자 무영향. 단 토큰 낭비·동작 변경 가능.
- 수정: question을 별도 user turn으로 분리, context는 system으로. 카테고리명 따옴표 래핑.

[LOW] 그 외(영향 작음, 위생 차원):
- .gitignore:8-10 — `.env.production`/`.env.staging`/`apps/**/.env` 미커버(확인). `.env.*` + 예외 패턴 추가 권장.
- health.py:10-14 — app_env·service명 무인증 노출(확인). `{"ok": True}`로 축소.
- transactions month 파라미터 등 YYYY-MM 형식 검증 없음 → 잘못된 입력이 month_bounds()로 직행, 500 가능. Annotated regex 검증.
- supabase.py:16-19 — get_supabase()가 서비스 레이어에서 HTTPException raise + "credentials not configured" 내부정보 노출(확인). 일반 메시지로.
- transaction parse_meta: dict 무제약(클라이언트가 confidence/route 위조 가능) → 서버에서 덮어쓰거나 typed schema.
- CORS allow_methods/headers=["*"](main.py:27-28) → 필요 메서드·헤더로 좁히기.
- ProfileUpdate.display_name 길이 제한 없음 → Field(max_length=50).
- api.ts authHeaders token optional → 인증 함수 token required 분리.

[INFO] openai_service.py:18-21 주석 — system prompt가 ~1024토큰 캐시 임계 미달이라 prompt-cache 미적용 자인. 근본 대책은 중복 호출 제거(coach 캐시).

## cost_control_plan
인디 1인에게 AI 비용은 보안보다 직접적 손실이므로 우선순위 최상. 단계별로.

[1순위 — 오늘, 출혈 차단]
(a) GET /insights에 `dependencies=[Depends(rate_limit_parse)]` 추가. 단 한 줄, 가장 큰 누수 막음.
(b) _coach_line 결과 인메모리 캐시: 키 = (user_id, month) 또는 facts+over 해시, TTL 1시간. summary 안 바뀌면 LLM 재호출 0. 인사이트 페이지 새로고침·폴링 비용 제거. insights_service.py 내 dict 캐시 + 만료 엔트리 정리로 충분(MVP 단일 인스턴스).

[2순위 — 이번 주, 총량 상한]
(c) ratelimit.py에 일일 캡 레이어(_MAX_PER_DAY, 예: 200) 추가. 분당+일일 2단 방어로 28,800회 이론치를 사업 현실치로 제한.
(d) limiter 팩토리로 엔드포인트별 분리: parse 20/분, assistant 10/분(토큰 2배니까 더 보수적), insights 5/분. 한 엔드포인트 소진이 다른 기능 막는 UX 문제도 동시 해결.
(e) 코드 외 안전망(필수): OpenAI 계정 Usage Limits에 월 hard limit + soft 알림 설정. 코드 버그가 있어도 청구 상한이 물리적으로 막힘. 1인 운영에 가장 가성비 높은 한 줄.

[3순위 — 재시작 내성/스케일 대비, 필요해질 때]
(f) Railway 단일 인스턴스 유지(수평확장 금지)면 인메모리로 충분. 재배포 빈도가 잦아 우회가 실측되면 Supabase rate_limit_hits 테이블(user_id, window_start, count)로 이전. Redis(Upstash)는 트래픽 늘면.
(g) max_tokens 재점검: assistant complete 기본 300 → 단문 답변이면 200으로. insights coach 80은 적절. parse 150 적절. 입력측은 assistant _CONTEXT_MONTHS=3이 토큰 비용 주원인 — 카테고리 상위 N개만 컨텍스트에 넣어 입력 토큰 축소 검토.

[모니터링]
(h) parse_meta의 latency_ms·model은 이미 기록 중 — 여기에 호출 카운트/일자를 더해 user별 LLM 호출 수를 주기적으로 보면 남용 사용자 조기 탐지 가능.

핵심: rate limit은 "남용 방지"이고, 캐시 + OpenAI 계정 hard limit이 "비용 상한"이다. 둘 다 있어야 안심. 특히 (e) 계정 hard limit은 모든 코드 결함의 최종 방어선이라 1순위와 함께 즉시 설정 권장.

## quick_wins
지금 바로(각 1-5분, 저공수·고효과):

1. [비용 최대효과] insights.py:10 — `@router.get("/insights", response_model=list[InsightCard], dependencies=[Depends(rate_limit_parse)])` + 상단 `from app.core.ratelimit import rate_limit_parse`. 한 줄로 최대 누수 차단.

2. [프라이버시 최대효과] sw.js — fetch 핸들러 상단에 same-origin API prefix early-return:
   `const API=["/transactions","/summary","/insights","/budgets","/categories","/assistant","/me"]; if(API.some(p=>url.pathname.startsWith(p))) return;`
   (origin 체크보다 먼저). 금융 데이터 디스크 캐싱 즉시 중단. + 캐시 버전 bump(cashmanager-v1→v2)로 기존 캐시 무효화.

3. [비용 상한 — 코드 무관] OpenAI 계정 대시보드에서 월 hard usage limit + 알림 설정. 모든 코드 결함의 최종 방어선.

4. [인증 강화] deps.py:24-29 jwt.decode에 `issuer=f"{settings.supabase_url}/auth/v1"` + options require에 "iss" 추가. 설정 추가 불필요(supabase_url 이미 존재).

5. [정보 노출] main.py:21 — production이면 docs_url/redoc_url/openapi_url=None. health.py는 `{"ok": True}`로 축소.

6. [시크릿 위생] .gitignore에 `.env.*` + `!.env.example` + `apps/**/.env` 추가. 미래의 실수 커밋 예방.

7. [보안 헤더] main.py에 SecurityHeadersMiddleware 한 개(nosniff/X-Frame-Options DENY/HSTS/Referrer-Policy). 금융 앱 기본기.

8. [CORS 축소] main.py:27-28 allow_methods를 [GET,POST,PATCH,PUT,DELETE,OPTIONS], allow_headers를 [Authorization,Content-Type]로.

1·2·3은 사용자가 우려한 두 축(보안·AI 비용)을 정확히 직격하는 핵심 3종. 우선 이것부터.
# 배포 가이드 — 캐시매니저 (Railway 단일 서비스)

> 방식: **Railway 한 서비스**에서 FastAPI가 빌드된 React 웹까지 함께 서빙(루트 `Dockerfile`).
> 결과: **URL 하나 · CORS 불필요 · 환경변수 한 세트.** DB는 Supabase(이미 클라우드).
> 비용: Railway ~$5/월(항상 켜짐, 콜드스타트 없음) + OpenAI 사용량(소액).

## 동작 구조
```
[Railway 단일 서비스]  ← 루트 Dockerfile
   ├─ node 스테이지: apps/web 빌드 (VITE_* 빌드시 주입)
   └─ python 스테이지: apps/api 실행 (uvicorn) + 빌드된 웹을 /app/web 에서 서빙
        / → React SPA  ·  /health·/budgets·... → API  (같은 origin)
```

## 사전 준비
- GitHub: https://github.com/Jaehyeok-Lee-pastel/cashmanager (완료)
- Supabase 프로젝트 + 마이그레이션 적용(완료)
- 준비할 키: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_JWT_SECRET(있으면), anon key, OPENAI_API_KEY

---

## A) Railway 배포
1. https://railway.app 가입(GitHub 연동) → **New Project → Deploy from GitHub repo** → `cashmanager` 선택
2. Railway가 루트 **`Dockerfile`** 을 자동 감지해 빌드(단일 서비스).
3. 서비스 → **Variables** 에 아래를 모두 추가(빌드·런타임 공용으로 들어감):
   ```
   # --- 웹 빌드용 (프론트에 박힘, 공개용) ---
   VITE_SUPABASE_URL=https://xxxx.supabase.co
   VITE_SUPABASE_ANON_KEY=eyJ... (anon)
   VITE_API_BASE_URL=            # 비워둠 = 같은 주소(상대경로). Dockerfile 기본값도 빈값

   # --- API 런타임용 (비밀) ---
   SUPABASE_URL=https://xxxx.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=eyJ... (service_role, 비밀)
   SUPABASE_JWT_SECRET=...        # 있으면
   OPENAI_API_KEY=sk-...
   OPENAI_MODEL=gpt-5.4-mini
   ```
   > `PORT`·`WEB_DIR`·`APP_ENV`는 Railway/Dockerfile이 알아서 처리 — 건드리지 말 것.
4. **Settings → Networking → Generate Domain** 으로 공개 URL 발급(예: `https://cashmanager-production.up.railway.app`).
5. 배포 완료 후 그 URL 접속 → `/health`가 JSON, `/`가 로그인 화면이면 성공.

---

## B) Supabase Auth 연결 (로그인용)
Supabase 대시보드 → **Authentication → URL Configuration**:
- **Site URL**: 위 Railway URL
- **Redirect URLs**: 위 Railway URL 추가
- (Google 로그인 쓰면) Google Cloud OAuth 리디렉션에도 도메인 등록.

> 이메일 가입 즉시 로그인하려면 **Authentication → Providers → Email → "Confirm email" OFF**(테스트용).

---

## C) 폰에서 PWA로 쓰기
1. 폰 브라우저로 Railway URL 접속 → 로그인
2. **홈 화면에 추가**: 안드로이드 크롬 메뉴(⋮) → "앱 설치" / 아이폰 사파리 공유 → "홈 화면에 추가"
3. 홈 아이콘으로 앱처럼 전체화면 실행. (iOS 아이콘은 추후 PNG 교체 가능)

---

## 운영 팁
- 코드 `git push` → Railway 자동 재배포.
- 친구 배포 시 OpenAI 비용 보호: `apps/api/app/core/ratelimit.py` 한도 조정(+ 원하면 일일 상한 추가).
- 완전 무료로 맛보기만 원하면: 웹 = Vercel(무료) + API = Render Free(콜드스타트). 단일 서비스 장점(URL 하나·CORS 0)은 사라짐.

## 트러블슈팅
- **로그인 안 됨** → Supabase Site URL/Redirect URLs에 Railway 도메인 등록했는지.
- **화면은 뜨는데 API 401/에러** → JWT/Supabase 키 확인. 같은 origin이라 CORS는 신경 안 써도 됨.
- **빌드 실패** → Railway Variables에 VITE_SUPABASE_URL/ANON_KEY 넣었는지(웹 빌드에 필요).
- **첫 배포가 느림** → Docker 멀티스테이지 빌드라 처음만 몇 분, 이후 캐시.

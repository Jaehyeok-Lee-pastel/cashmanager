# 배포 가이드 — 캐시매니저

> 목표: 폰에서 PWA로 매일 쓸 수 있게 **무료(또는 소액)** 로 배포. 구성 = 웹(Vercel) + API(Render) + DB(Supabase, 이미 클라우드).
> 비용: Vercel 무료 · Render 무료(비활성 시 슬립) · Supabase 무료 · OpenAI 사용량(개인 소액).

## 사전 준비
- GitHub 저장소: https://github.com/Jaehyeok-Lee-pastel/cashmanager (완료)
- Supabase 프로젝트 + 마이그레이션 적용 (완료)
- OpenAI API 키
- 키 값 준비: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWT_SECRET`(있으면), anon key

---

## A) API 배포 — Render (FastAPI)
1. https://render.com 가입(GitHub 연동) → **New → Web Service** → 저장소 선택
2. 설정:
   - **Root Directory**: `apps/api`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. **Environment** 탭에 변수 추가(.env 파일 대신 여기 입력 — pydantic-settings가 환경변수를 읽음):
   ```
   APP_ENV=production
   SUPABASE_URL=https://xxxx.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=eyJ... (service_role, 비밀)
   SUPABASE_JWT_SECRET=...(있으면)
   OPENAI_API_KEY=sk-...
   OPENAI_MODEL=gpt-5.4-mini
   CORS_ORIGINS=https://임시            # 웹 배포 후 실제 주소로 교체(B 끝나고)
   ```
4. 배포 → 주소 확보(예: `https://cashmanager-api.onrender.com`) → `/health` 200 확인.

> ⚠️ Render 무료는 비활성 시 슬립 → 첫 요청 ~30초 콜드스타트. 항상 켜두려면 유료($7/월) 또는 Railway/Fly 대안.

---

## B) 웹 배포 — Vercel (React/Vite)
1. https://vercel.com 가입(GitHub 연동) → **Add New → Project** → 저장소 선택
2. 설정:
   - **Root Directory**: `apps/web`
   - **Framework Preset**: Vite (자동) · Build: `npm run build` · Output: `dist`
3. **Environment Variables** (빌드 전에 반드시 입력 — VITE_ 변수는 빌드 시 박힘):
   ```
   VITE_API_BASE_URL=https://cashmanager-api.onrender.com   # A의 API 주소
   VITE_SUPABASE_URL=https://xxxx.supabase.co
   VITE_SUPABASE_ANON_KEY=eyJ... (anon, 공개용)
   ```
4. 배포 → 주소 확보(예: `https://cashmanager.vercel.app`).

---

## C) 연결 마무리 (중요)
1. **CORS**: Render(A) 환경변수 `CORS_ORIGINS`를 웹 주소로 교체 → `https://cashmanager.vercel.app` → API 재배포.
2. **Supabase Auth 리다이렉트**: Supabase 대시보드 → **Authentication → URL Configuration** →
   - **Site URL**: `https://cashmanager.vercel.app`
   - **Redirect URLs**에도 추가 (Google 로그인·이메일 확인 링크가 배포 도메인으로 동작하게)
3. (Google 로그인 쓰면) Google Cloud OAuth 동의화면/리디렉션에 도메인 등록 — Supabase 가이드 따름.

---

## D) 폰에서 PWA로 쓰기
1. 폰 브라우저(크롬/사파리)로 `https://cashmanager.vercel.app` 접속 → 로그인
2. **홈 화면에 추가**:
   - 안드로이드 크롬: 메뉴(⋮) → "앱 설치" / "홈 화면에 추가"
   - 아이폰 사파리: 공유 → "홈 화면에 추가"
3. 홈 화면 아이콘으로 **앱처럼 전체화면 실행**.

> iOS는 아이콘이 기본으로 보일 수 있음(SVG 한계). 추후 `apps/web/public/`에 PNG(180·192·512) 추가 + manifest/`apple-touch-icon` 교체하면 해결.

---

## 비용 요약
| 항목 | 무료 한도 | 초과 시 |
|---|---|---|
| Vercel | 개인 무료 | 트래픽 큼 |
| Render | 무료(슬립) | 항상 켜두면 $7/월 |
| Supabase | 무료(작은 DB) | 사용량 증가 시 |
| OpenAI | 없음(사용량제) | 개인 하루 몇 원 — `ratelimit.py`로 보호 |

## 운영 팁
- 코드 push → Vercel/Render가 자동 재배포(연동 시).
- 친구 배포 시 OpenAI 비용 보호: `apps/api/app/core/ratelimit.py` 한도 조정 + (원하면) 일일 상한 추가.
- 콜드스타트가 싫으면 API를 Railway/Fly로(무료 크레딧/상시 가동 옵션).

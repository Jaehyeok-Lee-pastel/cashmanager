# Stack Rule — Python / FastAPI (api)

> 상세·예시는 [`docs/08_coding_guidelines/02_python_fastapi.md`](../../docs/08_coding_guidelines/02_python_fastapi.md). 이 카드는 Claude가 항상 지키는 요약.

- **레이어 분리**: 라우터(`app/api/routes/`)는 HTTP 입출력·의존성만. 비즈니스 로직은 `app/services/`, DB 접근은 `app/repositories/`(또는 service 내부), 타입은 `app/schemas/`(Pydantic).
- **라우트는 얇게**: `async def` 기본. 긴 DB 조회·분류·외부호출을 라우터에 직접 넣지 않는다.
- **타입힌트 필수**, PEP8, `snake_case`(함수/모듈), `PascalCase`(클래스), `UPPER_SNAKE_CASE`(상수). 라인 길이 ~100.
- **Pydantic**: request/response는 모델로. DB raw row를 그대로 노출 금지. enum류는 `Literal`/`Enum`.
- **Supabase 클라이언트는 `app/services/supabase.py`에서만 생성**. 라우터에서 `create_client` 직접 호출 금지.
- **인증/권한**: `get_current_user`(JWT 검증)는 `app/api/deps.py`. service_role로 DB를 읽더라도 **테넌트/소유권 검증을 서버에서 반드시** 수행(RLS 우회 전제).
- **시크릿**: `SUPABASE_SERVICE_ROLE_KEY` 등은 백엔드 전용. 코드/로그/프론트에 노출 금지. 설정은 `app/core/config.py`(pydantic-settings)에서 `.env` 로드.
- **포맷/린트**: `ruff format .` / `ruff check .`. 변경 후 최소 `python -m py_compile` 또는 import 통과 확인.
- **테스트 우선순위**: 권한검증 → 핵심 도메인 로직 → AI/외부 JSON validation → 응답 schema.
- 파일이 150~200줄을 넘거나 책임이 2개 이상 섞이면 분리.

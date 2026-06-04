# Stack Rule — Supabase (db)

> 데이터 아키텍처 산출물은 [`docs/04_data_architecture/`](../../docs/04_data_architecture/), 마이그레이션은 [`supabase/migrations/`](../../supabase/migrations/).

- **변경은 항상 migration 파일로 남긴다**. 기존 migration을 되돌리지 말고 **새 파일로 보정**한다(타임스탬프 prefix: `YYYYMMDDhhmm_description.sql`).
- **RLS**: 새 테이블은 RLS를 **켠다(enable)** 그리고 **policy를 둔다**. 테넌트 컬럼(예: `workspace_id`/`org_id`) 기준 접근 제어.
- **키 분리**: 프론트=anon key, 백엔드=service_role key. service_role은 RLS를 우회하므로 **API 레이어에서 소유권/테넌트 검증 필수**.
- **인덱스**: 자주 필터/정렬하는 컬럼, FK, 페이징 정렬 기준에 인덱스를 둔다.
- **seed**: `supabase/seed.sql`는 개발용. 운영 DB에 그대로 적용 금지. 플레이스홀더 id는 실제 `auth.users.id`로 교체 후 사용.
- 파괴적 SQL(`DROP`/`TRUNCATE`/`DELETE`·`UPDATE` without WHERE)은 `guard-bash.py`가 CLI 실행을 차단한다 — migration 파일로 의도를 명시한다.

# Stack Rule — React / TypeScript (web)

> 상세·예시는 [`docs/08_coding_guidelines/03_react_typescript.md`](../../docs/08_coding_guidelines/03_react_typescript.md). 이 카드는 Claude가 항상 지키는 요약.

- **함수형 컴포넌트** + TypeScript `strict`. 컴포넌트 `PascalCase`, 함수/변수 `camelCase`, 타입/인터페이스 `PascalCase`, hook은 `use`로 시작.
- **폴더**: `src/app/`(App·routes), `src/components/`(공통·layout), `src/features/{domain}/`(도메인 기능), `src/lib/`(api·supabase·util), `src/styles/`. 파일이 늘면 이 구조로 이동.
- **컴포넌트**: 한 파일에 주 컴포넌트 하나. 150줄 넘으면 분리 검토. props 타입은 컴포넌트 가까이.
- **API 호출은 `src/lib/api.ts`로 감싼다**. 컴포넌트에 URL 문자열 흩뿌리기 금지. response 타입 명시. 에러는 사용자용 문구로 변환.
- **Supabase 클라이언트는 `src/lib/supabase.ts`에서만 생성**. 프론트는 **anon key만** 사용. `service_role` key를 프론트 env에 넣지 않는다.
- **상태**: MVP는 로컬 state + Supabase session. 전역 상태 라이브러리는 필요해질 때 TanStack Query부터 검토.
- **상태 UI**: loading / error / empty 3상태를 둔다.
- **접근성**: input에 label/`aria-label`, icon-only 버튼에 `aria-label`, 색상만으로 상태 구분 금지, 실제 `<button>` 사용.
- UI 문구는 한국어 허용, **코드 식별자는 영어 도메인 용어**.
- **품질**: `npm run build`(= `tsc -b && vite build`) / `npm run typecheck` 통과. 한글 깨짐 없는지 확인.

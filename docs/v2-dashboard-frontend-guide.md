# V2-Dashboard Frontend 학습 + 구현 가이드 (Next.js 14 / 자바 개발자용)

대상: Java/Spring 개발자, 프론트/Next.js 신규
구현 대상: V2-Dashboard Phase 1 frontend (1-page 모니터링 대시보드)
박제 출처: `docs/stage1-subplans/v2-dashboard.md` V2-D-03

---

## 1. Next.js 핵심 (Spring 비유)

| Next.js | Spring/Java 비유 |
|---------|-----------------|
| **App Router** (`app/` 디렉토리) | `@Controller` + URL 매핑. 폴더 구조가 곧 URL (`app/page.tsx` = `/`, `app/about/page.tsx` = `/about`) |
| **`page.tsx`** | `@GetMapping("/")` 메서드 — 해당 path의 default export를 컴포넌트로 렌더 |
| **`layout.tsx`** | 공통 wrapper (Spring `@ControllerAdvice` + Thymeleaf layout 같은 역할). 자식 page를 `{children}`으로 감쌈 |
| **Server Component** (기본) | 서버에서 HTML 렌더링 → 클라이언트로 전송. JSP/Thymeleaf와 비슷. **fetch / DB 호출은 여기서** |
| **Client Component** (`"use client"`) | 브라우저에서 hydration + JS 동작. `useState`, `useEffect`, 이벤트 핸들러 사용. JSP의 `<script>` 영역 |
| **`fetch()`** | Java 11+ HttpClient 또는 `RestTemplate.getForObject`. `await` 키워드 있음 |
| **`async/await`** | Java의 `CompletableFuture.thenApply` 비슷. 비동기 결과를 동기처럼 작성 |
| **TypeScript** | Java 정적 타입 + `interface` 거의 동일. `interface Position { entry_price_krw: number; ... }` |
| **JSX/TSX** | Thymeleaf + Java 표현식 같은 거. `<div>{value}</div>` 형태 |

### 1.1 폴더 구조 (우리 dashboard/frontend)

```
dashboard/frontend/
├── package.json              # Maven pom.xml 같은 의존성 정의
├── next.config.js            # Spring application.yml 같은 설정
├── tsconfig.json             # TypeScript 컴파일 설정
├── tailwind.config.ts        # Tailwind CSS 설정 (디자인 utility)
└── src/
    ├── app/
    │   ├── layout.tsx        # 공통 레이아웃 (HTML, body, nav)
    │   ├── page.tsx          # 메인 / 라우트 (대시보드)
    │   └── globals.css       # 전역 CSS
    ├── components/           # 재사용 컴포넌트 (Position 카드, PnL 차트 등)
    └── lib/                  # API 호출 함수 (Spring service layer 비유)
```

---

## 2. TypeScript 빠른 정리 (Java vs TS)

```typescript
// Java
public interface Position {
    String cellKey;
    double entryPriceKrw;
    Long volume;  // nullable
}

// TypeScript
interface Position {
    cell_key: string;
    entry_price_krw: number;
    volume: number | null;  // nullable union 타입
}

// Java
public List<Position> getPositions() { ... }

// TypeScript
function getPositions(): Position[] { ... }
async function getPositions(): Promise<Position[]> { ... }
```

차이점 정리:
- 타입 표기는 변수/함수 뒤 (`name: string`, `() => string`)
- 함수 반환 타입은 `:` 뒤
- **`null | undefined | number` union** 자유롭게
- `Promise<T>` = Java `CompletableFuture<T>`

---

## 3. App Router 데이터 fetch (3가지 패턴)

### 3.1 Server Component에서 fetch (권장 — SEO/초기 로드 빠름)

```typescript
// app/page.tsx (Server Component, 기본)
async function fetchPositions() {
    const res = await fetch("http://127.0.0.1:8001/api/positions", { cache: "no-store" });
    return res.json();
}

export default async function Page() {
    const data = await fetchPositions();   // Java: CompletableFuture .get()
    return <div>{data.count} positions</div>;
}
```

`cache: "no-store"` = Spring `@Cacheable` 끄기. 매 요청마다 fresh.

### 3.2 Client Component에서 fetch + state

```typescript
"use client";
import { useEffect, useState } from "react";

export default function PositionList() {
    const [data, setData] = useState<Position[]>([]);
    useEffect(() => {
        fetch("/api/positions").then(r => r.json()).then(d => setData(d.positions));
    }, []);   // [] = mount 시 1회 (Spring `@PostConstruct`와 비슷)
    return <ul>{data.map(p => <li key={p.cell_key}>{p.cell_key}</li>)}</ul>;
}
```

`useState` = 컴포넌트 내부 상태 (Java: 인스턴스 필드). `useEffect` = lifecycle hook.

### 3.3 폴링 (실시간 업데이트)

```typescript
useEffect(() => {
    const fetchData = () => fetch("/api/positions").then(r => r.json()).then(setData);
    fetchData();
    const id = setInterval(fetchData, 30_000);  // 30초마다
    return () => clearInterval(id);   // unmount 시 cleanup (Spring `@PreDestroy`)
}, []);
```

대시보드 모니터링용에 적합.

---

## 4. Tailwind CSS (utility-first)

```html
<!-- 기존 CSS 방식 -->
<div class="card">
  <h1>제목</h1>
</div>
<style>
  .card { padding: 1rem; border: 1px solid gray; border-radius: 8px; }
</style>

<!-- Tailwind 방식 -->
<div class="p-4 border border-gray-300 rounded-lg">
  <h1>제목</h1>
</div>
```

자바 비유: Tailwind = Bootstrap utility classes. 별도 CSS 작성 거의 X, HTML에 utility 직접 박제.

자주 쓰는 유틸:
- `p-4` = padding 1rem, `m-2` = margin 0.5rem
- `flex flex-col gap-2` = flexbox + 세로 + 자식 사이 간격
- `bg-gray-100`, `text-blue-600`, `hover:bg-gray-200`
- `rounded-lg`, `shadow`, `border`
- `grid grid-cols-3` = 3열 grid

---

## 5. 우리 Dashboard 화면 설계

```
┌─────────────────────────────────────────────────────┐
│  coin-bot dashboard                  daemon: alive  │
│                                      last cycle: 09:05 KST │
├─────────────────────────────────────────────────────┤
│  [총 PnL 카드]    [trades]   [win/loss]   [days]    │
│  +12,500 KRW      8 cells    5/3          14d       │
├─────────────────────────────────────────────────────┤
│  [Open Positions]                                    │
│  ┌──────────────┬──────────────┬──────────────┐    │
│  │ KRW-BTC_A    │ KRW-ETH_A    │ KRW-BTC_D    │    │
│  │ entry  85M   │ entry  6.2M  │ entry  85.2M │    │
│  │ unrl  +2.5%  │ unrl  -1.0%  │ (no pos)     │    │
│  └──────────────┴──────────────┴──────────────┘    │
├─────────────────────────────────────────────────────┤
│  [PnL Chart] (Chart.js / recharts)                  │
│   누적 realized PnL 시계열                          │
├─────────────────────────────────────────────────────┤
│  [Recent Trades] (테이블)                           │
│  date  side  pair    price       PnL                │
│  04-26 sell  KRW-BTC 116M       +269                │
├─────────────────────────────────────────────────────┤
│  [Recent Logs] (ERROR 우선)                         │
└─────────────────────────────────────────────────────┘
```

### 5.1 컴포넌트 구조

```
src/
├── app/
│   └── page.tsx                  # 전체 조립
├── components/
│   ├── HealthBadge.tsx           # daemon alive 표시
│   ├── SummaryCards.tsx          # 상단 4 카드
│   ├── PositionCard.tsx          # 단일 포지션
│   ├── PositionGrid.tsx          # 3 cells grid
│   ├── PnLChart.tsx              # 차트
│   ├── TradesTable.tsx           # trades 테이블
│   └── LogsPanel.tsx             # 최근 로그
└── lib/
    ├── api.ts                    # fetch wrapper (위 §3.3 패턴)
    └── types.ts                  # Position / Trade / Order 타입
```

---

## 6. 단계별 구현 (V2-D-03)

본 가이드를 따라 다음 순서로 구현:

| 단계 | 작업 | 학습 포인트 |
|------|------|------------|
| **6.1** | `create-next-app` 초기화 | npm/Next.js 셋업 |
| **6.2** | `lib/types.ts` + `lib/api.ts` 작성 | TS interface + fetch wrapper |
| **6.3** | `HealthBadge` 컴포넌트 | Server Component fetch + JSX |
| **6.4** | `SummaryCards` + `PositionGrid` | Tailwind utility + props |
| **6.5** | `TradesTable` | 테이블 + map 렌더링 |
| **6.6** | `PnLChart` (recharts) | 차트 라이브러리 + Client Component |
| **6.7** | `LogsPanel` | 폴링 (실시간) |
| **6.8** | `app/page.tsx` 조립 + Tailwind layout | 전체 통합 |
| **6.9** | localhost 통합 sanity (backend ↔ frontend) | E2E |

각 단계 commit하고 사용자 진도 확인.

---

## 7. 환경 변수 (보안 박제)

```bash
# dashboard/frontend/.env.local (gitignored)
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8001
```

`NEXT_PUBLIC_` 접두 = 브라우저에 노출 (Spring `@ConfigurationProperties` public 필드와 비슷). 시크릿이라면 접두 X (서버 only).

본 dashboard는 **read-only API**라 NEXT_PUBLIC OK. 매매 제어 (Phase 2) 시점엔 별도 설계.

---

## 8. 실행 명령어 모음

```bash
# 개발 서버 (hot reload)
cd dashboard/frontend
npm run dev                       # localhost:3000

# 빌드 (프로덕션)
npm run build && npm run start    # localhost:3000

# 린트
npm run lint
```

V2-D-06 launchd plist에서는 `npm run build && next start` 형태. 또는 정적 export (`next export`) → backend가 정적 파일 서빙.

---

## 9. 자바 개발자 자주 만나는 함정

1. **`undefined` vs `null`**: TS에서 둘 다 falsy. union 타입 `string | null | undefined` 자주.
2. **Promise 반환**: `async` 함수는 항상 `Promise<T>`. caller에서 `await` 또는 `.then()`.
3. **`Array.map`**: Java Stream `.map`과 동일. JSX 내부에서 `{arr.map(x => <li>{x}</li>)}` 패턴 흔함.
4. **`key` prop**: 리스트 렌더링 시 React가 element 추적용. Java HashMap key 같은 역할. `<li key={item.id}>`.
5. **Client Component import 트리**: `"use client"` 선언한 컴포넌트가 Server Component를 import할 수 없음. 반대는 OK.
6. **fetch CORS**: backend가 `Access-Control-Allow-Origin` 헤더 안 주면 브라우저가 차단. 우리 backend는 `localhost:3000` 허용 박제됨 (`app/main.py` CORS).

---

End of frontend guide. 다음: `dashboard/frontend/` create-next-app 초기화.

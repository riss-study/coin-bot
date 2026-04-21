# 시스템 아키텍처

> `decisions-final.md`의 결정을 실제 시스템으로 구현하는 설계 문서.
> 진화하는 문서 — Phase별로 새 컴포넌트 추가 시 업데이트.
>
> 모르는 단어는 [`glossary.md`](./glossary.md) 참조.
> TimescaleDB, Cloudflare Tunnel, Freqtrade, vectorbt 등 도구 설명 포함.

---

## Phase 로드맵

| Phase | 기간 | 주요 산출물 | 킬 체크포인트 |
|-------|------|-----------|--------------|
| **P1** | Week 1 | Jupyter 데이터 수집 + 단일 전략 복제 | Sharpe > 0.8? |
| **P2** | Week 2 | Walk-forward + DSR + 알트 확장 | DSR > 0.5? |
| **P3** | Week 3 | Option 3 (A/B/C 비교) → 전략 확정 | 전략 채택 가능? |
| **P4** | Week 4 | Freqtrade 이식 + Docker 설정 | 노트북과 동일 결과? |
| **P5** | Week 5 | 실시간 데이터 파이프라인 + 페이퍼 모드 | 체결 시뮬레이션 OK? |
| **P6** | Week 6~9 | 페이퍼 트레이딩 4주 | 백테스트의 70%+? |
| **P7** | Week 10~11 | 대시보드 (FastAPI + Next.js) + Cloudflare Tunnel | 외부 접속 가능? |
| **P8** | Week 12+ | 라이브 전환 (50만원) — **모든 조건 충족 시** | 8주 킬 체크 |
| **P9** | Month 4+ | 안정화 + 모니터링 고도화 | — |
| **P10+** | Month 5+ | LLM 5개 역할 추가 (옵션) | — |

---

## 전체 시스템 다이어그램 (완성 형태)

```
┌───────────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL DATA SOURCES                              │
│                                                                           │
│  업비트 API     바이낸스 API    FRED API    alternative.me    CoinGecko    │
│  (REST+WS)     (REST)          (HTTP)       (HTTP)            (HTTP)      │
└──────────┬────────────┬────────────┬────────────┬──────────────┬──────────┘
           │            │            │            │              │
           ▼            ▼            ▼            ▼              ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                      DATA INGESTION LAYER                                 │
│                                                                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │
│  │ OHLCV       │ │ Orderbook   │ │ Macro Data  │ │ Sentiment/Index     │ │
│  │ Collector   │ │ Collector   │ │ Collector   │ │ Collector           │ │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────────┬──────────┘ │
│         │               │               │                    │            │
│         └───────────────┴───────────────┴────────────────────┘            │
│                                 │                                          │
│                                 ▼                                          │
│                      ┌──────────────────────┐                             │
│                      │  Gap Detection &     │                             │
│                      │  Anomaly Filter      │                             │
│                      └──────────┬───────────┘                             │
└─────────────────────────────────┼─────────────────────────────────────────┘
                                  │
                                  ▼
┌───────────────────────────────────────────────────────────────────────────┐
│               POSTGRESQL + TIMESCALEDB (Single Source of Truth)           │
│                                                                           │
│  Hypertables:                                                              │
│    ohlcv_1m          (1분봉 원시)                                         │
│    ohlcv_4h          (리샘플, 전략 결정용)                                  │
│    macro_indicators  (FOMC/CPI/DXY/고용/F&G)                              │
│    orderbook_snap    (5분마다 스냅샷, 슬리피지 모델용)                      │
│                                                                           │
│  Regular Tables:                                                           │
│    trades            (체결 기록 — 세금 로깅 기반)                          │
│    positions         (현재 오픈 포지션)                                     │
│    signals           (생성된 매매 신호 + 이유)                              │
│    regime_states     (분류된 레짐 히스토리)                                 │
│    circuit_events    (서킷 브레이커 발동 이력)                              │
│    audit_log         (대시보드 수동 조작 감사)                              │
└─────────────────────────────────┬─────────────────────────────────────────┘
                                  │
                                  ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                       STRATEGY & DECISION ENGINE                          │
│                              (Freqtrade)                                  │
│                                                                           │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────────────┐ │
│  │  Strategy A     │   │  Strategy B     │   │  Regime Filter          │ │
│  │  Trend-Follow   │   │  Mean-Reversion │   │  (200MA + ADX + ATR%)   │ │
│  │  200MA+Donchian │   │  RSI(4)<25      │   │                         │ │
│  └────────┬────────┘   └────────┬────────┘   └──────────┬──────────────┘ │
│           │                     │                        │                │
│           └─────────┬───────────┘                        │                │
│                     ▼                                    │                │
│           ┌──────────────────┐                           │                │
│           │ Ensemble Combiner│◄──────────────────────────┘                │
│           │  (50/50 weights) │                                            │
│           └────────┬─────────┘                                            │
│                    │                                                       │
│                    ▼                                                       │
│           ┌──────────────────┐                                            │
│           │  Risk Filters    │                                            │
│           │  - Event windows │  (FOMC/CPI 차단)                          │
│           │  - F&G extremes  │                                            │
│           │  - BTC -10%/24h  │                                            │
│           └────────┬─────────┘                                            │
│                    │                                                       │
│                    ▼                                                       │
│           ┌──────────────────┐                                            │
│           │ Position Sizer   │  ATR 기반, 리스크 1%                      │
│           └────────┬─────────┘                                            │
└────────────────────┼───────────────────────────────────────────────────────┘
                     │
                     ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                        CIRCUIT BREAKERS (항상 감시)                      │
│                                                                           │
│  L1: BTC -5%/4h → 50% 정리       L2: -10%/24h → 전량 청산                │
│  L3: -15%/24h → 72h 중단          L4: 수동 킬 스위치                      │
└────────────────────┬───────────────────────────────────────────────────────┘
                     │
                     ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                      ORDER EXECUTION LAYER                                │
│                                                                           │
│  업비트 주문 API (pyupbit) → 체결 확인 → DB 기록                            │
│  미체결 주문 재조정 (reconciliation)                                        │
│  WebSocket 끊김 시 REST 폴백                                               │
└────────────────────┬───────────────────────────────────────────────────────┘
                     │
         ┌───────────┼───────────┐
         ▼           ▼           ▼
┌────────────┐ ┌──────────┐ ┌──────────────────┐
│ DASHBOARD  │ │ DISCORD  │ │ KAKAOTALK        │
│ (FastAPI + │ │ WEBHOOK  │ │ (urgent only)    │
│  Next.js)  │ │          │ │                  │
└─────┬──────┘ └──────────┘ └──────────────────┘
      │
      ▼
┌──────────────┐
│ CLOUDFLARE   │
│ TUNNEL       │
│ (HTTPS auto) │
└──────┬───────┘
       │
       ▼
   [Browser]
```

---

## 컴포넌트 상세

### 1. Data Ingestion Layer

**목적**: 업비트 + 외부 데이터 소스에서 필요한 데이터를 가져와 DB에 저장.

**서브 컴포넌트**:

#### 1-1. OHLCV Collector
- Initial backfill: 업비트 5년치 1분봉 다운로드 (Week 1)
- Incremental: 매 1분마다 최신 봉 가져오기
- Gap detection: 예상 타임스탬프 vs 실제 비교
- Anomaly filter: `(high-low)/close > 10 * rolling_std` 체크
- 저장: `ohlcv_1m` hypertable

#### 1-2. Orderbook Snapshot Collector
- 매 5분마다 상위 15 레벨 호가창 스냅샷
- 슬리피지 모델 학습/검증용
- 저장: `orderbook_snap`

#### 1-3. Macro Data Collector
- FRED API: FOMC/CPI/DXY/고용 (스케줄 발표 후 업데이트)
- alternative.me: 공포탐욕지수 (일 1회)
- CoinGecko: BTC 도미넌스 (시간 단위)
- ExchangeRate API: USD/KRW (일 1회)
- 저장: `macro_indicators`

#### 1-4. Resampler
- 1분봉 → 4시간봉 자동 리샘플 (전략용)
- TimescaleDB `time_bucket()` 활용
- Continuous aggregate로 성능 최적화

---

### 2. Strategy & Decision Engine (Freqtrade)

**목적**: 데이터 → 매매 신호 생성.

**구조**:
```
engine/
├── strategies/
│   ├── trend_following.py       # Strategy A
│   ├── mean_reversion.py        # Strategy B
│   └── ensemble.py              # Strategy C
├── filters/
│   ├── regime_filter.py         # 200MA + ADX + ATR%
│   ├── event_filter.py          # FOMC/CPI 차단
│   └── extremes_filter.py       # F&G, BTC 급락
├── sizing/
│   └── atr_volatility_sizer.py
├── circuit_breakers/
│   └── breakers.py              # L1~L4
└── executor/
    ├── upbit_executor.py        # pyupbit 기반
    └── reconciler.py            # 미체결 주문 정리
```

**Freqtrade 커스텀**:
- 업비트는 Freqtrade 기본 지원, ccxt로 연결
- 커스텀 손절 로직 (ATR 트레일링)
- 커스텀 지표 (RSI(4), Donchian 20/10)

---

### 3. Database (PostgreSQL + TimescaleDB)

**주요 테이블 스키마** (FK 의존성 순서로 작성: signals → trades):

```sql
-- 시계열 데이터 (Hypertable)
CREATE TABLE ohlcv_1m (
    time        TIMESTAMPTZ NOT NULL,
    exchange    TEXT NOT NULL,
    symbol      TEXT NOT NULL,
    open        NUMERIC(20,8),
    high        NUMERIC(20,8),
    low         NUMERIC(20,8),
    close       NUMERIC(20,8),
    volume      NUMERIC(30,8),
    PRIMARY KEY (time, exchange, symbol)
);
SELECT create_hypertable('ohlcv_1m', 'time');

-- 인덱스: 심볼 기반 조회 최적화
CREATE INDEX ON ohlcv_1m (exchange, symbol, time DESC);

-- signals를 먼저 생성 (trades가 FK로 참조)
CREATE TABLE signals (
    signal_id       UUID PRIMARY KEY,
    time            TIMESTAMPTZ NOT NULL,
    pair            TEXT NOT NULL,
    strategy_name   TEXT NOT NULL,
    side            TEXT NOT NULL,
    confidence      NUMERIC,
    indicators      JSONB,   -- RSI, ATR, MA values
    regime          TEXT,
    filters_passed  TEXT[],  -- 어떤 필터를 통과했는지
    was_executed    BOOLEAN,
    skip_reason     TEXT
);
CREATE INDEX ON signals (pair, time DESC);

-- 세금 로깅 기반 (라이브 전환 시 채우기 시작)
CREATE TABLE trades (
    trade_id            UUID PRIMARY KEY,
    timestamp_utc       TIMESTAMPTZ NOT NULL,
    timestamp_kst       TIMESTAMPTZ NOT NULL,
    exchange            TEXT NOT NULL,
    pair                TEXT NOT NULL,
    side                TEXT NOT NULL,  -- 'buy' or 'sell'
    quantity            NUMERIC(20,8) NOT NULL,
    price_krw           NUMERIC(20,8) NOT NULL,
    fee_krw             NUMERIC(20,8) NOT NULL,
    realized_pnl_krw    NUMERIC(20,8),  -- sell 시에만
    cost_basis_method   TEXT DEFAULT 'FIFO',
    running_holdings    NUMERIC(20,8),
    strategy_name       TEXT,
    signal_id           UUID REFERENCES signals(signal_id),
    is_paper            BOOLEAN DEFAULT true,
    metadata            JSONB
);
CREATE INDEX ON trades (pair, timestamp_utc DESC);
CREATE INDEX ON trades (strategy_name, timestamp_utc DESC);

CREATE TABLE regime_states (
    time        TIMESTAMPTZ NOT NULL,
    pair        TEXT NOT NULL,  -- 코인별 레짐 (또는 'BTC_GLOBAL')
    regime      TEXT NOT NULL,  -- trending_up/down/ranging/high_vol
    adx_4h      NUMERIC,
    ma200_dir   TEXT,
    atr_pct     NUMERIC,
    PRIMARY KEY (time, pair)
);

-- Note: Week 1에서는 'BTC_GLOBAL' 하나만 사용.
-- Phase 6에서 코인별 레짐 분류 시 여러 레코드로 확장.

CREATE TABLE audit_log (
    log_id      UUID PRIMARY KEY,
    timestamp   TIMESTAMPTZ NOT NULL DEFAULT now(),
    user_action TEXT NOT NULL,
    details     JSONB,
    ip_address  INET,
    session_id  TEXT
);
```

---

### 4. Dashboard

#### 4-1. Backend (FastAPI)

```
dashboard-backend/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── positions.py      # 현재 포지션 조회
│   │   ├── trades.py         # 매매 이력
│   │   ├── performance.py    # 수익률, Sharpe 등
│   │   ├── regime.py         # 레짐 상태
│   │   ├── macro.py          # 매크로 지표
│   │   ├── controls.py       # 수동 매매/일시정지/Kill
│   │   └── auth.py           # 로그인 (Cloudflare Access 연동)
│   ├── db/
│   ├── models/
│   └── services/
└── Dockerfile
```

**주요 엔드포인트**:
```
GET  /api/positions/current
GET  /api/trades?limit=100&since=2026-04-01
GET  /api/performance/daily
GET  /api/performance/summary
GET  /api/regime/current
GET  /api/macro/indicators
POST /api/controls/pause          → Freqtrade /api/v1/stop
POST /api/controls/resume         → Freqtrade /api/v1/start
POST /api/controls/manual-buy     → Freqtrade /api/v1/forcebuy   (1단계 확인)
POST /api/controls/manual-sell    → Freqtrade /api/v1/forcesell  (1단계 확인)
POST /api/controls/liquidate-all  → Freqtrade /api/v1/forcesell (all)  (2단계 확인)
POST /api/controls/kill-switch    → Freqtrade /api/v1/stop + freeze    (2단계 확인)
```

**보안 원칙**:
- Upbit API 키는 **strategy-engine 컨테이너만 보유**
- dashboard-backend는 Upbit 키 접근 권한 없음 (least privilege)
- dashboard-backend → strategy-engine 통신은 내부 Docker 네트워크 + 별도 토큰
- Cloudflare Tunnel은 dashboard-backend만 노출 (engine/DB는 노출 0)

**대시보드 → 업비트 매매 흐름**:
```
Browser
  → Cloudflare Tunnel (HTTPS 자동)
  → dashboard-backend (FastAPI) [Upbit 키 없음]
  → Freqtrade REST API (내부 네트워크, 토큰 인증)
  → strategy-engine [Upbit 키 보유]
  → pyupbit/ccxt
  → 업비트 API
```

#### 4-2. Frontend (Next.js)

```
dashboard-frontend/
├── app/
│   ├── page.tsx              # 메인 (포지션 + 수익률)
│   ├── trades/page.tsx
│   ├── performance/page.tsx
│   ├── regime/page.tsx
│   ├── macro/page.tsx
│   ├── controls/page.tsx     # 수동 제어 (권한 필요)
│   └── layout.tsx
├── components/
│   ├── PositionTable.tsx
│   ├── PnLChart.tsx
│   ├── CircuitBreakerStatus.tsx
│   ├── RegimeCard.tsx
│   └── ConfirmDialog.tsx     # 2단계 확인 다이얼로그
└── lib/
    ├── api.ts
    └── auth.ts
```

---

### 5. Cloudflare Tunnel 설정

**docker-compose.yml 에 추가**:
```yaml
services:
  cloudflared:
    image: cloudflare/cloudflared:latest
    command: tunnel run
    environment:
      - TUNNEL_TOKEN=${CLOUDFLARE_TUNNEL_TOKEN}
    networks:
      - coinbot-net
    depends_on:
      - dashboard-backend
      - dashboard-frontend
```

**설정 순서** (Week 10 시점):
1. Cloudflare 계정 가입 (무료)
2. Zero Trust 대시보드에서 Tunnel 생성
3. 토큰 복사 → macOS Keychain에 저장
4. docker-compose 기동 → 자동 HTTPS URL 발급
5. Cloudflare Access로 이메일 OTP 설정

---

### 6. 알림 시스템

```
notifications/
├── channels/
│   ├── discord.py      # Webhook 방식
│   └── kakao.py        # 카카오 알림톡 API
├── classifier.py       # 이벤트 → 채널 매핑
├── debouncer.py        # 5분 내 중복 방지
└── templates/          # 메시지 템플릿
```

**분류 로직**:
```python
URGENT_EVENTS = {
    'stop_loss_triggered',
    'circuit_breaker_l1', 'circuit_breaker_l2', 'circuit_breaker_l3',
    'critical_error',
    'api_key_error',
    'kill_switch_triggered',
}

def notify(event):
    send_discord(event)  # 항상
    if event.type in URGENT_EVENTS:
        send_kakao(event)  # 긴급만 추가
```

---

### 7. Docker Compose (Week 4+ 최종 형태)

```yaml
version: '3.9'

services:
  postgres:
    image: timescale/timescaledb:latest-pg15
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=coinbot
      - POSTGRES_USER=coinbot
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    networks:
      - coinbot-net

  data-collector:
    build: ./services/collector
    depends_on: [postgres]
    secrets:
      - upbit_key
      - upbit_secret
    environment:
      - UPBIT_API_KEY_FILE=/run/secrets/upbit_key
      - UPBIT_API_SECRET_FILE=/run/secrets/upbit_secret
    networks:
      - coinbot-net

  strategy-engine:
    build: ./services/engine   # Freqtrade + 커스텀
    depends_on: [postgres, data-collector]
    secrets:
      - upbit_key
      - upbit_secret
      - freqtrade_api_token
    environment:
      - MODE=paper  # or 'live'
      - UPBIT_API_KEY_FILE=/run/secrets/upbit_key
      - UPBIT_API_SECRET_FILE=/run/secrets/upbit_secret
      - FREQTRADE_API_TOKEN_FILE=/run/secrets/freqtrade_api_token
    networks:
      - coinbot-net

  dashboard-backend:
    build: ./services/dashboard-backend
    depends_on: [postgres, strategy-engine]
    secrets:
      - freqtrade_api_token   # 엔진 호출용 토큰만, Upbit 키는 없음
    environment:
      - FREQTRADE_API_TOKEN_FILE=/run/secrets/freqtrade_api_token
      - FREQTRADE_BASE_URL=http://strategy-engine:8080
    networks:
      - coinbot-net

  dashboard-frontend:
    build: ./services/dashboard-frontend
    depends_on: [dashboard-backend]
    networks:
      - coinbot-net

  cloudflared:
    image: cloudflare/cloudflared:latest
    command: tunnel --no-autoupdate run
    env_file:
      - ./secrets/.cloudflared.env   # TUNNEL_TOKEN=... 한 줄
    depends_on: [dashboard-frontend]
    networks:
      - coinbot-net

networks:
  coinbot-net:
    driver: bridge

# 일반 docker-compose (Swarm 아님) → file 기반 secrets
secrets:
  db_password:
    file: ./secrets/db_password.txt
  upbit_key:
    file: ./secrets/upbit_key.txt
  upbit_secret:
    file: ./secrets/upbit_secret.txt
  freqtrade_api_token:
    file: ./secrets/freqtrade_api_token.txt
```

**키 주입 흐름** (수정):
```
macOS Keychain
  ↓ (startup script: security find-generic-password)
임시 파일 (./secrets/, 권한 600)
  ↓ (docker compose up, secrets file mount)
컨테이너 /run/secrets/* 파일
  ↓ (앱이 *_FILE env var로 경로 받아 읽음)
앱 메모리만 (디스크 미저장)
  ↓ (docker compose down)
shutdown script가 ./secrets/ 안전 삭제 (shred)
```

**중요**: cloudflared는 `TUNNEL_TOKEN_FILE` 미지원 → `env_file:` 로 `TUNNEL_TOKEN=` 평문 라인 주입. 이 .env 파일도 startup script가 Keychain에서 생성, shutdown 시 삭제.

---

## Phase별 최소 구성

### Phase 1~3 (Week 1~3): 최소 구성
```
[ Jupyter 노트북 (로컬) ] → [ pandas DataFrames ] → [ Parquet 파일 ]
```
- Docker 없음, DB 없음, 프레임워크 없음
- 오직 데이터 + 노트북
- 목표: 전략 작동 여부 확인

### Phase 4~5 (Week 4~5): 엔진 추가
```
[ Docker: Postgres + Freqtrade ]
          ↓
    [ 페이퍼 트레이딩 ]
```

### Phase 6~9 (Week 6~11): 대시보드 추가
```
+ FastAPI 백엔드
+ Next.js 프론트엔드
+ Cloudflare Tunnel
```

### Phase 10+ (Month 5+): LLM 레이어 추가
```
+ LLM Service (별도 컨테이너)
  - 매크로 이벤트 태거
  - Validator
  - 레짐 내러티브
  - 사후 분석
  - 주간 리뷰
```

---

## 개발 우선순위 원칙

1. **데이터 무결성 > 기능 완성도**
   - 데이터가 틀리면 전략이 맞아도 의미 없음
   - Gap detection, anomaly filter 우선 구현

2. **관찰 가능성(Observability) > 성능**
   - 모든 신호, 체결, 거부권은 **왜** 발생했는지 기록
   - 사후 디버깅이 개발 속도보다 중요

3. **상태 복원력 > 새 기능**
   - 봇이 어떤 시점에 죽어도 재시작 시 일관된 상태로 복구 가능해야 함
   - Reconciliation 로직 첫날부터 구현

4. **주 단위 이터레이션**
   - 매주 끝 = 점검 포인트
   - "이번 주 학습한 것 + 다음 주 계획"을 문서로 남김

---

## Day 0 작성 당시 다음 단계 (완료, 역사 기록)

> 본 섹션은 2026-04-13 Day 0 작성 시점의 메모. 이후 진행 경과는 `stage1-execution-plan.md` 상태 표 + `git log main` 참조.

~~`week1-plan.md` 작성 후 Week 1 Day 1 시작.~~ — 완료. `week1-plan.md`는 sub-plan으로 분할됐고 EPIC Week 섹션은 `stage1-weekly/week1.md`로 이동됨 (2026-04-21).

**현재 위치**: W2-03 Go 결정 완료. W3-01 walk-forward 진입 대기.

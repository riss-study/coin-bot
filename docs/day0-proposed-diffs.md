# Day 0 — 수정 Diff 제안 (적용 완료, 역사적 문서)

> **상태: 적용 완료 (2026-04-12)**. 이 문서는 역사적 참조용.
> 모든 변경 사항이 `decisions-final.md`, `architecture.md`, `week1-plan.md`에 적용됨.
>
> 추가로 vectorbt 0.28.5 + pyupbit 0.2.34 API를 web search로 검증한 결과를 반영함.
>
> 모르는 단어는 [`glossary.md`](./glossary.md) 참조.

---

## 📁 파일 1: `decisions-final.md` (소규모 수정)

### Diff 1-1: 리스크 % 통일 (L53, L65)

**Before**:
```markdown
#### Strategy A: 추세 추종 (Trend-Following)
...
포지션: ATR 기반 변동성 조정 사이징, 트레이드당 리스크 1%

#### Strategy B: 평균 회귀 (Mean Reversion)
...
포지션: 고정 비율, 트레이드당 리스크 2%
```

**After**:
```markdown
#### Strategy A: 추세 추종 (Trend-Following)
...
포지션: ATR 기반 변동성 조정 사이징, 트레이드당 리스크 1%

#### Strategy B: 평균 회귀 (Mean Reversion)
...
포지션: ATR 기반 변동성 조정 사이징, 트레이드당 리스크 1%
(평균회귀는 일반적으로 신뢰도가 낮으므로 트렌드와 동일 또는 낮은 리스크 유지)
```

**근거**: 감사관 LC6 — 2% 리스크는 직관과 반대. 통일.

---

### Diff 1-2: 일일 손실 임계값 통일 (L81, L91)

**Before**:
```markdown
| 일일 손실 한도 | -3% → 당일 매매 중단 |
...
| L2 | BTC 24h 내 -10% OR 일일 -2% | 전 포지션 청산, 12h 중단 |
```

**After**:
```markdown
| 일일 손실 소프트 한도 | -2% → 포지션 50% 축소 + 당일 신규 진입 차단 |
| 일일 손실 하드 한도 | -3% → 전 포지션 청산 + 24h 중단 |
...
| L2 | BTC 24h 내 -10% (비대칭 시장 급락) | 전 포지션 청산, 12h 중단 |
```

**근거**: 감사관 LC1 — 기존에는 -2.5%에 L2가 청산해서 -3% 규칙이 dead code. 소프트/하드 2단계로 분리하고, L2는 BTC 급락 전용으로 축소.

---

### Diff 1-3: Strategy B 일봉 기준 명시 (Part 2-1 B)

**Before**:
```markdown
#### Strategy B: 평균 회귀 (Mean Reversion)
진입: 가격 > 200일 MA (상승 추세에서만 역추세 매수)
      AND RSI(4) < 25 (극단 과매도)
청산: RSI(4) > 50
      OR 5일 경과
      OR 하드 스톱 -8%
```

**After**:
```markdown
#### Strategy B: 평균 회귀 (Mean Reversion)
(원 논문: Larry Connors 스타일, 일봉 기반)

진입: 가격 > 200일 MA (일봉 기준)
      AND RSI(4) < 25 (일봉 기준 극단 과매도)
청산: RSI(4) > 50
      OR 5 거래일 경과
      OR 하드 스톱 -8%

주: Week 1에서 일봉 기반 복제를 먼저 수행. 4시간봉 적용은 별도 실험.
```

---

### Diff 1-4: 킬 크라이테리아 타임라인 재정의 (Part 11)

**Before**:
```markdown
**8주 타임 박스 시작 시점**: Week 1 Day 1

**체크포인트:**
- Week 3: 복제 완료 → Sharpe > 0.8? (수수료 포함)
  - Fail → Week 4를 "전략 패밀리 탐색"에 사용
- Week 5: Freqtrade 이식 + 동일 결과 재현?
  - Fail → 프레임워크 문제 디버그
- Week 8: 페이퍼 트레이딩 시작 + 초기 결과 OK?
  - Fail → 킬 조건 발동
```

**After**:
```markdown
**타임 박스 시작**: Week 1 Day 1

**2단계 킬 크라이테리아:**

### Stage 1 — 8주 "연구 계속 여부" 판단
- Week 3: 노트북 복제 완료 → 사전 지정 파라미터 Sharpe > 0.8?
  - Fail → Week 4 전략 패밀리 탐색
- Week 5: Freqtrade 이식 + 노트북 결과 재현?
  - Fail → 프레임워크 or 포팅 문제 디버그
- **Week 8: 페이퍼 트레이딩 초기 2주 결과 평가** (페이퍼 시작 Week 6)
  - Pass: 전략 유지, 추가 2주 페이퍼 진행
  - Fail: **전략 패밀리 교체** OR 연구 모드 전환 (라이브 무한 연기)

### Stage 2 — 12주 "라이브 투입 여부" 판단
- Week 9: 페이퍼 4주 완료
- Week 10~11: 대시보드 + Cloudflare Tunnel 세팅
- **Week 12: 라이브 투입 게이트**
  - 모두 충족 시: 백테스트 Sharpe > 1.0, DSR > 0.5, 페이퍼 4주 대비 70%+
  - Fail: 라이브 연기, 페이퍼 유지 또는 전략 재검토

**주의**: 8주 킬은 "라이브 가드"가 아닌 "연구 방향 재평가".
라이브 투입은 구조상 Week 12+에만 가능.
```

**근거**: 감사관 LC3/LC4 — 원래 타임라인은 수학적으로 킬이 라이브 이전에 항상 발동하게 되어 있었음. 2단계로 재정의.

---

### Diff 1-5: 데이터 기간 고정 (Part 9)

**Before**:
```markdown
- **기간**: 2021~2026 (5년, 사용자 선택)
```

**After**:
```markdown
- **기간**: 2021-01-01 ~ 2026-04-12 (Day 0 당일 기준 고정)
- **데이터 freeze**: Week 1 Day 1 수집 직후 Parquet SHA256 해시 기록 → Week 2 이후 동일 데이터 보장
```

---

## 📁 파일 2: `architecture.md` (기술 오류 수정)

### Diff 2-1: DB 스키마 순서 수정 (Part 3)

**Before**:
```sql
CREATE TABLE trades (
    ...
    signal_id           UUID REFERENCES signals(signal_id),  -- ❌ 아직 없음
    ...
);

CREATE TABLE signals (
    ...
);
```

**After**:
```sql
-- signals를 먼저 생성
CREATE TABLE signals (
    signal_id       UUID PRIMARY KEY,
    time            TIMESTAMPTZ NOT NULL,
    pair            TEXT NOT NULL,
    strategy_name   TEXT NOT NULL,
    side            TEXT NOT NULL,
    confidence      NUMERIC,
    indicators      JSONB,
    regime          TEXT,
    filters_passed  TEXT[],
    was_executed    BOOLEAN,
    skip_reason     TEXT
);

-- trades는 signals 참조
CREATE TABLE trades (
    trade_id            UUID PRIMARY KEY,
    ...
    signal_id           UUID REFERENCES signals(signal_id),
    ...
);
```

---

### Diff 2-2: Docker secrets 현실화 (Part 4-7)

**Before**:
```yaml
services:
  postgres:
    environment:
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
...
secrets:
  db_password:
    external: true
  upbit_key:
    external: true
  cf_tunnel_token:
    external: true
```

**After**:
```yaml
services:
  postgres:
    environment:
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    secrets:
      - db_password

  strategy-engine:
    secrets:
      - upbit_key
      - upbit_secret
    environment:
      - UPBIT_API_KEY_FILE=/run/secrets/upbit_key
      - UPBIT_API_SECRET_FILE=/run/secrets/upbit_secret

  cloudflared:
    image: cloudflare/cloudflared:latest
    command: tunnel --no-autoupdate run
    environment:
      - TUNNEL_TOKEN=${CLOUDFLARE_TUNNEL_TOKEN}  # _FILE 제거
    env_file:
      - ./secrets/.cloudflared.env

secrets:
  db_password:
    file: ./secrets/db_password.txt
  upbit_key:
    file: ./secrets/upbit_key.txt
  upbit_secret:
    file: ./secrets/upbit_secret.txt
```

**주입 흐름 (수정)**:
```
Startup script:
  1. macOS Keychain에서 시크릿 읽기 (security find-generic-password)
  2. ./secrets/ 디렉토리에 임시 파일 생성 (권한 600)
  3. cloudflared용 .env 파일 생성
  4. docker compose up
  5. 컨테이너 기동 후 임시 파일 shred + 삭제

Shutdown script:
  1. docker compose down
  2. ./secrets/ 정리 확인
```

**근거**: 감사관 T1/T2 — `external: true`는 Swarm 전용. `TUNNEL_TOKEN_FILE`은 cloudflared가 지원 안 함.

---

### Diff 2-3: 대시보드 → 업비트 경로 명시 (Part 4-5)

**Before** (undefined):
```
POST /api/controls/manual-buy   (2단계 확인)
POST /api/controls/manual-sell  (2단계 확인)
```

**After**:
```
## 대시보드 수동 매매 경로

흐름:
  Browser
    → Cloudflare Tunnel (HTTPS)
    → dashboard-backend (FastAPI)
    → Freqtrade REST API (내부 네트워크, 토큰 인증)
    → strategy-engine (Freqtrade 내부 로직)
    → pyupbit/ccxt
    → 업비트 API

**보안 원칙**:
- Upbit API 키는 **strategy-engine 컨테이너만 보유**
- dashboard-backend는 Upbit 키 접근 권한 없음
- dashboard-backend → Freqtrade 통신은 내부 Docker 네트워크의 별도 토큰
- Cloudflare Tunnel은 dashboard-backend만 노출 (engine/DB는 노출 0)

API 엔드포인트 (실제):
  POST /api/controls/manual-buy    → Freqtrade /api/v1/forcebuy
  POST /api/controls/manual-sell   → Freqtrade /api/v1/forcesell
  POST /api/controls/pause         → Freqtrade /api/v1/stop
  POST /api/controls/resume        → Freqtrade /api/v1/start
  POST /api/controls/liquidate-all → Freqtrade /api/v1/forcesell (all pairs)
```

**근거**: 감사관 T5 — 대시보드 → 업비트 경로 미정의 = Cloudflare 노출 서비스가 Upbit 키 보유 가능성 = 보안 구멍.

---

### Diff 2-4: Hypertable 보조 인덱스 추가 (Part 3)

**After** (CREATE TABLE 다음 추가):
```sql
-- 심볼 기반 조회 최적화
CREATE INDEX ON ohlcv_1m (exchange, symbol, time DESC);
CREATE INDEX ON ohlcv_4h (exchange, symbol, time DESC);

-- 거래 조회 최적화
CREATE INDEX ON trades (pair, timestamp_utc DESC);
CREATE INDEX ON trades (strategy_name, timestamp_utc DESC);
CREATE INDEX ON signals (pair, time DESC);
```

---

### Diff 2-5: regime_states 스키마에 pair 추가

**Before**:
```sql
CREATE TABLE regime_states (
    time        TIMESTAMPTZ NOT NULL,
    regime      TEXT NOT NULL,
    ...
    PRIMARY KEY (time)
);
```

**After**:
```sql
CREATE TABLE regime_states (
    time        TIMESTAMPTZ NOT NULL,
    pair        TEXT NOT NULL,   -- 코인별 레짐 (또는 'BTC_GLOBAL')
    regime      TEXT NOT NULL,
    adx_4h      NUMERIC,
    ma200_dir   TEXT,
    atr_pct     NUMERIC,
    PRIMARY KEY (time, pair)
);

-- Note: Week 1에서는 'BTC_GLOBAL' 하나만 사용.
-- Phase 6에서 코인별 레짐 분류 시 여러 레코드로 확장.
```

---

## 📁 파일 3: `week1-plan.md` (전면 재작성)

### 주요 변경 요약

사용자 결정에 따라 Week 1 플랜을 전면 재구성:
1. **일봉 기반 복제를 먼저** (Padysak 원 논문과 동일)
2. **앙상블은 Week 1 제외** (Week 2로 이동)
3. **4시간봉 실험은 Day 5로 이동** (일봉이 작동 확인된 후)
4. **치명적 버그 5개 모두 수정**
5. **git init, requirements.lock, 데이터 해시** 추가
6. **사전 지정 파라미터 vs 민감도 그리드 분리**

### 새 Week 1 일정

| Day | 작업 | 주요 산출물 |
|-----|------|-----------|
| Day 1 | 환경 세팅 + git init + 데이터 수집 (일봉 + 4h) | 프로젝트 스켈레톤, 2개 Parquet, SHA256 |
| Day 2 | Strategy A (추세) **일봉 구현** + 사전 지정 파라미터 백테스트 | A 일봉 결과 |
| Day 3 | Strategy B (평균회귀) **일봉 구현** + 사전 지정 파라미터 백테스트 | B 일봉 결과 |
| Day 4 | 강건성 체크: 연도별 분할 + 민감도 그리드 (참고용) | 민감도 차트 |
| Day 5 | **4시간봉 포팅** (동일 전략, 1200/120/60 윈도우) | 4h 결과 비교 |
| Day 6 | 종합 리포트 + Go/No-Go 결정 | `week1_report.md` |
| Day 7 | 사용자 리뷰 + Week 2 계획 | Week 2 초안 |

### Go/No-Go 기준 (수정됨)

**사전 지정 파라미터 기준 (민감도 그리드 최고값 아님!)**:
- 일봉 Strategy A: Sharpe > 0.8
- 일봉 Strategy B: Sharpe > 0.5 (평균회귀는 보수적 기준)
- MDD < 50% (BTC 자체가 75% 드로다운을 겪었으므로 완화)
- 각 연도 중 최소 2개 연도에서 양수 수익 (**Buy&Hold 대비 의미 있는 필터**)
- 4시간봉은 **참고용**, Week 1 킬 기준 아님

### 주요 코드 수정 (Day 2 예시)

**Strategy A — 일봉 기반**:
```python
# 데이터: Upbit KRW-BTC daily
df_d = pd.read_parquet('data/KRW-BTC_1d_frozen_20260412.parquet')
close = df_d['close']
high = df_d['high']
low = df_d['low']
volume = df_d['volume']

# 지표 — 일봉 스케일
ma200 = close.rolling(window=200).mean()  # ✅ 진짜 200일
donchian_high_20 = high.rolling(window=20).max().shift(1)  # ✅ 20일
donchian_low_10 = low.rolling(window=10).min().shift(1)    # ✅ 10일
vol_avg_20 = volume.rolling(window=20).mean()

# ATR — Wilder 스무딩 (ta 라이브러리)
from ta.volatility import AverageTrueRange
atr_14 = AverageTrueRange(high=high, low=low, close=close, window=14).average_true_range()

# 진입 (마스크)
entry = (
    (close > ma200) &
    (close > donchian_high_20) &
    (volume > vol_avg_20 * 1.5)
)

# 청산: Donchian 하단 이탈만 마스크로
exit_ = close < donchian_low_10

# vectorbt에게 스톱 파라미터 전달 (버그 #3 해결)
pf_a = vbt.Portfolio.from_signals(
    close=close,
    entries=entry,
    exits=exit_,
    sl_stop=0.08,  # 하드 스톱 -8%
    ts_stop=(atr_14 * 1.5) / close,  # ATR 트레일링 (비율)
    init_cash=1_000_000,
    fees=0.0005,
    slippage=0.0005,
    freq='1d'
)

pf_a.stats()
```

**Strategy B — 일봉 기반**:
```python
import ta
rsi4 = ta.momentum.RSIIndicator(close=close, window=4).rsi()

entry = (close > ma200) & (rsi4 < 25)
exit_ = rsi4 > 50

# 시간 스톱 (버그 #4 해결)
pf_b = vbt.Portfolio.from_signals(
    close=close,
    entries=entry,
    exits=exit_,
    td_stop=pd.Timedelta('5d'),  # 5 거래일 시간 스톱
    sl_stop=0.08,
    init_cash=1_000_000,
    fees=0.0005,
    slippage=0.0005,
    freq='1d'
)
```

**앙상블 없음 (Week 2로 이동)**.

### 데이터 수집 (Day 1) — 타임존 & 해시 추가

```python
import pyupbit
import pandas as pd
import hashlib
from pathlib import Path

# 1. 일봉 5년치
df_daily = pyupbit.get_ohlcv_from(
    ticker="KRW-BTC",
    interval="day",
    fromDatetime="2021-01-01",
    to="2026-04-12"
)

# 2. 4시간봉 5년치
df_4h = pyupbit.get_ohlcv_from(
    ticker="KRW-BTC",
    interval="minute240",
    fromDatetime="2021-01-01",
    to="2026-04-12"
)

# 3. 타임존 localize (버그: 원래 없었음)
for df in [df_daily, df_4h]:
    df.index = df.index.tz_localize('Asia/Seoul').tz_convert('UTC')

# 4. Gap detection
def check_gaps(df, freq):
    expected = pd.date_range(start=df.index[0], end=df.index[-1], freq=freq)
    missing = expected.difference(df.index)
    return len(missing), missing

daily_gaps, _ = check_gaps(df_daily, '1d')
h4_gaps, _ = check_gaps(df_4h, '4h')
print(f"Daily gaps: {daily_gaps}, 4h gaps: {h4_gaps}")

# 5. 저장 + 해시
Path('data').mkdir(exist_ok=True)
df_daily.to_parquet('data/KRW-BTC_1d_frozen_20260412.parquet')
df_4h.to_parquet('data/KRW-BTC_4h_frozen_20260412.parquet')

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

with open('data/data_hashes.txt', 'w') as f:
    f.write(f"KRW-BTC_1d_frozen_20260412.parquet: {sha256_file('data/KRW-BTC_1d_frozen_20260412.parquet')}\n")
    f.write(f"KRW-BTC_4h_frozen_20260412.parquet: {sha256_file('data/KRW-BTC_4h_frozen_20260412.parquet')}\n")
```

### Day 1 추가 작업

```bash
# Git 초기화 (추가됨)
cd /Users/kyounghwanlee/Desktop/coin-bot
git init
git add docs/ .gitignore
git commit -m "Day 0: initial docs and decisions"

# research 디렉토리는 별도 리포로 나중에 (Week 2+)
# 또는 같은 리포의 서브디렉토리로 유지

# requirements.lock 생성 (재현성)
pip install uv  # 또는 pip-tools
uv pip compile requirements.txt -o requirements.lock
git add requirements.txt requirements.lock
git commit -m "Day 0: pin dependencies"
```

### 민감도 그리드 변경 (Day 4)

**Before**: ±20% 변동 → 3×3×3×3 = 81 조합 → 최고값 보고
**After**:
- **사전 지정 파라미터(pre-registered)만 Go/No-Go에 사용**
- 민감도 그리드는 **참고용 시각화만**:
  - MA ∈ [100, 150, 200, 250, 300] (더 넓게)
  - Donchian ∈ [10, 15, 20, 30, 40]
  - RSI 임계 ∈ [20, 25, 30]
- **등고선 차트**로 성과 평탄(robust) vs 뾰족(overfit) 시각화
- 민감도 결과는 Week 2 DSR의 `N_trials` 입력으로 사용

---

## ✅ 변경 사항 요약

| 파일 | 변경 수 | 심각도 |
|------|:------:|:------:|
| `decisions-final.md` | 5개 diff | 문서 일관성 |
| `architecture.md` | 5개 diff | 기술 정확성 |
| `week1-plan.md` | 전면 재작성 | 버그 5개 + 전략 방향 전환 |

### 유지되는 것 (건강한 결정)

- Upbit 거래소 메인
- Freqtrade (Week 4+)
- PostgreSQL + TimescaleDB
- Cloudflare Tunnel
- LLM Phase 10+ 연기
- 학습 프로젝트 재정의
- 주 단위 승인
- GitHub 비공개 × 3

### 제거/이동

- ~~Week 1 앙상블~~ → Week 2로 이동
- ~~4시간봉 즉시 복제~~ → Day 5 실험으로 축소
- ~~81 조합 grid의 최고값 보고~~ → 사전 지정 파라미터 + 참고용 grid

---

## 🎬 승인 요청

아래 중 하나로 응답해주세요:

### Option 1: 전체 승인
```
"Day 0 진행"
```
→ 위 모든 diff를 일괄 적용, week1-plan.md 전면 재작성, 완료 후 검증 리포트 제출

### Option 2: 부분 수정
```
"Diff X-Y 수정: [내용]"
```
→ 해당 diff만 수정하고 재제시

### Option 3: 추가 질문
```
"질문: [내용]"
```
→ 기술적 설명 후 재확인

**기본값: Option 1 권장**. 모든 수정은 감사관 지적을 직접 반영한 것이며, 구조적 방향(Upbit/Freqtrade/Cloudflare Tunnel/LLM Phase 10+/학습 프로젝트)은 그대로 유지됩니다.

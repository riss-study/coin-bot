# Day 0 — 긴급 수정 사항

> **외부 감사관 재검증 결과, Week 1 Day 1 시작 전 반드시 수정해야 할 치명적 버그와 모순이 발견되었습니다.**
>
> **현재 상태로는 Day 1 시작 불가**. 코드가 실행 중 크래시하거나, 돌더라도 의미 없는 숫자를 반환합니다.

---

## 🔴 심각도 요약

| 심각도 | 개수 | 내용 |
|-------|:---:|------|
| **CATASTROPHIC** | 1 | MA200이 30일 MA로 잘못 계산됨 — 전략의 근간 무너짐 |
| **HIGH (코드 크래시)** | 4 | 변수 미정의, 앙상블 자본 이중계산 |
| **HIGH (문서 모순)** | 4 | 일일 손실 임계값, 킬 타임라인 불가능 |
| **MEDIUM (기술 오류)** | 5 | Docker secrets, 스키마, TZ, 재현성 |
| **LOW (개선 권고)** | 많음 | 점검/강건성/관측성 개선안 |

---

## Part 1: 치명적 코드 버그 (Week 1 Day 1 시작 전 필수 수정)

### 🔴 BUG #1: MA200이 30일 MA로 잘못 계산됨 (CATASTROPHIC)

**위치**: `week1-plan.md` Day 2 Strategy A 코드
```python
ma200 = close.rolling(window=6*30).mean()  # 4h * 6 * 30 ≈ 30일
```

**문제**: 주석조차 "30일"이라고 적혀있는데 변수명은 `ma200`. 실제로는 **30일 MA**. 4시간봉에서 200일 MA는 **1,200 바**(200 × 6)여야 함.

**영향**: 전략 A와 B의 공통 추세 필터(`close > ma200`)가 **6.67배 짧은 윈도우**로 작동. 두 전략 모두 무효. Week 1 전체 결과가 무의미.

**수정**:
```python
ma200 = close.rolling(window=1200).mean()  # 200 * 6 = 1200 bars on 4h
```

---

### 🔴 BUG #2: Donchian 윈도우도 같은 실수 (HIGH)

**위치**: Day 2 Strategy A
```python
donchian_high_20 = high.rolling(window=20).max().shift(1)
donchian_low_10 = low.rolling(window=10).min().shift(1)
```

**문제**: 20 바 = 3.33일, 10 바 = 1.67일. Padysak 스펙은 "일" 단위.

**수정**:
```python
donchian_high_20 = high.rolling(window=120).max().shift(1)  # 20 days * 6
donchian_low_10 = low.rolling(window=60).min().shift(1)     # 10 days * 6
```

---

### 🔴 BUG #3: `entry_price` 미정의 (코드 크래시) (HIGH)

**위치**: Day 2 Strategy A 청산 코드
```python
exit_ = (
    (close < donchian_low_10) |
    (close < entry_price - 2 * atr_14)
)
```

**문제 1**: `entry_price`라는 변수가 어디에도 정의되지 않음 → `NameError`로 크래시
**문제 2**: Boolean 마스크로 "가격 < 진입가 - 2 ATR" 표현 불가. vectorbt는 `from_signals`의 불리언 exit에 이걸 표현할 방법이 없음.
**문제 3**: 결정 문서는 "1.5x ATR 트레일링" (decisions-final.md)인데 코드는 "2 ATR" — 파라미터 드리프트

**수정**:
```python
pf = vbt.Portfolio.from_signals(
    close=close,
    entries=entry,
    exits=exit_trend_break,  # Donchian(10) 하단만
    sl_stop=atr_14 * 2 / close,  # 2x ATR 손절 (비율로 변환)
    ts_stop=atr_14 * 1.5 / close,  # 1.5x ATR 트레일링
    init_cash=1_000_000,
    fees=0.0005,
    slippage=0.0005,
    freq='4h'
)
```

---

### 🔴 BUG #4: `bars_held` 미정의 (코드 크래시) (HIGH)

**위치**: Day 3 Strategy B
```python
exit_ = (
    (rsi4 > 50) |
    (bars_held > 5 * 6)  # 5일
)
```

**문제**: `bars_held`는 존재하지 않는 변수. vectorbt는 Boolean exit mask에서 "보유 바 수"를 직접 제공하지 않음.

**수정**:
```python
pf = vbt.Portfolio.from_signals(
    close=close,
    entries=entry_b,
    exits=(rsi4 > 50),
    td_stop=pd.Timedelta('5d'),  # vectorbt의 시간 기반 청산
    init_cash=1_000_000,
    fees=0.0005,
    freq='4h'
)
```

---

### 🔴 BUG #5: 앙상블이 자본 이중 계산 (Sharpe 부풀림) (HIGH)

**위치**: Day 4 앙상블 코드
```python
pf_a = vbt.Portfolio.from_signals(close, entry_a, exit_a, init_cash=500_000, ...)
pf_b = vbt.Portfolio.from_signals(close, entry_b, exit_b, init_cash=500_000, ...)
ensemble_value = pf_a.value() + pf_b.value()
```

**문제**:
1. 두 개의 독립 계좌를 합산 → A와 B가 동시에 진입하면 실제로는 과레버리지 상태가 되는데 시뮬레이션은 각각 50만원씩 안전하다고 봄
2. 한 전략이 현금 보유 중일 때 다른 전략의 변동성을 희석 → **Sharpe 인위적 상승**
3. 연간 리밸런싱 없음 → 50/50 드리프트

**수정**: 단일 포트폴리오에 결합된 진입/청산 마스크 사용
```python
# 결합 마스크 (둘 다 같은 방향이면 진입, 반대면 건너뜀)
entry_combined = entry_a | entry_b
exit_combined = exit_a & exit_b  # 또는 별도 로직

pf_ensemble = vbt.Portfolio.from_signals(
    close=close,
    entries=entry_combined,
    exits=exit_combined,
    size=0.5,  # 각 신호에 50% 할당
    size_type='targetpercent',
    init_cash=1_000_000,
    fees=0.0005,
    freq='4h'
)
```

**또는 Week 1에서 앙상블 연기**: A와 B 개별 결과만 확인하고, 앙상블은 Week 2에서 제대로 구현.

---

### 🟡 BUG #6: Padysak/Vojtko는 일봉 기반, 4시간봉 "복제"는 복제가 아님 (STRATEGIC)

**문제**: Padysak/Vojtko 원 논문은 **일봉 기반**. 4시간봉에서 돌리는 건 복제가 아니라 "파생 전략".

**영향**: Week 1 전체 프레임이 잘못됨. "Padysak 복제"라고 부를 수 없음.

**수정 옵션**:
- **Option A (권장)**: Week 1 Day 2~4를 **일봉 기반**으로 먼저 돌림. 재현 성공 후 Day 5에 4시간봉으로 포팅 실험.
- **Option B**: "Padysak-영감을 받은 A/B/C" 로 재명명 + 원 논문 숫자는 참고로만.

---

## Part 2: 문서 모순 (논리적 붕괴)

### 🔴 모순 #1: 일일 손실 -2% vs -3% 불일치

**decisions-final.md L81**: `일일 손실 한도 -3% → 당일 매매 중단`
**decisions-final.md L91**: `L2 서킷브레이커: BTC 24h -10% OR 일일 -2% → 전 포지션 청산`

→ -2.5%에 도달하면 L2가 발동해서 전량 청산하지만, -3% "당일 매매 중단"은 절대 발동 안 됨. **-3% 규칙이 dead code**.

**수정 제안**: 하나로 통일
```
일일 손실 -2% → 포지션 50% 축소 + 당일 매매 중단
일일 손실 -3% → 전 포지션 청산 + 24시간 중단
```

---

### 🔴 모순 #2: 킬 크라이테리아 타임라인 수학적 불가능

**사실들**:
- 페이퍼 트레이딩은 Week 6~9 (4주)
- 라이브 전환은 "페이퍼 4주 완료" 필수
- 킬 크라이테리아는 Week 8 발동

**문제**: Week 8 = 페이퍼 시작 후 2주 밖에 안 됨. **4주 페이퍼는 Week 9에야 완료** → **라이브는 항상 Week 10+ 에만 가능**. 하지만 킬은 Week 8에 발동 → **킬이 라이브 이전에 항상 작동**.

**결과**: 8주 킬은 "라이브 투입 가드"가 아니라 **"연구 계속 여부 판단"** 역할. 문서는 전자처럼 기술했지만 실제로는 후자.

**수정 제안**: 킬 크라이테리아를 재정의
```
Week 8 킬 체크 = "Week 6~8 페이퍼 초기 2주 결과가 살아있는가?"
  - Pass: Week 9~11 Freqtrade 페이퍼 유지
  - Fail: 전략 패밀리 교체

Week 12 = 라이브 전환 체크 (페이퍼 4주 + 백테스트 70%+)
```

---

### 🟡 모순 #3: 리스크 퍼센트 비일관 (A: 1%, B: 2%)

**문제**: Strategy A는 트레이드당 1% 리스크, B는 2% 리스크. 근거 없음.
**직관**: 평균회귀는 일반적으로 **낮은 신뢰도** → 낮은 리스크가 맞음. 2%는 거꾸로.

**수정**: 둘 다 1%로 통일 (또는 B를 0.5%로 낮춤).

---

### 🟡 모순 #4: Week 8 checkpoint "페이퍼 시작" 오기

**Part 3**: 페이퍼 시작 Week 6
**Part 11 Week 8**: "페이퍼 트레이딩 시작 + 초기 결과 OK?"

→ "시작"이 아니라 "시작 후 2주 경과 초기 평가"로 수정.

---

## Part 3: 아키텍처 기술 오류

### 🟠 오류 #1: Docker secrets `external: true`는 Swarm 모드 필요

**architecture.md**:
```yaml
secrets:
  db_password:
    external: true
```

**문제**: `external: true`는 **Docker Swarm 모드**에서만 동작. 일반 `docker compose`에서는 파일 기반이어야 함.

**수정**:
```yaml
secrets:
  db_password:
    file: ./secrets/db_password.txt
  upbit_key:
    file: ./secrets/upbit_key.txt
  # ...
```
그리고 `./secrets/` 디렉토리는 macOS Keychain에서 컨테이너 시작 전에 임시 파일로 주입하는 스크립트 작성.

---

### 🟠 오류 #2: cloudflared `TUNNEL_TOKEN_FILE` 미지원

**architecture.md**:
```yaml
environment:
  - TUNNEL_TOKEN_FILE=/run/secrets/cf_tunnel_token
```

**문제**: cloudflared 공식 이미지는 `TUNNEL_TOKEN`만 지원. `_FILE` 변형은 postgres, mariadb 등 일부 이미지에만 있음.

**수정**: 호스트에서 env var로 직접 주입
```yaml
environment:
  - TUNNEL_TOKEN=${CLOUDFLARE_TUNNEL_TOKEN}
```
그리고 Keychain → shell env → docker-compose 흐름.

---

### 🟠 오류 #3: DB 스키마 외래키 순서 오류 (CREATE 실패)

**architecture.md**:
```sql
CREATE TABLE trades (
    ...
    signal_id UUID REFERENCES signals(signal_id),  -- ❌ signals 아직 없음
    ...
);

CREATE TABLE signals (...);  -- 이것이 trades 뒤에 위치
```

**문제**: 최초 실행 시 `relation "signals" does not exist` 에러.

**수정**: `signals` 테이블을 먼저 `CREATE`하거나 `ALTER TABLE`로 나중에 FK 추가.

---

### 🟠 오류 #4: 대시보드 → 업비트 주문 경로 미정의 (보안 구멍)

**문제**: `POST /api/controls/manual-buy`가 업비트에 어떻게 주문을 넣는지 정의 안 됨. 가능한 경로:
1. dashboard-backend가 업비트 API 키 보유 → **Cloudflare Tunnel에 노출된 서비스가 키 보유 = 보안 위반**
2. dashboard-backend가 Freqtrade REST API 호출 → 문서 없음
3. DB `commands` 테이블 polling → 문서 없음

**수정**: 옵션 2 채택 명시
```
대시보드 수동 매매 흐름:
  Browser → Cloudflare Tunnel → dashboard-backend
    → Freqtrade REST API (내부 토큰)
    → strategy-engine
    → Upbit API (키는 engine 컨테이너에만 존재)
```

---

### 🟠 오류 #5: 타임존 처리 누락

**문제**:
- pyupbit는 **KST-naive** 타임스탬프 반환
- FRED API는 **UTC**
- 바이낸스는 **UTC**
- Week 1 노트북 어디에도 localize/convert 없음 → **9시간 silent 오프셋**

**수정**: 데이터 수집 직후
```python
df.index = df.index.tz_localize('Asia/Seoul').tz_convert('UTC')
```

---

## Part 4: 백테스트 엄밀성 문제

### 🟡 R1: Week 1 Go/No-Go가 plain Sharpe만 사용 (데이터 스누핑 위험)

**문제**: Day 5 민감도 그리드 = 81 조합. Day 6 Go 기준 = "최소 1개 전략 Sharpe > 0.8". **81개 중 최고값을 보면 노이즈만으로도 거의 항상 통과**.

**수정**:
- Day 6 Go 기준: **사전 지정(pre-registered) 파라미터만** 평가
- 민감도 그리드는 **참고용**, Week 2 DSR에 N_trials=81 입력

---

### 🟡 R2: ATR 계산이 Wilder 스무딩 아님

**Week 1 코드**: ATR을 SMA로 계산
**표준**: Wilder의 RMA 스무딩 사용 (`ta` 라이브러리 기본값)

**수정**:
```python
from ta.volatility import AverageTrueRange
atr_14 = AverageTrueRange(high=high, low=low, close=close, window=14).average_true_range()
```

---

### 🟡 R3: 데이터 프리즈 (날짜 고정) 누락

**문제**: Week 1에서 "2021-01-01 ~ 오늘"로 다운로드 → Week 2 재실행 시 새 데이터 포함 → 결과 silently 변함.

**수정**: 고정 종료일 지정 + Parquet SHA256 해시 기록.

---

## Part 5: 누락된 것들

1. **`git init` 누락** — .gitignore는 있지만 Git 초기화는 안 나옴
2. **Pinned versions 없음** — `requirements.lock` 생성 필요
3. **단위 테스트 없음** — Part 8 "엄격한 테스트"라고 했지만 Week 1에 테스트 0개
4. **바이낸스 교차 검증 안 씀** — 데이터 sanity check에 거의 공짜
5. **"피크 대비 -10%"에서 피크 정의 없음** — ATH? 롤링? 포지션 개시?
6. **"일일" 시계 기준 없음** — KST 자정? UTC 자정?
7. **업비트 점검 시간 감지 방법 없음** — "사전 공지 감지"만 명시
8. **백업 전략 없음** — `pg_dump` 스케줄, 복구 drill

---

## 🛠 Day 0 실행 계획

### Day 0 오전 (2시간): 코드 버그 수정

- [ ] `week1-plan.md` BUG #1~#5 수정 (MA200, Donchian, ATR 스톱, 시간 스톱, 앙상블)
- [ ] BUG #6 결정: 일봉 먼저(Option A) vs "Padysak-영감" 재명명(Option B)
- [ ] 타임존 localize 코드 추가
- [ ] `requirements.lock` 생성 절차 추가
- [ ] `git init` 추가

### Day 0 오후 (1시간): 문서 모순 해결

- [ ] `decisions-final.md` 모순 #1 수정 (일일 손실 임계값 통일)
- [ ] `decisions-final.md` 모순 #2 수정 (킬 크라이테리아 타임라인 재정의)
- [ ] `decisions-final.md` 모순 #3 수정 (리스크 % 통일)
- [ ] `decisions-final.md` 모순 #4 수정 (Week 8 체크포인트 문구)

### Day 0 저녁 (1시간): 아키텍처 기술 오류 수정

- [ ] `architecture.md` Docker secrets → file 기반
- [ ] cloudflared TUNNEL_TOKEN (`_FILE` 제거)
- [ ] DB 스키마 순서 수정
- [ ] 대시보드 → Freqtrade REST 경로 명시
- [ ] DB 인덱스 추가 (hypertable secondary index)

### Day 0 종료 후

- [ ] 수정사항 검증 (간단한 sanity 체크)
- [ ] Day 1 시작 가능 상태

---

## 📋 사용자 결정 필요

### 결정 #1: Day 0 실행 방식

- [ ] **A. 제가 직접 모든 수정을 적용** (약 30분~1시간 작업) → 완료 후 검증 요청
- [ ] **B. 각 수정사항별로 승인받으며 진행** (더 느리지만 투명)
- [ ] **C. 제가 수정 diff를 먼저 제시, 승인 후 적용**

### 결정 #2: BUG #6 — Padysak 복제 전략

- [ ] **A. 일봉 기반 복제 먼저** (Week 1 Day 2~3 일봉, Day 4~5 4시간봉 실험) — 권장
- [ ] **B. 4시간봉 그대로 + "Padysak-영감" 재명명** — 빠르지만 원 논문 숫자는 비교 기준 X
- [ ] C. 직접 판단해줘

### 결정 #3: 앙상블 Week 1 포함?

- [ ] **A. Week 1에서 앙상블 제외** — 개별 A, B만 먼저 확인 (권장)
- [ ] **B. Week 1에서 수정된 앙상블 포함** — 버그 #5 제대로 수정
- [ ] C. 직접 판단해줘

---

## 💭 감사관 최종 평가 인용

> **"Not safe to execute as Day 1 start. Five Week-1 code bugs will either crash the notebook or silently produce nonsense numbers. That noise will then be fed into Week 2's walk-forward and DSR machinery, which will dutifully declare 'DSR > 0.5' or '< 0.5' based on nothing, and the 8-week kill criterion will fire (or fail to fire) on garbage. Real money at Week 10+ is downstream of Week 1 correctness."**
>
> **"The good news: the structural decisions (Upbit spot, Freqtrade, TimescaleDB, Cloudflare Tunnel, kill criterion existing at all, LLM deferred to Phase 10, paper-first) are sound. The architecture doc's Phase-by-Phase incremental complexity is excellent. The bugs are concentrated in Week 1 code and a small number of document contradictions — all fixable in a day of focused cleanup."**

**구조적 결정은 건강합니다.** Day 0 1일 집중 수정이면 Day 1을 안전하게 시작할 수 있습니다.

결정 #1~#3에 답변해주시면 Day 0 작업을 진행합니다.

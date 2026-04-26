# V2-Strategy-E (Momentum 추격) sub-plan

Task ID: V2-Strategy-E (V2-06과 병행 리서치 트랙)
Feature: STAGE1-V2-013
Created: 2026-04-26
Status: 계획 박제 — 사용자 명시 승인 대기

박제 출처:
- `docs/decisions-final.md` "Tier 1/2 페어 + W2-03 grid" 박제
- `docs/candidate-pool.md` Strategy A/D Active + Tier 1만 채택
- 사용자 발화 (2026-04-26): "지금도 엄청 올라가는 애들이 있는데 그런거에 대한 시도도 없는게 좀 그런데..? 너무 메인코인만 보는거 같아."
- W2-03 정신: 사전 박제 + DSR + Sharpe>0.8 (cycle 1 #5 cherry-pick 회피)

---

## 0. 동기

V2-06 페이퍼 daemon 가동 중 (BTC_A + ETH_A + BTC_D). 그러나:
- 현재 BTC/ETH **MA200 한참 아래** (-9%/-17%) → Strategy A 진입 X
- 동일 시각 알트 급등 (ORCA +38%, RAY +24% 등)
- Strategy A/D는 일봉 추세 follow → 단기 급등 포착 X

V2-06 4주 페이퍼 trades < 1건 예상. trades ≥ 10 박제 미달 → Go 가능성 낮음.

→ **Strategy E (모멘텀 추격) 신규 리서치 트랙** 병행. V2-06 4주 페이퍼 동안 작업 (사용자 손 비어있음 활용).

---

## 1. 핵심 원칙 (W2-03 cycle 1 #5 회피)

| 원칙 | 적용 |
|------|------|
| **사전 박제** | Strategy E 진입/청산 룰 + 파라미터 + 후보 풀 + Go 기준 — 백테스트 **이전**에 본 sub-plan에서 박제. 백테스트 결과 보고 사후 변경 금지 |
| **DSR 평가** | Bailey & López de Prado 2014 — 다중 검정 보정. Sharpe 단독으로는 cherry-pick 위험 |
| **OOS 분리** | in-sample 2024-01 ~ 2025-12 (24개월). 페이퍼 4주 (2026-04-26~05-24)는 OOS 자연 분리 |
| **자동 결정 (코드)** | Tier 3 후보 풀은 추정 리스트 박제 X. **규칙만 박제 + 시총/거래대금/변동성 자동 필터** |
| **사용자 명시 박제** | sub-plan 본문 + 사용자 명시 승인 ("ㄱㄱ" 또는 명시 채택) 후 착수 |

---

## 2. Strategy E 사전 박제 (변경 금지)

### 2.1 진입 조건 (3개 모두 AND)

```
일봉 close 시점 평가:
  (1) 강한 양봉:    close >= open × 1.05    (당일 +5% 이상)
  (2) 거래량 spike: volume > volume.rolling(20).mean().shift(1) × 2.0
  (3) 단기 돌파:    close > high.rolling(5).max().shift(1)    (5일 고가 돌파)
```

**근거**:
- (1) 5% 양봉 — 알트 평균 변동성 대비 충분히 강한 신호 (BTC/ETH 1~2%, 알트 5~10%)
- (2) 거래량 2배 — Strategy A의 1.5배보다 더 엄격 (false positive 차단)
- (3) 5일 고가 돌파 — Donchian 20일과 다른 단기 (Strategy A와 동시 매매 시 신호 분산)

### 2.2 청산 조건 (어느 하나라도)

```
  (a) Hard SL:      close < entry × 0.95       (-5% 손절, 알트 변동성 고려)
  (b) Trend exit:   close < low.rolling(5).min().shift(1)   (5일 저가 하향 돌파)
  (c) 약화:         close < open × 0.97        (당일 -3% 음봉)
```

**근거**:
- Strategy A 청산 (-8%, Donchian 10일 저가)보다 **더 빠른 청산** — 모멘텀은 wave 짧음
- (c) 당일 -3% — 모멘텀이 식기 시작하는 신호. 빠른 손실 cap

### 2.3 Portfolio 박제

```yaml
fees: 0.0005          # Upbit 0.05% (W2-03 동일)
slippage: 0.0010      # **알트는 0.1%로 상향** (BTC/ETH 0.05%, 알트 horde slippage)
freq: 1D
year_freq: 365 days
init_cash: 1_000_000
stake_amount: 100_000  # cell당
```

**slippage 0.1% 박제 사유**: 알트 시총 낮음 → 매수 시 호가 갭 큼. Upbit KRW 마켓 ORCA/RAY 같은 코인 1억 매수 시 평균 0.1~0.3% 슬리피지 (실측 책무 — V2-07 라이브 진입 시 보정).

### 2.4 동시 매매 제한

```
max_open_positions: 3         # config.yaml 그대로 유지
priority: 진입 신호 발생 순서 (FIFO)
```

알트는 동시 여러 종목 급등 가능. 3 cells 한도 → 가장 먼저 신호 발생한 3개만 매수. 나머지 무시.

---

## 3. Tier 3 후보 풀 (자동 결정, 추정 리스트 박제 X)

### 3.1 필터 규칙 (사전 박제)

```python
# 측정 창 (sub-plan 작성 시점 기준 6개월): 2025-10-26 ~ 2026-04-25 UTC
1. KRW 마켓 전체 (Upbit /v1/market/all isDetails=false 필터)
2. 시총 top 30 (CoinGecko KRW 환산, 측정 창 마지막 일자 스냅샷)
3. 일평균 거래대금 ≥ 100억 KRW (acc_trade_price_24h 측정 창 평균)
4. 24h 변동성 표준편차 ≥ 3% (return.std() × 100)
5. **상장 ≥ 180일** (단명 코인 제거)
6. **상장폐지 위험 X** (Upbit 투자유의 종목 제외)

→ 자동 필터 결과를 **그대로 사용** (사후 추가/제거 금지)
```

### 3.2 Cherry-pick 차단

- 측정 창 종료 후 결과 리스트 발견 → 사용자/Claude가 임의 추가 금지
- 결과 리스트가 비어있거나 ≤ 3 → **Fallback (i)**: Tier 1+2 (BTC/ETH/XRP/SOL/TRX/DOGE) 그대로 + Strategy E 평가
- 결과 리스트 너무 큼 (> 20) → top 20 거래대금 기준 자동 cap

### 3.3 측정 창

```
in-sample:  2024-01-01 ~ 2025-12-31 UTC (24개월, OHLCV 기준)
OOS 검증:   2026-01-01 ~ 2026-04-25 UTC (3.8개월, walk-forward 대신 단순 OOS)
페이퍼:     2026-04-26 ~ (V2-06 자연 OOS 4주)
```

W2-03 v8 측정 창과 다름 (의도) — Strategy A는 BTC 5년, Strategy E는 알트 24개월. Strategy E의 BTC/ETH 평가도 동일 측정 창.

---

## 4. Go 기준 (W2-03 정신 그대로)

### 4.1 Primary

```
Sharpe (in-sample 24개월) > 0.8
AND
DSR_z (Bailey & López de Prado) > 0
```

### 4.2 OOS 검증 (3.8개월)

```
in-sample Go cells의 OOS Sharpe > 0.4 (in-sample의 50%)
AND
OOS trades ≥ 3 (단명 평가 회피)
```

OOS 미달 cell은 **Tier 3 채택 X** (학습 가치만 박제, deprecated 처리는 cycle 종료 시).

### 4.3 Recall mechanism

W2-03과 동일: in-sample Go + OOS Pass → V2-07 라이브 후보 풀 진입. 단 BTC_A/ETH_A/BTC_D와 함께 평가 (V2-07 stake 분배).

### 4.4 사용자 명시 박제

본 sub-plan + 4주 후 결과 보고 → **사용자 명시 승인** 후 V2-07 진입. cycle 1 학습.

---

## 5. 작업 분해 (10~12일, V2-06 4주 내 완료)

| ID | 항목 | 추정 | 산출물 |
|----|------|:----:|--------|
| **C-01** | Tier 3 후보 풀 자동 필터 코드 + 측정 창 결과 박제 | 2d | `research/scripts/v2_tier3_pool.py` + 결과 .json |
| **C-02** | Strategy E signals 함수 + 단위 테스트 | 2d | `research/scripts/strategy_e.py` + sanity (warmup / SL / breakout) |
| **C-03** | in-sample 24개월 grid (Tier 1+2+3 × Strategy E) | 2d | vectorbt portfolio + Sharpe/DSR 통계 |
| **C-04** | OOS 3.8개월 검증 + Go cells 박제 | 2d | `research/notebooks/v2_strategy_e.ipynb` 또는 .py |
| **C-05** | candidate-pool.md v8 박제 + sub-plan 결과 박제 | 1d | docs 갱신 |
| **C-06** | (옵션) 페이퍼 daemon에 Strategy E 통합 | 2d | `engine/engine/strategies/e.py` + config.yaml 신규 cells |
| **C-07** | 사용자 명시 박제 보고 + V2-07 후보 갱신 | 0.5d | handover/메모리 갱신 |

**C-06은 별도 사용자 결정** — V2-06 페이퍼 daemon 중간 변경 = 4주 데이터 일관성 깨짐. 4주 마감 후 V2-07 진입 시점에 통합 권장.

---

## 6. 진입 / 종료 기준

### 진입 (착수 조건)
- ✅ V2-06 페이퍼 daemon 가동 중 (PID 87918)
- ✅ V2-Dashboard D 옵션 완료 (알트 시세 가시화)
- ⏳ **본 sub-plan 사용자 명시 승인**
- ⏳ Tier 3 후보 풀 자동 필터 결과 박제 (C-01 완료 후 결과만 보고, cherry-pick X)

### 종료 (Strategy E 완료 조건)
- in-sample Sharpe>0.8 + DSR>0 cells 박제
- OOS 검증 통과 cells 박제
- candidate-pool.md v8 갱신
- 사용자 명시 박제

### 종료 후 시나리오
- Tier 3 통과 cell 多 → V2-07 stake 분배 (BTC_A/ETH_A/BTC_D + Strategy E cells)
- Tier 3 통과 cell 0 → 학습 가치만 박제. V2-07은 BTC/ETH 그대로
- 페이퍼 V2-06 결과 미달 + Strategy E 통과 → V2-07 Strategy E 단독 진입 검토

---

## 7. 위험 + 완화

| 위험 | 완화 |
|------|------|
| **알트 데이터 부족** (180일 상장 미만 등) | 자동 필터 §3.1 박제 |
| **상장폐지 / 투자유의** | Upbit market_warning 필드 자동 제외 |
| **cycle 1 #5 cherry-pick** | 사전 박제 §2 + Go 기준 §4 변경 금지. 결과 보고 시 미달 cell 그대로 박제 (학습 가치) |
| **cycle 1 #16 외부 API 추측** | CoinGecko 시총 / Upbit ticker 모두 실측 검증 후 코드 작성 |
| **slippage 모델 추정** | 알트 0.1% 박제 + V2-07 라이브 진입 시 실측 보정 책무 (sub-plan §2.3) |
| **실시간 모멘텀 미적용** (4주 페이퍼와 다른 시간대) | Strategy E in-sample/OOS 검증 후 V2-07 라이브 진입 시 통합 |

---

End of V2-Strategy-E sub-plan. Generated 2026-04-26.

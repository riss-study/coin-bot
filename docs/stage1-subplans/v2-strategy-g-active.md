# V2-Strategy-G (Active Multi-pair) sub-plan

Task ID: V2-Strategy-G
Feature: STAGE1-V2-014
Created: 2026-04-26
Status: **사용자 명시 동의 박제됨** ("그렇게 해봐" 2026-04-26)

박제 출처:
- 사용자 발화 (2026-04-26): "에프는 하기 싫어. 활발했으면 좋겠어 나는"
- 일반 봇 운영자 사례 조사 (Freqtrade NFI / Reddit r/algotrading / 한국 변동성돌파 등)
- 위험 박제: For Traders 통계 "set-and-forget 봇 90일 내 52% 깨짐"

---

## 0. 사용자 명시 동의 박제 ⚠️

> "Strategy G는 통계 alpha 검증 X. 빈번 활동 + 학습 + 위험 감수 동의. 손실은 사용자 책임. Stage 1 v2 Go 기준 평가 대상 X. 50만원 한도 내. 일반 봇 운영자 90일 내 52% 깨짐 통계 인지."

사용자 동의 형태: **"그렇게 해봐"** (2026-04-26).

handover #10/11 정신: 본 sub-plan은 통계 검증 절차 (W2-03 Sharpe/DSR) **밖에 있음**. 4주 후 V2-06 Go/No-Go 판정 시 Strategy G는 별도 평가 (학습 가치 vs 손실 통제 관점).

---

## 1. 동기

| 사용자 의도 | 박제 정책 (현재) | 결과 |
|-------------|------------------|------|
| 빈번한 활동 | 통계 우선 (Sharpe>0.8 + DSR>0) | 약세장 hold = 활동 0 |
| 다양한 코인 | Tier 1 BTC/ETH 박제 | 알트 미접근 |

→ Strategy G = **활동 빈도 우선 + 통계 검증 명시 포기 + 후보 풀 확대 + 위험 사용자 책임**.

---

## 2. Strategy G 사전 박제 (변경 금지)

### 2.1 진입 (3 AND)

```
(1) 양봉:    close >= open × 1.02              (+2%)
(2) 거래량:  volume > volume.rolling(20).mean().shift(1) × 1.2
(3) 단기 돌파: close > high.rolling(3).max().shift(1)
```

### 2.2 청산 (어느 하나라도)

```
(a) Hard SL: close <= entry × 0.97              (-3%)
(b) TP:      close >= entry × 1.05              (+5%)
(c) 시간:    bars_held >= 3                     (3일 timeout)
```

### 2.3 Portfolio 박제

```yaml
init_cash: 1_000_000
fees: 0.0005           # Upbit 0.05%
slippage: 0.0010       # 알트 박제 (sub-plan v2-strategy-e §2.3 참조)
freq: 1D
max_open_positions: 10
stake_amount: 50_000   # cell당 (50만 한도 / 10)
```

### 2.4 후보 풀 (동적 자동 결정, 2026-04-27 박제 정정)

```python
# 매 cycle 시작 시 (KST 09:05) 자동 fetch:
1. /v1/market/all isDetails=true KRW 마켓 전체
2. /v1/ticker?markets=... acc_trade_price_24h 기준 정렬
3. top 30 (단순 거래대금 우선)
4. market_warning="NONE" 강제 (투자유의 제외)
5. fetch fail (네트워크 등) 시 → config.yaml 정적 fallback cells 사용

→ 자동 필터 결과를 그대로 사용 (cherry-pick X)
→ 매일 신규 급등 코인 자동 진입 (KRW-TOKAMAK 같은 사례)
```

**박제 정정 사유 (2026-04-27 사용자 보고)**:
- 사용자 발화: "토카막네트워크가 16% 올랐는데 왜 미리 안 샀나?"
- 정적 박제는 측정 시점 (2026-04-25) top 30 = 신규 급등 코인 영구 미접근
- 사용자 의도 ("활발 + 여러 코인 + 신규 급등 잡기") 충족 위해 동적 변경
- cycle 1 #5 회피 유지 (자동 결정, 사람 cherry-pick X)

---

## 3. Go 기준 (없음)

- **Sharpe / DSR / trades 임계 박제 X** — 활동 우선 트랙
- 4주 페이퍼 결과로 판단:
  - 누적 PnL > 0 → V2-07 진입 후보 (별도 한도, 예: 10만원만 Strategy G 배정)
  - 누적 PnL < -10% → 학습 가치 + V2-07 진입 X (사용자 결정)
  - 누적 PnL -10% ~ +0% → 사용자 결정 (계속 vs 종료)

---

## 4. 위험 박제 ⚠️

| 위험 | 정량 |
|------|------|
| **음수 expected value** | 회당 -0.20% (수수료 0.10% + slippage 0.10%) |
| **월 90 trades 가정** | 월 -18% 손실 시나리오 (alpha 0 가정) |
| **Set-and-forget 깨짐** | For Traders 통계 90일 내 52% 봇 fail |
| **알트 폭락 동시 손절** | NFI 류 다페어 봇 흔한 패턴 |
| **도박화** | 5분봉/1시간봉 다지표는 슬롯머신화 위험 (우리는 일봉이라 완화) |

**완화**:
- 일봉 단위 (5m/1h 보다 도박화 위험 낮음)
- 단순 룰 (다지표 합성 X = overfitting 회피)
- max_open=10 분산 + stake 5만 = 단일 cell 손실 cap
- 50만원 라이브 한도 박제 (V2-07 시점)

---

## 5. 작업 분해 (~3일)

| ID | 항목 | 추정 | 산출물 |
|----|------|:---:|--------|
| **G-01** | sub-plan 박제 (본 문서) + 사용자 동의 박제 | 0.5d | 본 파일 |
| **G-02** | research/scripts/strategy_g.py (signals 함수 + 단위 테스트) | 0.5d | sanity |
| **G-03** | KRW 거래대금 top 30 자동 fetch + 박제 | 0.5d | research/notebooks/results/v2_strategy_g_pool.json |
| **G-04** | 빈도 sanity (지난 30일 backtest, 빈도 일평균 측정) | 0.5d | 빈도 ≥ 일 1건 검증 (또는 미달 시 진입 조건 재완화) |
| **G-05** | engine/engine/strategies/g.py + config.yaml 통합 | 0.5d | daemon 통합 |
| **G-06** | dashboard 시각화 (Strategy G cells 표시) | 0.5d | frontend |

---

## 6. 진입 / 종료 기준

### 진입 (착수 조건, 모두 충족 ✓)
- ✅ V2-06 daemon 가동 (PID 87918)
- ✅ V2-Strategy-E No-Go 박제 완료
- ✅ 사용자 명시 동의 (2026-04-26)
- ✅ 위험 박제 §4 사용자 인지

### 종료 (Strategy G 4주 마감 평가)
- 4주 후 V2-06 daemon 가동 통합 평가
- Strategy G 누적 PnL + trades count + win/loss + 빈도 실측

### V2-07 진입 시 별도 한도 (사용자 결정)
- BTC_A/ETH_A/BTC_D (V2-06 검증 통과 시): 40만원 배정
- Strategy G (별도 트랙): 10만원 한도 (사용자 결정 시점에 변경 가능)

---

## 7. V2-06 데이터 일관성 영향 ⚠️

**기존 박제 충돌**:
- V2-06 페이퍼 박제: BTC_A/ETH_A/BTC_D, max_open=3, stake=100_000
- Strategy G 추가: cells 30개, max_open=10, stake=50_000

**옵션 A**: 같은 daemon 통합 → portfolio max_open 확대 (3+10=13). stake 변경 시 BTC_A/ETH_A/BTC_D 평가에도 영향.
**옵션 B**: BTC_A/ETH_A/BTC_D는 stake 100k 그대로, Strategy G는 stake 50k별도. cell별 stake 박제 (config 확장).

→ **옵션 B 채택** (V2-06 페이퍼 일관성 보존). config.yaml에 cell별 `stake_amount_override` 추가.

---

## 8. 비권장 (조사 결과 정직 박제)

- **Freqtrade NFI 5m × 40 페어**: overfitting 심각, CLAUDE.md "데이터 스누핑 금지" 위반
- **Grid Bot 단일 페어**: 트렌드장 미적합, 한국 KRW 시장은 트렌드 자주 발생
- **DCA Martingale**: 베어장 자금 소진 위험

---

End of V2-Strategy-G sub-plan. Generated 2026-04-26.

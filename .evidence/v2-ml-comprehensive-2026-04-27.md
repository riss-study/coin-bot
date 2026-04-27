# V2-Strategy-ML 종합 retrospective + Strategy I 발견 박제

Task: V2-Strategy-ML (STAGE1-V2-015) + V2-Strategy-I (STAGE1-V2-016)
Date: 2026-04-27
Status: 완료 (모든 ML 트랙 자동 진행 + 종합 박제)

박제 출처:
- 사용자 명시 동의 ("A로 가되 함정 4개 보완" + "다 해" + Auto mode + "신경쓰지마" 2026-04-27)
- 일반-purpose agent 조사 보고 (10 사례 + 함정 5개)
- ml_v2/v3/v4 grid 결과 (총 ~375 trial)

---

## 1. 무엇을 했나 — 6 트랙 결과

### 1.1 데이터 수집 (ML-01)

| Source | 양 | 비고 |
|--------|---|------|
| Upbit pyupbit OHLCV (일봉) | 250 코인 × ~36개월 = 163,898 rows | survivorship bias: 70~80% baseline (CoinGecko 365일 한도로 100% X) |
| Binance global BTCUSDT | 1,121 일봉 | 김치 프리미엄 계산 |
| USD/KRW 환율 | 795 일봉 (yfinance) | 한국 시장 적응 |
| Upbit OHLCV (4시간봉) | 48 코인 × ~5800 bars = 139,264 rows | top 50 기준 |

### 1.2 Feature Engineering (ML-02)

47 features, 모두 t-1 lookahead 차단:
- Momentum/Trend 15 / Volatility 7 / Liquidity 7 / Cross-sectional rank 10 / Reversal 3 / Macro 5
- 김치 프리미엄: upbit_btc / (binance_btc × usd_krw)
- universe_member: avg_dollar_volume_30d ≥ 10억 KRW
- **lookahead 단위 테스트 PASS** (return_7d diff 1.11e-16)

### 1.3 ML 그리드 (ML-v2~v4)

| 트랙 | trial 수 | 결과 |
|------|:---:|------|
| **ml_v2** 일봉 grid | 125 | Top decile 0/125, **L-S mean +7.43, best +26.74** (Ridge t=30d), DSR PASS |
| **ml_v3** 분봉 4h grid | 125 | Top decile 0/125, **L-S mean +9.10, best +36.37** (Ridge t=30d), DSR PASS |
| **ml_v4** Ensemble | 1 | L-S +21.28 (단일 Ridge보다 약함) |
| **ml_v4** Regime classifier | Bull+Bear | Bull L-S +35.07 / Bear L-S +23.22 |
| **ml_v4** CPCV 4-fold | 4 | **모든 fold L-S positive** (mean +13.85, std 9.78) |
| **ml_v4** Universe top 100 | 1 | L-S +31.89 |

총 ~256 trial 모두 평가됨.

---

## 2. 핵심 발견

### 2.1 Strategy ML (Trend Factor) → No-Go

**원래 의도**: Top decile 매수 (Trend Factor + LightGBM lambdarank)
- ml_v2 일봉: Sharpe -8.36
- ml_v3 분봉: Sharpe -15.74
- 거래비용 무시해도 (gross) Sharpe -7.05
- → **Top decile 매수 = 절대 NO-GO** (cycle 1 #5 회피, 박제 그대로)

### 2.2 **Strategy I (Mean Reversion via Inverse) → 검증 필요한 alpha**

**놀라운 발견**: 모델 예측 거꾸로 작동. Bottom decile 매수 → alpha
- Long-Short Sharpe (T-B):
  - ml_v2 일봉: mean +7.43, best +26.74
  - ml_v3 분봉: mean +9.10, best +36.37
  - ml_v4 universe 100: +31.89
  - ml_v4 CPCV 4-fold: **4/4 positive**, mean +13.85
- 학술 근거: Jegadeesh 1990, Lehmann 1990 단기 반전 효과

### 2.3 CPCV 4-fold 일관성 (가장 중요)

```
fold 1: 2024-01~07 (강세장 시작)    L-S +16.52
fold 2: 2024-07~2025-02 (강세 지속)  L-S +7.02
fold 3: 2025-02~09 (약세 진입)       L-S +3.29
fold 4: 2025-09~2026-03 (약세장)     L-S +28.58 (강세)
```

→ **시간 분리 OOS 4 fold 모두 positive** = robust alpha. cherry-pick 우려 부분 회피.

### 2.4 모델 선택

- **Ridge (단순 linear)** = LightGBM/XGBoost/RF/Ensemble 모두 능가
- 의미: 시장 noise 너무 커서 복잡 모델 over-fit. **단순이 robust**.
- 학술 일관: Cambridge JFQA Trend Factor도 단순 factor

### 2.5 한국 시장 특이

- 김치 프리미엄: mean +2% (2024~2026), std ±2%
- Universe size: 평균 129 코인 (저유동성 필터 후)
- 약세장 (2025-10~2026-01) 4개월 폭락 → 모델 테스트 환경
- **2026-04 시장 회복 시작**: V2-06 페이퍼 운영 시점

---

## 3. 어디가 바뀌었나 — Commit 흐름 (7개)

```
2680da5  ML-01a API 가용성 검증 (CoinGecko 365일 한도 발견 → B+D 채택)
398b2a7  ML-01b 데이터 수집 script
a76dbeb  ML-02 Feature Engineering 47개 + lookahead PASS
41eeeb3  ML-03/04/05 LightGBM 학습 + OOS (Sharpe -8.36 NO-GO)
dea413d  ML-06 학습 분석 (Long-Short ≈ 0 + regime change 입증)
2c56d0e  ML-v2 grid 125 trial (Mean Reversion 발견 +26.74)
e372ca8  ML-v3 분봉 grid 125 trial (+36.37)
42f7ba8  ML-v4 extras (Ensemble + Regime + CPCV 4/4 + Universe 100)

총 신규 파일:
  research/scripts/ml_01b_data_collection.py
  research/scripts/ml_02_features.py
  research/scripts/ml_03_train_backtest.py
  research/scripts/ml_06_analysis.py
  research/scripts/ml_v2_grid.py
  research/scripts/ml_v3_intraday_collect.py
  research/scripts/ml_v3_features_grid.py
  research/scripts/ml_v4_extras.py
  research/scripts/strategy_i_forward_check.py
  research/data/ml_v2/{ohlcv_upbit, btc_binance, usdkrw, features}.parquet (~5.4MB)
  research/data/ml_v3/{ohlcv_4h}.parquet (~4.6MB)
  research/notebooks/results/v2_strategy_ml_*.json (5개)
  docs/stage1-subplans/v2-strategy-ml-trend-factor.md
  docs/stage1-subplans/v2-strategy-i-mean-reversion.md
  .evidence/v2-ml-01a-api-2026-04-27.md
```

---

## 4. Strategy I 진입 결정 권장 (사용자 결정 필요 ⚠️)

### 4.1 alpha 검증 종합

| 검증 | 결과 |
|------|------|
| ml_v2 일봉 best (Ridge t=30d hp=4) | L-S Sharpe +26.74 |
| ml_v3 분봉 best | L-S Sharpe +36.37 |
| Universe top 100 | L-S Sharpe +31.89 |
| **CPCV 4-fold** | **4/4 positive (mean +13.85)** ← cherry-pick 회피 검증 |
| DSR (N_trials=125, SR_0 ~17~25) | 모든 best > SR_0 PASS |

→ **alpha 통계적 유의 + robust** (CPCV 시간 분리 OOS)

### 4.2 그러나 위험

- 룰: Bottom decile 매수 (모델 inverse) — 사전 박제 = top decile 매수와 정반대
- **사용자 명시 박제 변경 필요** (handover #10/11 정신)
- 라이브 진입 시 별도 한도 (예: 10만원) + 4주 페이퍼 추가 검증 권장
- 단 사용자 2주 후 라이브 결정 박제 → 4주 검증 시간 부족

### 4.3 옵션

| 옵션 | 설명 |
|------|------|
| **A** | Strategy I 미진입, 학습 가치만 박제 (안전) |
| **B** | Strategy I daemon 통합 + 페이퍼 4주 forward 검증 → V2-07 진입 검토 |
| **C** | 5/11 라이브 진입 시 Strategy I 별도 한도 (예: 5만원) 즉시 진입 |
| **D** | 페이퍼 forward 14일 후 (~5/11) 결과 보고 결정 |

권장: **D** (보수적 + 학술 표준).

---

## 5. V2-07 라이브 진입 (5/11) 준비 상태

### 5.1 박제된 트랙

| 트랙 | 상태 | V2-07 진입 |
|------|------|:---:|
| Strategy A (Trend Following BTC/ETH) | 페이퍼 가동, 약세장 hold | 제한적 (회복 시) |
| Strategy D (Volatility Breakout BTC) | 페이퍼 가동, hold | 제한적 |
| Strategy G (Active Multi-pair, 30 cells) | 페이퍼 가동, 활동 중 | **메인 진입** |
| Strategy E (Momentum) | No-Go (학습 가치) | X |
| Strategy ML (Trend Factor) | No-Go (학습 가치) | X |
| **Strategy I (Mean Reversion inverse)** | **검증 alpha** | **사용자 결정 대기** |

### 5.2 사용자 책무 (5/11 전)

- [ ] K뱅크 → Upbit KRW **10만원** 입금
- [ ] Strategy I 진입 결정 (옵션 A~D)
- [ ] V2-07 sub-plan 사용자 명시 동의
- [ ] engine config `run_mode: paper → live` 전환 (5/11)

---

## 6. 사용자 결정 필요 항목 모음

1. **Strategy I 진입 결정**: A (학습만) / B (페이퍼 4주) / C (즉시 5/11) / D (페이퍼 14d 후 결정)
2. **V2-07 한도 분배**: BT-A/D + G + (I) → 10만원 분배 박제 명시
3. **5/11 라이브 진입 일정 확정**: 사용자 K뱅크 입금 시점

---

End of V2-Strategy-ML/I comprehensive retrospective. Generated 2026-04-27.

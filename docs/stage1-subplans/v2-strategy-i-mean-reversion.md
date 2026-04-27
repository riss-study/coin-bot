# V2-Strategy-I (Mean Reversion via Inverse Trend Factor) sub-plan

Task ID: V2-Strategy-I
Feature: STAGE1-V2-016
Created: 2026-04-27
Status: 사전 박제 (사용자 명시 동의 대기) — cycle 1 #5 회피 정신 적용

박제 출처:
- ML-v2 grid 결과 (2026-04-27): 125 trial 중 best Long-Short Sharpe +26.74 (Ridge hp=4 t=30d)
- DSR_z PASS (best > SR_0=17.79, N_trials=125)
- 학술 검증: Jegadeesh 1990, Lehmann 1990 (단기 반전 효과)

---

## 0. 발견 + cherry-pick 회피

### ML-v2 결과
- Top decile 매수 (Trend Factor) = Sharpe -8.79 폭락
- Long-Short (T-B) = Sharpe +7.43 평균 → Best +26.74
- 의미: **모델 예측 거꾸로 작동** = Mean Reversion alpha

### Cherry-pick 위험 박제
- 같은 OOS 기간 (2025-09 ~ 2026-04)에서 발견 = **cherry-pick 영역** (cycle 1 #5)
- 사전 박제 = top decile 매수, 실제 alpha = bottom decile 매수
- → **신규 forward 기간 검증 필수** (페이퍼 운영 2026-04-27~ 자연 OOS)

### 회피 절차
1. Strategy I 룰 사전 박제 (본 sub-plan)
2. 페이퍼 forward 검증 4주 (사용자 결정 시 2주 단축 동의)
3. forward Sharpe > 0.5 + Long-Short > 0.5 시에만 V2-07 진입 후보

---

## 1. Strategy I 사전 박제 (변경 금지)

### 1.1 핵심 룰

```
매일 KST 09:05 시점:
1. Universe: KRW 거래대금 top 50 (market_warning="NONE", 거래대금 ≥ 10억)
2. Feature 47개 계산 (ML-v2 동일)
3. Ridge regression model (학습 ML-v2 grid best 발견)
4. score = model.predict(features)
5. **Bottom decile (score 낮은 5개) 매수** ← 핵심: 거꾸로
6. 동일가중 stake (예: 50만 / 5 = 10만/cell, 라이브 시 별도 한도)
7. 7일 후 rebalance (재 score → 새 bottom 5)
8. SL -5% / TP +10% / time stop 7일 (mean reversion 빠른 회수)
```

### 1.2 모델 박제

```
Algorithm: Ridge Regression
Library: sklearn.linear_model.Ridge
Hyperparam (ML-v2 hp_idx=4): alpha=0.01
Target: forward 30d cross-sectional percentile rank
Train: 2024-01-01 ~ 2025-08-31 (20m, ML-v2와 동일)

Note: hyperparam 사후 변경 금지. ML-v2 grid에서 best 발견했지만
      cycle 1 #5 회피 = 새 forward에서만 검증.
```

### 1.3 거래비용

```
fee: 0.0005 × 왕복
slippage: 메이저 0.0005 / 중형 0.0010 / 소형 0.0030 (avg_dollar_volume_30d 기준)
```

---

## 2. Go 기준 (사전 박제)

### 2.1 Forward 검증 (자연 OOS)

```
페이퍼 forward 기간: 2026-04-27 ~ (V2-06 운영 중)
최소 측정: 14d (사용자 2주 결정 박제 동의 시)
최대 측정: 28d (V2-06 4주 박제)
```

### 2.2 PASS 조건 (사전 박제, 변경 금지)

```
조건 모두 충족:
- forward Long-Short Sharpe > 0.5 (보수적)
- forward Bottom decile Sharpe > 0 (단순 long alpha)
- forward trades ≥ 14 (2주 × 5 cells × 1.4회/cell)
- DSR_z > 0 (forward 자체 유의성)
```

### 2.3 FAIL 시 처리

```
- Strategy I 학습 가치만 박제
- V2-07 후보 X
- candidate-pool.md Retained 등록 (Strategy E와 동일 패턴)
```

### 2.4 PASS 시 처리

```
- V2-07 라이브 진입 후보 (별도 한도 5만 또는 10만)
- 사용자 명시 동의 후 engine 통합
- 한도 박제: Strategy I 단독 X. BT-A/D + G + I 합산 50만 절대
```

---

## 3. 위험 박제

### 위험 1: Mean Reversion 시장 의존

- mean reversion alpha는 **약세장/횡보장에서 강함**, 강세장에서 약함
- 2026-04 시장 회복 시작 → mean reversion alpha 약화 가능성
- 페이퍼 forward 검증 필수

### 위험 2: 거래비용 대 alpha

- ML-v2 분석: Best L-S Sharpe 26.74 (gross)
- 거래비용 미반영. net Sharpe 추산 필요
- 7일 holding × 5 cells × 매주 rebalance = 월 ~20 trades
- cost = 20 × 0.20% = -4%/월 → 연환산 -50% 가능
- → forward 검증에서 net Sharpe 박제

### 위험 3: 데이터 부족

- 페이퍼 2주 = 14 일봉 = 2 rebalance cycle만 측정
- 통계 유의성 약함
- 사용자 2주 라이브 결정 + 라이브 첫 1주 결과 추가 검증 권장

---

## 4. 작업 분해

| ID | 항목 | 추정 |
|----|------|:---:|
| **I-01** | Sub-plan 박제 (본 문서) | ✓ |
| **I-02** | Ridge 모델 사전 학습 + 저장 (artifact) | 0.5d |
| **I-03** | 페이퍼 forward 검증 스크립트 (매일 score 계산 + bottom decile 매수 시뮬) | 1d |
| **I-04** | 14d/28d forward Sharpe + DSR 측정 | 0.5d |
| **I-05** | candidate-pool.md v11 박제 (PASS/FAIL 결과) | 0.5d |
| **I-06** | (PASS 시) engine 통합 + 사용자 명시 동의 | 1d |

총 ~3.5일 (페이퍼 검증 시간 별도 14~28일)

---

## 5. 사용자 결정 필요 ⚠️

본 sub-plan 진행 의사:

| 옵션 | 설명 |
|------|------|
| **A** | I-01 박제만 + 페이퍼 forward 자연 검증 (engine 통합 X, 매일 score 기록만) |
| **B** | I-01~04 + Strategy I daemon 통합 (사용자 명시 동의 + 한도 박제) |
| **C** | 보류 — Strategy E No-Go와 같은 학습 가치만 박제 |
| **D** | 분봉 ML-v3 결과 보고 결정 |

---

End of V2-Strategy-I sub-plan. Generated 2026-04-27.

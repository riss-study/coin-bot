# Task W3-01 Walk-forward Analysis — Evidence

Task ID: W3-01 / Feature ID: BT-004 / Date: 2026-04-22 / Status: 자동 평가 No-Go, 사용자 공식 결정 대기
Sub-plan: `docs/stage1-subplans/w3-01-walk-forward.md` **v2** (사용자 옵션 A 직접 선택 "2", 2026-04-21)
Report: `research/outputs/week3_report.md`
Reviewer: backtest-reviewer (본 evidence 작성 직후 호출 예정)
Auditor: 외부 감사 2차 (W3-01.6, 결과 정합성 + 프레임 A/B 판단) 대기
사용자 공식 결정: 프레임 A (학습 모드) vs B (재탐색) 중 명시 선택 대기 (W3-01.7)

---

## 1. 데이터

### 1.1 페어 (2개, Tier 1만)

| Pair | File | T (bars) | SHA256 (12 chars) |
|------|------|----------|-------------------|
| KRW-BTC | `research/data/KRW-BTC_1d_frozen_20260412.parquet` | 1927 | `da5b5a5bd74c` |
| KRW-ETH | `research/data/KRW-ETH_1d_frozen_20260412.parquet` | 1927 | `2dfbb4970bc8` |

### 1.2 시간 범위

- Advertised: 2021-01-01 ~ 2026-04-12 UTC
- W3-01 train start: 2021-10-15 UTC (Common-window, cycle 2 v5)
- 타임존: UTC, naive 인덱스 없음
- freeze 종료일: 2026-04-12 UTC 일관

### 1.3 Fold 분할 (2026-04-21 v2 사용자 승인 시점 freeze)

| Fold | Train | Train bars | Test | Test bars |
|------|-------|-----------|------|-----------|
| 1 | 2021-10-15 ~ 2023-10-15 | 730 | 2023-10-15 ~ 2024-04-12 | 180 |
| 2 | 2021-10-15 ~ 2024-04-15 | 913 | 2024-04-15 ~ 2024-10-12 | 180 |
| 3 | 2021-10-15 ~ 2024-10-15 | 1096 | 2024-10-15 ~ 2025-04-13 | 180 |
| 4 | 2021-10-15 ~ 2025-04-15 | 1278 | 2025-04-15 ~ 2025-10-12 | 180 |
| 5 | 2021-10-15 ~ 2025-10-15 | 1461 | 2025-10-15 ~ 2026-04-12 | 179 (경계) |

Sanity: test 180 ±1%, train warmup MA200+ 모두 충족.

## 2. 파라미터 (사전 지정, 재튜닝 금지)

### 2.1 Cells (W2-03 Go cells 양방향 freeze)

```
CELLS = [
    ("KRW-BTC", "A"), ("KRW-BTC", "C"), ("KRW-BTC", "D"),
    ("KRW-ETH", "A"), ("KRW-ETH", "D"),
]
```

ETH_C 재포함 X (W2-03 FAIL), Secondary 마킹 (SOL/DOGE 등) 포함 X.

### 2.2 Strategy 파라미터 (W2-02 v5 박제, 변경 X)

- Strategy A: MA=200, Donchian=20/10, Vol>1.5×, SL=8%
- Strategy C: MA=50/200, ATR=14, ATR×3 trailing (**방법 B manual exit_mask**, W2-03.1 박제)
- Strategy D: Keltner(20, 1.5×ATR14, original_version=False) + Bollinger(20, 2σ), SL=8%

### 2.3 Go 기준 (옵션 A, v2 박제, 사용자 직접 선택 "2")

```
N_TRIALS = 5
GO_SHARPE_THRESHOLD = 0.8
GO_DSR_Z_THRESHOLD = 0.0
GO_STABILITY_REQUIRED = 5  # 5/5 모든 fold pass
MIN_TRADE_COUNT = 2        # fold당 < 2 trade → N/A = FAIL
YEAR_FREQ = '365 days'     # PT-04 신규 노트북 범위 선행 적용
```

### 2.4 Portfolio

```
INIT_CASH = 1_000_000 / FEES = 0.0005 / SLIPPAGE = 0.0005 / FREQ = '1D' / YEAR_FREQ = '365 days'
```

## 3. 결과

### 3.1 자동 평가 요약

- **is_go = False**
- **go_cells = []** (0/5)
- 25 조합 중 non-NA = 11, N/A = 14 (56%)

### 3.2 Cell별 Aggregation

| Cell | fold pass | Mean Sharpe | Mean DSR_z | Cell Go | N/A |
|------|-----------|-------------|------------|:-------:|:---:|
| BTC_A | 2/5 | +1.913 | +16.266 | ✗ | 2 |
| BTC_C | 0/5 | None | None | ✗ | 5 |
| BTC_D | 3/5 | +1.012 | +22.054 | ✗ | 0 |
| ETH_A | 1/5 | +2.729 | +23.570 | ✗ | 4 |
| ETH_D | 2/5 | +1.896 | +15.108 | ✗ | 3 |

### 3.3 Fold별 V_empirical

| Fold | non-NA | V_empirical | SR_0 |
|------|--------|-------------|------|
| 1 | 4 | 0.3657 | 0.7212 |
| 2 | 1 | N/A | N/A |
| 3 | 2 | 0.2101 | 0.5467 |
| 4 | 3 | 0.1643 | 0.4834 |
| 5 | 1 | N/A | N/A |

### 3.4 결과 파일

- `research/outputs/w3_01_walk_forward.json` (25 조합 + fold DSR + cell summary + metadata)
- `research/outputs/week3_report.md`

## 4. 자동 검증

### 4.1 데이터 무결성

- BTC + ETH SHA256 재계산 → data_hashes.txt 값과 일치 (PASS)
- 타임존 UTC + monotonic + no duplicates (PASS)

### 4.2 Fold 분할 sanity

- 각 fold test bar count = 180 ±1% (fold 1-4: 180, fold 5: 179 경계) PASS
- 각 fold train warmup ≥ MA200 (Strategy A 요구) PASS

### 4.3 DSR 공식 검증

- Bailey 2014 eq. 9 (`SR_0 = sqrt(V) × ((1-γ)·Φ⁻¹(1-1/N) + γ·Φ⁻¹(1-1/(N·e)))`)
- Bailey 2014 eq. 10 (`DSR_z = (SR_hat - SR_0) × sqrt((T-1)/(1 - γ_3·SR_0 + ((γ_4-1)/4)·SR_0²))`)
- γ_4 Fisher → raw 변환 (+3) 명시 (W2-03 v8 일관)

### 4.4 min_trade_count 필터 (W-7)

- 14 fold (총 25 중 56%)가 trade < 2 → N/A = FAIL 처리
- Strategy C 전부 N/A (5/5): W-7 박제 리스크 현실화 확인
- Strategy A (BTC 2, ETH 4), ETH_D 3, BTC_D 0

### 4.5 Go/No-Go 자동 평가

- 옵션 A (5/5 stability + 평균 pass) 엄격 적용
- is_go=False / go_cells=[]

## 5. 룰 준수 (v8 WARNING-3 + v2 박제 강제 확인)

### 5.1 V_empirical 일관 적용 ✓

- 각 fold 독립 V_empirical_fold 산출 (non-NA cells 기반)
- Floor 재도입 금지 준수 (floor 적용 X)
- V_reported=max(V_emp, 1.0) 같은 보수적 조치 X

### 5.2 임계값 변경 금지 ✓

- Sharpe > 0.8 / DSR_z > 0 (v8 박제 그대로)
- 5/5 stability (옵션 A 사용자 직접 선택, 박제)

### 5.3 Fold별 DSR 재산정 의무 ✓

- 각 fold의 DSR_z 독립 산출 (fold별 V_empirical + fold별 T + fold별 daily_returns skew/kurtosis)

### 5.4 W2-03 Go cells 양방향 freeze ✓

- 확장 X: ETH_C 재포함 / Secondary 마킹 포함 X
- 축소 X: 5 cell 모두 실행 (Strategy C 전 fold N/A여도 축소 X)

### 5.5 Strategy 파라미터 재튜닝 X ✓

- W2-02 v5 박제값 그대로 + W2-03.1 방법 B 구현 (NIT-1 명시)
- 알트별 튜닝 X (Tier 1만)

### 5.6 min_trade_count=2 사전 박제 ✓

- v2 W-7 정정 반영. 결과 본 후 완화 X.
- N/A fold = FAIL 처리 (fold_pass_count 미포함)

### 5.7 `pf.sharpe_ratio(year_freq='365 days')` 명시 호출 (PT-04 신규 노트북 선행 적용) ✓

- vectorbt default 의존 제거 (cycle 1 #16 재발 방지)

### 5.8 `np.mean` aggregation (median 대체 X) ✓

- NIT-3 박제 준수

### 5.9 W3-02 pooled V deferred = Go 판정 번복 근거 X ✓

- v2 핵심 원칙 #8 박제. W3-01.7 사용자 결정 후 W3-02 진입 시 재확인 필요

## 6. 리뷰

### 6.1 backtest-reviewer (W3-01.5, 본 evidence 작성 직후 호출 예정)

- 검증 focus: 수치 정합성, v8/v2 박제 준수, 6단 구조, API 검증
- Trace 저장 위치: `.evidence/agent-reviews/w3-01-walk-forward-reviewer-2026-04-22.md`

### 6.2 외부 감사 2차 (W3-01.6 대기)

- 검증 focus: 결과 정합성 bit-level 재계산, cherry-pick 통로 (프레임 B 사후 완화 유혹), 프레임 A/B 근거
- Trace 저장 위치: `.evidence/agent-reviews/w3-01-walk-forward-result-review-2026-04-22.md`

### 6.3 사용자 공식 결정 (W3-01.7 대기)

- **프레임 A 선택**: Stage 1 학습 모드 전환 (decisions-final.md L133 트리거)
- **프레임 B 선택**: Week 3 재탐색 (v3 박제 + cycle 3 강제) or 설계 재조정
- **공통**: Stage 1 킬 카운터 +2 소급, Strategy A Active → Retained 복귀 (NIT-4)

## 7. Stage 1 킬 카운터

- **현재 (W3-01 자동 결과 No-Go 반영 전)**: +1 (W1 종료 시점)
- **W3-01 공식 No-Go 확정 후**: **+2** (W2-03 Go + W3-01 No-Go 이중 실패, W2-03 v8 WARNING-4 박제 발동)

## 8. 커밋 (예상, 사용자 결정 후)

```
feat(plan): BT-004 W3-01 Walk-forward 완료 — 사용자 프레임 {A|B} 선택 + Stage 1 킬 카운터 +2 소급

- 25 조합 (5 cell × 5 fold Anchored) 실행 완료
- is_go=False, Go cells 0/5. Strategy C 전부 N/A (W-7 리스크 현실화)
- 사용자 명시 결정: 프레임 {A 학습 모드 / B 재탐색} (2026-04-22)
- Stage 1 킬 카운터 +2 소급 가산 (decisions-final.md 갱신)
- Strategy A Active → Retained 역방향 복귀 (candidate-pool.md v6)
- backtest-reviewer + 외부 감사 2차 APPROVED

Evidence: .evidence/w3-01-walk-forward-2026-04-22.md
```

---

End of W3-01 evidence. Generated 2026-04-22 by claude-opus-4-7. v8/v2 박제 준수.

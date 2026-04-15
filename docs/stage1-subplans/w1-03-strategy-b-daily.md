# Task W1-03 - Strategy B 일봉 백테스트 (평균 회귀)

## 메인 Task 메타데이터

| 항목 | 값 |
|------|-----|
| **메인 Task ID** | W1-03 |
| **Feature ID** | STR-B-001 |
| **주차** | Week 1 (Day 3) |
| **기간** | 1일 |
| **스토리 포인트** | 3 |
| **작업자** | Solo |
| **우선순위** | P0 |
| **상태** | Done (v2, 2026-04-14) |
| **Can Parallel** | NO (W1-01 필수, W1-02와 같은 데이터 사용) |
| **Blocks** | W1-04, W1-06 |
| **Blocked By** | W1-01 |

## 개요

Larry Connors 스타일 평균 회귀 전략을 일봉으로 백테스트.
- 200일 MA 추세 필터 (상승 추세에서만 역추세 매수)
- RSI(4) < 25 진입, RSI(4) > 50 청산
- 시간 스톱: 5 거래일 경과 (vectorbt에 td_stop 없으므로 entries.shift(5) 패턴)
- ATR 기반 하드 스톱 -8%
- 목표: Sharpe > 0.5

## 현재 진행 상태

- 메인 Task 상태: Done
- 완료일: 2026-04-14 (v2 post-external-audit)
- Evidence: `.evidence/w1-03-strategy-b-daily.txt` (backtest-reviewer agent APPROVED)
- 결과: Sharpe 0.1362 (**FAIL < 0.5**), MDD -21.27%, Trades 39, PF 1.092
- 해석: Method 정확, 결과는 W1-06 Go/No-Go 영역. Strategy A 단독 채택 가능성 높음.

| SubTask | 상태 | 메모 |
|---------|------|------|
| W1-03.1 | Done | 노트북 셋업 + data hash assert + monotonic + len==1927 |
| W1-03.2 | Done | MA200 + RSI(4) Wilder (ta.momentum.RSIIndicator) |
| W1-03.3 | Done | 진입/청산 마스크 + time stop entries.shift(5) + warmup assert |
| W1-03.4 | Done | vectorbt Portfolio.from_signals (검증된 0.28.5 API) |
| W1-03.5 | Done | strategy_b_daily.json (v4 schema: status field + realized_time_stop_trades) |
| W1-03.6 | Done | Evidence + 2 agent review traces (v1 + v2) |

## SubTask 목록

### SubTask W1-03.1: 노트북 셋업

**작업자**: Solo
**예상 소요**: 0.1일

- [ ] `research/notebooks/03_strategy_b_mean_reversion_daily.ipynb` 생성
- [ ] import + 데이터 해시 검증 + 데이터 로드 (W1-02 패턴 동일)
- [ ] **`sha256_hash` 변수를 `sha256_file(PARQUET_PATH)`로 명시 할당** (결과 JSON에 사용됨, NameError 방지)

### SubTask W1-03.2: 지표 계산

**작업자**: Solo
**예상 소요**: 0.1일

사전 지정 파라미터:

```python
MA_PERIOD = 200
RSI_PERIOD = 4
RSI_BUY = 25
RSI_SELL = 50
TIME_STOP_DAYS = 5
SL_PCT = 0.08
```

- [ ] MA200: `close.rolling(window=MA_PERIOD).mean()`
- [ ] RSI(4) Wilder (ta 라이브러리):
  ```python
  from ta.momentum import RSIIndicator
  rsi = RSIIndicator(close=close, window=RSI_PERIOD).rsi()
  ```

### SubTask W1-03.3: 진입 + 시간 스톱 청산

**작업자**: Solo
**예상 소요**: 0.2일

- [ ] 진입 마스크:
  ```python
  entries = (close > ma200) & (rsi < RSI_BUY)
  ```
- [ ] 청산 1: RSI 회복
  ```python
  rsi_exits = rsi > RSI_SELL
  ```
- [ ] 청산 2: 시간 스톱 (vectorbt 0.28.5에 td_stop 없음, entries.shift 패턴 사용)
  ```python
  # 주: 이는 "엔트리 신호 N바 후 exit" 근사. 실제 보유 N바 후가 아님.
  # 포지션 재진입 차단 시 약간 차이 가능.
  time_exits = entries.shift(TIME_STOP_DAYS).fillna(False).astype(bool)
  ```
- [ ] 결합:
  ```python
  exits = rsi_exits | time_exits
  ```

### SubTask W1-03.4: vectorbt 백테스트

**작업자**: Solo
**예상 소요**: 0.1일

- [ ] vectorbt 호출 (sl_stop만, sl_trail=False):
  ```python
  pf = vbt.Portfolio.from_signals(
      close=close,
      entries=entries,
      exits=exits,
      sl_stop=SL_PCT,
      sl_trail=False,
      init_cash=1_000_000,
      fees=0.0005,
      slippage=0.0005,
      freq='1D',
  )
  ```
- [ ] `pf.stats()` 출력

### SubTask W1-03.5: 결과 저장

**작업자**: Solo
**예상 소요**: 0.1일

- [ ] 핵심 지표 추출 (W1-02 v3 schema 따름 — nested metrics + 추가 필드):
  ```python
  # MDD duration 두 metric 분리 (deepest vs longest)
  records = pf.drawdowns.records_readable
  records['DD_pct'] = (records['Valley Value'] - records['Peak Value']) / records['Peak Value']
  records['Duration_days'] = (
      pd.to_datetime(records['End Timestamp']) - pd.to_datetime(records['Peak Timestamp'])
  ).dt.days
  deepest = records.loc[records['DD_pct'].idxmin()]
  longest = records.loc[records['Duration_days'].idxmax()]

  # Sharpe SE (Lo 2002, return-basis, T_returns=N-1)
  T_returns = len(close) - 1
  sharpe_se = float(np.sqrt((1 + 0.5 * sharpe**2) / T_returns))

  results = {
      'feature_id': 'STR-B-001',
      'task_id': 'W1-03',
      'data_hash': sha256_hash,
      'parameters': {
          'ma_period': MA_PERIOD,
          'rsi_period': RSI_PERIOD,
          'rsi_buy': RSI_BUY,
          'rsi_sell': RSI_SELL,
          'time_stop_days': TIME_STOP_DAYS,
          'sl_pct': SL_PCT,
      },
      'metrics': {  # nested (W1-02 v3 schema 일관성)
          'sharpe': sharpe,
          'sharpe_se_return_basis': sharpe_se,
          'sharpe_se_t_returns': T_returns,
          'sharpe_ci_95_normal': [sharpe - 1.96*sharpe_se, sharpe + 1.96*sharpe_se],
          'sharpe_ci_method': 'Lo 2002 normal approximation, return-basis',
          'total_return': total_return,
          'max_drawdown': max_dd,
          'deepest_drawdown': {
              'pct': float(deepest['DD_pct']),
              'duration_days': int(deepest['Duration_days']),
              'recovered': deepest['Status'] == 'Recovered',
              'peak_timestamp': pd.to_datetime(deepest['Peak Timestamp']).isoformat(),
              'end_timestamp': pd.to_datetime(deepest['End Timestamp']).isoformat(),
          },
          'longest_drawdown': {
              'pct': float(longest['DD_pct']),
              'duration_days': int(longest['Duration_days']),
              'recovered': longest['Status'] == 'Recovered',
          },
          'total_drawdown_records': len(records),
          'win_rate': win_rate,
          'profit_factor': profit_factor,
          'total_trades': total_trades,
      },
      'edge_case_checks': {
          'warmup_zero_entries': bool(int(entries.iloc[:MA_PERIOD].sum()) == 0),
          'time_stop_mask_nonempty': bool(int(time_exits.iloc[MA_PERIOD:].sum()) > 0),
          'time_stop_mask_count_raw': int(time_exits.iloc[MA_PERIOD:].sum()),
          # Exit reason breakdown (bar-based, 타임프레임 독립)
          # 각 trade exit bar에서 time_exits/rsi_exits 조건 검사로 정확 분류
          'exit_reason_breakdown': {
              'time_stop_exclusive': ...,   # time only (순수 time-stop)
              'time_stop_coincident': ...,  # time + rsi 동시 (ambiguous)
              'rsi_exclusive': ...,         # rsi only
              'sl_stop_or_other': ...,      # sl_stop 또는 unknown
          },
          'total_time_stop_contribution': ...,  # exclusive + coincident
          'deepest_dd_reconciles_with_max_drawdown': bool(abs(deepest_dd_pct - max_dd) < 1e-9) if total_trades > 0 else None,
      },
  }
  ```
- [ ] `outputs/strategy_b_daily.json` 저장
- [ ] equity curve: `outputs/strategy_b_equity.png`

### SubTask W1-03.6: Evidence + 리뷰

**작업자**: Solo + backtest-reviewer agent (실제 호출, self-review 금지)
**예상 소요**: 0.1일

- [ ] `.evidence/w1-03-strategy-b-daily.txt` 작성
- [ ] **backtest-reviewer agent 실제 호출** (Task tool, .claude/agents/backtest-reviewer.md 체크리스트 적용)
- [ ] **Agent review trace 저장**: `.evidence/agent-reviews/w1-03-{timestamp}-review.md`
- [ ] Evidence 파일에 trace 경로 명시 ("Agent review trace: ...")
- [ ] APPROVED 받음 (BLOCKING 0)
- [ ] 상태 업데이트 (sub-plan + execution-plan)

## 인수 완료 조건 (Acceptance Criteria)

- [ ] 사전 지정 파라미터 상수 선언
- [ ] 데이터 해시 검증 통과 (consumer 노트북 첫 셀 룰)
- [ ] RSI는 ta 라이브러리 (Wilder 스무딩, 직접 구현 금지)
- [ ] 시간 스톱은 entries.shift() 패턴 (td_stop 사용 금지)
- [ ] 시간 스톱 한계 주석 포함 ("엔트리 N바 후 근사")
- [ ] vectorbt 크래시 없이 실행
- [ ] bars_held, entry_price 등 미정의 변수 참조 없음
- [ ] outputs/strategy_b_daily.json 생성 (W1-02 v3 schema 일관)
- [ ] JSON에 sharpe_se, sharpe_ci_95, deepest/longest_drawdown, edge_case_checks 포함
- [ ] backtest-reviewer agent APPROVED + trace 파일 저장

**Week 1 Go 기준 (W1-06에서 평가)**:
- Sharpe > 0.5

## 의존성 매트릭스

| From | To | 관계 |
|------|-----|------|
| W1-01 | W1-03 | 일봉 데이터 |
| W1-03 | W1-04 | 강건성 분석 입력 |
| W1-03 | W1-06 | Week 1 리포트 입력 |

## 리스크 및 완화 전략

| 리스크 | 영향 | 완화 |
|--------|------|------|
| Sharpe < 0.5 | Medium | Strategy A가 통과하면 W1-06에서 Go 가능 |
| 시간 스톱 패턴 부정확 | Low | 평균 보유 ~2~6 bar라 5일 거의 발동 안 함 |
| RSI(4)는 매우 민감, 잡음 신호 | Medium | 200MA 필터로 상승 추세 한정 |
| 거래 횟수 과다 | Medium | 수수료 누적 영향 모니터링 |

## 산출물 (Artifacts)

### 코드
- `research/notebooks/03_strategy_b_mean_reversion_daily.ipynb`

### 결과
- `research/outputs/strategy_b_daily.json`
- `research/outputs/strategy_b_equity.png`

### 검증
- `.evidence/w1-03-strategy-b-daily.txt`

### 테스트 시나리오

- **Happy**: 사전 지정 파라미터 → Sharpe X.XX 기록
- **Edge**: 시간 스톱 발동 빈도 확인 (RSI 회복이 5일 이내 대부분)
- **Edge**: 200 MA warmup 기간 trade 없음
- **Denial (수동)**: bars_held 변수 사용 시 reviewer가 BLOCKING

## Commit

```
feat(plan): STR-B-001 Strategy B 일봉 백테스트 완료

사전 지정 파라미터:
- MA200 (상승 추세 필터)
- RSI(4) < 25 진입, > 50 청산
- 시간 스톱: entries.shift(5)
- 하드 스톱: -8%

결과:
- Sharpe: X.XX (목표 > 0.5)
- MDD: XX.X%
- 트레이드: N

Evidence: w1-03-strategy-b-daily.txt (APPROVED)
```

---

**이전 Task**: [W1-02 Strategy A 일봉](./w1-02-strategy-a-daily.md)
**다음 Task**: [W1-04 강건성 + 민감도](./w1-04-robustness.md)

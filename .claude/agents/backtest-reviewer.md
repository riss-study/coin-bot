# Backtest Reviewer Agent

## 역할

coin-bot 백테스트 노트북/코드/Evidence 파일을 검증하는 spec-driven 리뷰어. 일반 코드 리뷰가 아닌 백테스트 정확성/룰 준수/Evidence 정합성 검증.

## 사용 시점

- W1-01 ~ W1-06 각 Task 종료 시 (구현 완료 후 Evidence 작성 직전)
- W2~W3 백테스트 Task 완료 시
- 모든 백테스트 결과를 사용자에게 보고하기 전

## 검증 항목

### A. Data Integrity (데이터 무결성)

- [ ] 데이터 freeze 해시 검증 코드가 노트북 첫 셀에 존재
- [ ] `assert df.index.tz is None` 후 `tz_localize('Asia/Seoul').tz_convert('UTC')` 패턴 사용
- [ ] 갭 < 0.1% (`check_gaps` 함수 결과)
- [ ] 데이터 파일명에 freeze 날짜 포함 (예: `_frozen_20260412`)
- [ ] `data/data_hashes.txt`와 매치 확인

### B. Pre-registered Parameters (사전 지정 파라미터)

- [ ] 사전 지정 파라미터가 노트북 상단에 **상수로 명시 선언** (예: `MA_PERIOD = 200`)
- [ ] 결과 JSON에 `parameters` 필드로 모든 파라미터 기록됨
- [ ] **민감도 그리드 결과가 Go/No-Go 평가에 사용되지 않음** (참고용 only 라벨)
- [ ] DSR 계산 시 (Week 2+) `N_trials` 입력 정확

### C. vectorbt 0.28.5 API Correctness (검증된 API만 사용)

- [ ] `sl_stop`은 fraction 형식 (`0.05`, not `5`)
- [ ] `sl_trail`은 boolean (`True`/`False`)
- [ ] **`ts_stop` 사용 안 함** (vectorbt 0.28.5 무료 버전에 없음)
- [ ] **`td_stop`, `max_duration`, `time_stop`, `dt_stop` 사용 안 함**
- [ ] `pf.sharpe_ratio()`, `pf.total_return()` 등 모든 메서드는 **괄호 호출** (`()` 필수)
- [ ] `freq` 파라미터 명시 (`'1D'` 또는 `'4h'`)
- [ ] Boolean exit mask에 **미정의 변수 참조 없음** (`entry_price`, `bars_held`, `position_size` 등 금지)
- [ ] 시간 스톱은 `entries.shift(N).fillna(False).astype(bool)` 패턴
- [ ] 앙상블은 `cash_sharing=True` + `group_by=True` 패턴 (Week 2+)

### D. pyupbit 0.2.34 API Correctness

- [ ] `get_ohlcv_from(ticker, interval, fromDatetime, to, period)` 시그니처
- [ ] `fromDatetime` camelCase (not `from_datetime`, not `from`)
- [ ] `period=0.2` 사용 (rate limit 안전 마진)
- [ ] 결과 None 가능성 처리 (재시도 wrapper)

### E. Wilder Smoothing (지표 계산)

- [ ] ATR은 `ta.volatility.AverageTrueRange(...).average_true_range()` 사용
- [ ] RSI는 `ta.momentum.RSIIndicator(...).rsi()` 사용
- [ ] 직접 SMA로 ATR/RSI 구현 금지

### F. Strategy Logic Correctness

- [ ] `MA200` 변수명이면 윈도우가 실제로 200 (일봉=200, 4h=1200)
- [ ] Donchian high/low에 `.shift(1)` 적용 (미래 정보 차단)
- [ ] **거래량 평균에도 `.shift(1)` 적용** (신호 바의 거래량 평균은 알 수 없음, look-ahead 방지)
- [ ] **모든 rolling 지표가 미래 정보를 사용하지 않는지 확인** (`.shift(1)` 누락 grep)
- [ ] 4시간봉 윈도우는 일봉의 6배 (1일 = 6 bars)
- [ ] 200 bar warmup으로 첫 N bar trade 없음 → 알려진 동작 주석
- [ ] **선언만 하고 사용 안 한 지표 감지** — 변수 선언했는데 entries/exits/portfolio 어디에도 참조 안 되면 dead code 경고
- [ ] **시간 스톱 캐비어트 주석 존재** — `entries.shift(N)` 사용 시 "엔트리 N바 후 근사, 실제 보유 N바 후가 아님" 주석 필수

### G. Output / Evidence

- [ ] 결과 JSON 저장 (`outputs/strategy_*.json`)
- [ ] JSON에 다음 필드 모두 포함: `feature_id`, `task_id`, `data_hash`, `parameters`, `sharpe`, `total_return`, `max_drawdown`, `win_rate`, `profit_factor`, `total_trades`
- [ ] **`sha256_hash` (또는 `data_hash`) 변수가 노트북에서 명시 할당됨** — `sha256_file()` 호출 결과를 변수에 바인딩, JSON에 사용
- [ ] **`freq` 파라미터가 데이터 frequency와 일치** — `'1D'`이면 일봉 Parquet, `'4h'`이면 4시간봉 Parquet
- [ ] Evidence 파일 (`.evidence/{task-id}-*.txt`) 6단 구조 준수:
  1. 데이터 입력
  2. 사전 지정 파라미터
  3. 결과
  4. 자동 검증 (PASS/FAIL)
  5. 룰 준수 (위 A~F 체크)
  6. Code review 결과
- [ ] Evidence Notes 섹션에 한계/가정 명시
- [ ] Evidence 파일 commit 메시지에 `Evidence: {filename}` 줄 포함

### H. Cross-document Consistency

- [ ] 사용된 파라미터가 sub-plan 메타데이터의 사전 지정 값과 일치
- [ ] 결과 JSON의 `feature_id`가 sub-plan의 Feature ID와 일치
- [ ] sub-plan의 Acceptance Criteria 모든 항목 평가됨
- [ ] execution-plan status 표 업데이트 준비됨

## 출력 형식

### BLOCKING (수정 필수, 다음 Task 진행 불가)

```
[BLOCKING] research/notebooks/02_strategy_a_trend_daily.ipynb cell 5
Description: vectorbt에 ts_stop=... 파라미터 사용. 0.28.5 무료 버전에 없음.
Fix: 트레일링이 필요하면 sl_stop=0.08 + sl_trail=True. 하드 손절만이면 sl_stop=0.08 + sl_trail=False.
Reference: research/CLAUDE.md Don'ts 섹션 (vectorbt 0.28.5 검증)
```

### WARNING (강력 권장 수정)

```
[WARNING] research/notebooks/02_strategy_a_trend_daily.ipynb cell 8
Description: pf.sharpe_ratio (괄호 없음). bound method 객체 반환.
Fix: pf.sharpe_ratio() 로 호출.
Reference: glossary.md Section 9 (vectorbt 0.28.5 검증 항목)
```

### NIT (개선 제안)

```
[NIT] research/notebooks/02_strategy_a_trend_daily.ipynb cell 12
Suggestion: 변수명 magic number (200, 20, 10) → 상수 선언 (MA_PERIOD, DH, DL)
Improves: 가독성 + 사전 지정 파라미터 명확성
```

### APPROVED

```
APPROVED FOR PROGRESSION TO TASK W1-03

검증 결과:
- A. Data Integrity: PASS
- B. Pre-registered Parameters: PASS
- C. vectorbt API: PASS (sl_stop fraction, sl_trail boolean, freq='1D', 메서드 호출 정확)
- D. pyupbit API: N/A (이 Task에서 사용 안 함)
- E. Wilder Smoothing: PASS (ta 라이브러리)
- F. Strategy Logic: PASS (MA200 윈도우=200 일봉, Donchian shift(1) 적용)
- G. Output: PASS (JSON 저장, Evidence 6단 구조)
- H. Cross-document: PASS (sub-plan 일치)

발견 사항: 0 BLOCKING, 0 WARNING, 1 NIT (수정 권장)
NIT 수정: pending (다음 Task와 무관)

다음 Task: W1-03 시작 가능
```

## 사용 방법

이 에이전트는 Claude Code Task 도구로 호출 (subagent_type: general-purpose):

```
Agent({
  description: "Backtest reviewer for W1-02",
  prompt: "Read .claude/agents/backtest-reviewer.md and apply the checklist to:
    - research/notebooks/02_strategy_a_trend_daily.ipynb
    - research/outputs/strategy_a_daily.json
    - .evidence/w1-02-strategy-a-daily.txt (draft)
    
    Return: BLOCKING / WARNING / NIT findings + final APPROVAL or REQUEST CHANGES."
})
```

## Approval Gate

- 모든 BLOCKING 해결 → 다음 Task 진행 가능
- WARNING은 다음 Task 진행 가능 (단, 사용자에게 보고)
- NIT는 무시하거나 다음 Task에서 처리
- APPROVED 받지 못한 Task는 sub-plan 상태가 Partial 또는 Blocked

## 에이전트 자체 검증

이 에이전트도 외부 감사관 패턴 적용 — 본인이 검증한 결과를 두 번째 호출에서 재검증 (사용자가 명시 요구 시).

## 변경 이력

- 2026-04-12: 초안 생성. vectorbt 0.28.5 + pyupbit 0.2.34 검증 결과 반영.

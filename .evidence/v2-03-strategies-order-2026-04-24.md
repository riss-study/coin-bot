# V2-03 Strategies + Order — Evidence

Task: V2-03 (strategies/{base, strategy_a, strategy_d} + order)
Feature: STAGE1-V2-006
Date: 2026-04-24
Status: Done (4 모듈 sanity 전부 PASS)
Sub-plan: `docs/stage1-v2-relaunch.md` v2 §2.1 / §2.4

---

## 1. 데이터 입력

- 실 Upbit public API: `fetch_ohlcv("KRW-BTC", count=400)` (400 bars, UTC tz)
- 박제 파라미터 (W2-02 v5, 재튜닝 금지):
  - Strategy A: MA=200, Donchian 20/10, Vol×1.5, SL 8%
  - Strategy D: Keltner(20, 1.5×ATR14, original_version=False), Bollinger(20, 2σ), SL 8%
- `ta>=0.11.0,<0.12` requirements.txt 추가 + 설치

## 2. 모듈 구조

```
engine/engine/strategies/
├── __init__.py          # StrategyA, StrategyD, SignalAction, SignalResult, Strategy 재수출
├── base.py              # SignalAction enum + SignalResult dataclass + Strategy Protocol + check_sl_hit
├── strategy_a.py        # Trend Following (150+ LOC)
└── strategy_d.py        # Volatility Breakout (180+ LOC)

engine/engine/
└── order.py             # OrderExecutor (paper/live 분기) + 멱등성 + 재시도 (280+ LOC)
```

## 3. Strategy A (Trend Following) — 실측 검증

- W1-02 박제 구현 재사용:
  - entry: `close > MA200 AND close > donchian_high.shift(1) AND volume > vol_avg.shift(1) × 1.5`
  - exit: `close < donchian_low.shift(1)` (또는 SL 8%)
- Sanity 결과 (최신 BTC 400 bars, 오늘 close 115,963,000):
  - [No position] action=hold (ma_filter_pass=False, donchian_breakout=False, volume_spike=False) — 현 시점 진입 조건 미충족
  - [In position fake entry=127,559,300] action=sl_exit (sl_level=117,354,556 > today_low=115,552,000)
  - SL 로직 정확 ✓

## 4. Strategy D (Volatility Breakout) — 실측 검증

- W2-02 v5 박제 구현 (방법 B 별개, 방법 B는 Strategy C 전용이었음):
  - entry: strict 동시 상향 돌파 (kc_upper + bb_upper 둘 다 crossover)
  - exit: strict kc_mid 하향 crossover (kc_mid = EMA(close, 20))
  - ta KeltnerChannel `original_version=False, window_atr=14, multiplier=1.5` 명시
- Sanity 결과 (최신 BTC 100 bars):
  - [No position] action=hold (kc_upper 115,147,160 vs close 115,963,000 — close가 넘었으나 어제 미돌파로 crossover 불성립)
  - snapshot: close, kc_upper, bb_upper 모두 실수 값 ✓
  - [In position fake entry=127,559,300] action=sl_exit ✓

## 5. Order Executor — 실측 검증 (paper mode)

**paper mode**: pyupbit API 호출 없이 `price_oracle` (현재가 함수)으로 즉시 체결 시뮬. state DB 기록.

**live mode**: pyupbit.Upbit 필요. `_safe_float` 로 ccxt #7235 `None` 필드 defensive 처리. (사용자 API 키 발급 후 V2-05에서 통합 테스트)

### 5.1 Paper buy sanity
- KRW 100,000 → 체결 (수수료 50 KRW = 0.0005, 실현 volume 0.00086240, filled_price 115,897,000)
- `OrderRecord` state.orders 테이블 기록 + `register_idempotency` 호출

### 5.2 멱등성 sanity
- 동일 `client_oid` 재호출 → 기존 `order_uuid` 반환 (재주문 X)
- cycle 1 학습 #5 (사후 완화) 및 이중 주문 방지 박제 준수 ✓

### 5.3 Paper sell sanity
- 동일 volume sell → 체결, fees 49.98 KRW

### 5.4 입력 검증
- `krw_amount <= 0` → ValueError ✓
- `run_mode='live'` without upbit_client → ValueError ✓

## 6. 자동 검증

- Strategy A `compute_signal`: 400 bars 입력 정상. warmup (MA200+1=201) 체크 ✓
- Strategy D `compute_signal`: 100 bars 입력 정상. warmup (max(kc,bb,atr)+2) 체크 ✓
- ta KeltnerChannel `original_version=False, window_atr=14, multiplier=1.5` 명시 호출 ✓
- SignalAction enum 4종 (ENTRY / EXIT / SL_EXIT / HOLD) ✓
- `check_sl_hit` 공통 함수 로직 정확 (entry × (1 - sl_pct) <= today_low) ✓
- OrderExecutor paper mode 즉시 체결 + state 기록 ✓
- `_safe_float` defensive 변환 (ccxt #7235 이슈 대응) ✓

## 7. 룰 준수

- 사전 지정 파라미터 (Strategy A/D) W2-02 v5 박제 그대로 ✓
- look-ahead 차단: Donchian / vol_avg `.shift(1)` 적용 ✓
- ta 라이브러리 사용 (research/CLAUDE.md 박제 Wilder smoothing) ✓
- 멱등성 (client_oid ↔ order_uuid 매핑) 활용 ✓
- 업비트 수수료 0.0005 (v1 박제) ✓
- run_mode paper/live 분기 + live validation ✓
- `_safe_float` ccxt #7235 `None` 방어 ✓

## 8. 리뷰

- backtest-reviewer: V2 초기 (단순 신호 함수 + paper order). V2-05 integration test 시점에 호출 예정
- 외부 감사: V2-04 완료 후 호출 예정
- 사용자 승인: "ㅇㅋ 착수 ㄱㄱ" (2026-04-24)

## 9. 다음 단계 (V2-04)

- `engine/scheduler.py`: KST 09:05 일봉 close 트리거 (cron-like)
- `engine/position.py`: 포지션 관리 + PnL + 세금 데이터
- `engine/notifier.py`: Discord webhook (엔트리/엑시트/에러)
- `engine/main.py`: orchestration (config 로드 → state 복원 → 스케줄 루프 → market_data → strategy → order → notifier)
- 예상 2~3일

---

End of V2-03 evidence. Generated 2026-04-24.

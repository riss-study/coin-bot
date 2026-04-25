# V2-04 Orchestration — Evidence

Task: V2-04 (notifier + position + scheduler + main)
Feature: STAGE1-V2-008
Date: 2026-04-25
Status: Done (4 모듈 sanity + 페이퍼 1-cycle end-to-end PASS)
Sub-plan: `docs/stage1-v2-relaunch.md` v2 §2.1 / §2.4

---

## 1. 신설 모듈 (~570 LOC)

```
engine/engine/
├── notifier.py   (~150 LOC) — Discord webhook + rate limit + 디바운스
├── position.py   (~165 LOC) — Position open/close + PnL + 세금 데이터
├── scheduler.py  (~110 LOC) — KST 09:05 일봉 close 트리거 (in-process)
└── main.py       (~250 LOC) — Engine orchestration
```

## 2. 모듈 책임

### notifier.py
- DiscordNotifier 클래스 (webhook URL 검증 + 디바운스)
- 메서드: notify_signal / notify_order_filled / notify_error / notify_summary
- 429 응답 시 Retry-After 따라 대기 후 1회 재시도
- 에러 디바운스 (10분, 동일 key 반복 방지)
- content 1900자 제한 (Discord 2000 제한 마진)

### position.py
- `open_position_from_order(state, buy_order)`: 매수 체결 → Position 생성 + state 저장
- `close_position_from_order(state, logs_dir, sell_order)`:
  - 매도 체결 → realized PnL 계산
  - **세금 데이터: entry + exit 두 거래 log_trade 기록** (`linked_to`, `realized_pnl_*` 필드 포함)
  - state.close_position
- `compute_unrealized_pnl(pos, current_price)`: 현재가 기반 평가손익

### scheduler.py
- `next_trigger_at(hour_kst, minute_kst, now_utc)`: KST hh:mm 다음 시각 → UTC datetime
- `sleep_until(target_utc)`: interruptible sleep (max 60s 단위 분할)
- `run_daily_loop(callback, hour_kst, minute_kst, on_error)`: 무한 루프 + 예외 처리

### main.py — Engine 클래스
- `__init__(cfg)`: state + strategies 인스턴스 + notifier (optional) + upbit client (live) + order_executor
- `restore_state()`: open positions/orders 로깅 + live 모드면 poll_status 동기화
- `process_cell(cell, trigger_utc)`: 단일 cell 시세→신호→주문→포지션→알림
- `run_cycle(trigger_utc)`: 모든 cell 순차 + 일일 요약 알림
- `run_forever()`: scheduler.run_daily_loop 진입

## 3. Sanity 결과

### 3.1 notifier.py
- Keychain `discord-webhook` 미발급 → mock 인스턴스 검증 fallback
- invalid URL 거부 ValueError ✓

### 3.2 position.py
- 매수 100,000 KRW (price 115,573,000) → entry / krw_invested=99,998 ✓
- 현재가 116,000,000 → unrealized +319 KRW (+0.32%)
- 매도 → realized +269 KRW (+0.27%) (= unrealized - exit fees 50)
- close 후 get_position(cell_key) = None ✓
- 세금 데이터 trades-2026.jsonl에 entry + exit 두 행 기록 (linked_to, realized_pnl_*)

### 3.3 scheduler.py
- next_trigger_at(9, 5, now=2026-04-25 09:00 KST) → 2026-04-25 09:05 KST ✓
- next_trigger_at(9, 5, now=2026-04-25 10:00 KST) → 2026-04-26 09:05 KST ✓
- sleep_until 2초 대기 → 2.0s 정확 ✓

### 3.4 main.py end-to-end (페이퍼)
- run_mode=paper, 3 cells (BTC_A, ETH_A, BTC_D)
- notifier disabled (webhook 미발급) → 정상 진행 (notify 호출 skip)
- restore_state: open positions/orders 0 (빈 DB) ✓
- run_cycle 1회 실행:
  - 3 cells 신호 평가 모두 hold (현 시점 진입 조건 미충족)
  - 주문 placement 0, 포지션 변화 0
  - last_run_ts 박제 ✓
- KeyboardInterrupt / 셀 단위 예외 → notify_error + 로깅 (봇 중단 X)

## 4. 룰 준수

- 일봉 close (KST 09:00 close, 09:05 평가) 박제 (config.yaml `signal_check_hour_kst=9, minute=5`)
- Strategy A/D 박제 파라미터 (W2-02 v5) 재튜닝 X — `build_strategy()` cfg 주입
- 시장가 주문 + 멱등성 (make_client_oid 분 단위 deterministic)
- 모든 거래 trades-YYYY.jsonl 영구 저장 (CLAUDE.md 박제)
- live mode → upbit client 필수 (없으면 startup 실패)
- paper mode → price_oracle 필수 (get_current_price 자동 주입)
- Discord 디바운스 10분 (동일 에러 키)
- KeyboardInterrupt 우아한 종료 (Ctrl+C)

## 5. 미확정 사항 (V2-05 책무)

- 페이퍼 fee 모델 vs Upbit 실제 paid_fee 비교 (V2-05 integration test)
- live mode 응답 폴링 (_immediate_poll) 실 호출 검증 — V2-05 사용자 API 키 후
- restart 시 incomplete 주문 (status='open') 재처리 시나리오 통합 테스트
- 동시성 (3 cells 병렬 시 SQLite WAL contention) 부하 테스트

## 6. 다음 단계 (V2-05)

- engine/tests/ 신설:
  - test_strategy_a.py / test_strategy_d.py (signal 로직 unit)
  - test_order.py (paper + live mock)
  - test_position.py (entry/exit + PnL)
  - test_state.py (idempotency + restart)
  - test_integration.py (mock Upbit + 1-cycle end-to-end)
- 사용자 API 키 발급 후 실제 Upbit 인증 호출 1회 (read-only `get_balance`) sanity
- 백테스트 결과 vs 페이퍼 데이터 ±30% 일치 검증 도구

---

End of V2-04 evidence. Generated 2026-04-25.

# V2-01 Engine Skeleton — Evidence

Task: V2-01 (engine/ 디렉토리 + venv + 기본 config 골격)
Feature: STAGE1-V2-003
Date: 2026-04-24
Status: Done (venv + config 로드 검증 PASS)
Sub-plan: `docs/stage1-v2-relaunch.md` v2 §2.1

---

## 1. 데이터 입력

- 박제 출처:
  - `docs/stage1-v2-relaunch.md` v2 (Custom bot 설계)
  - `docs/decisions-final.md` "Stage 1 v2 Tech Stack 전환" (2026-04-24)
  - `docs/candidate-pool.md` v7 (Strategy A/D 파라미터)

## 2. 사전 지정 파라미터 (박제 완료)

### Strategy A (W2-02 v5)
```yaml
ma_period: 200
donchian_high: 20
donchian_low: 10
vol_avg_period: 20
vol_mult: 1.5
sl_pct: 0.08
```

### Strategy D (W2-02 v5)
```yaml
keltner_window: 20
keltner_atr_mult: 1.5
atr_window: 14
bollinger_window: 20
bollinger_sigma: 2.0
sl_hard: 0.08
```

### Portfolio (W2-03 v9 + v2 실용)
```yaml
init_cash: 1,000,000    # 페이퍼 100만원 가상
stake_amount: 100,000   # 거래당 10만원
fees: 0.0005
slippage: 0.0005
year_freq: "365 days"   # PT-04 명시 (cycle 1 #16 방지)
max_open_positions: 3
```

### Go 기준 (v2 실용 박제)
```yaml
min_sharpe: 0.8
max_mdd: 0.50
min_trades: 10
paper_live_tolerance: 0.30
```

## 3. 결과

### 3.1 디렉토리 구조 신설

```
engine/
├── .venv/                        # Python 3.11.15 venv
├── config.yaml                   # 사전 지정 파라미터 박제
├── requirements.txt              # pyupbit 0.2.34 + deps
├── README.md
├── .gitignore
├── engine/
│   ├── __init__.py
│   └── config.py                 # 골격 완성
├── tests/                        # V2-05 예정
├── logs/ data/ secrets/          # 런타임 (gitignored, .gitkeep)
```

### 3.2 venv 설치 검증

```
Python: 3.11.15
pyupbit: 0.2.34          (PyPI 최신, 2026-04-24 실측)
yaml:    6.0.3
requests: 2.33.1
pydantic: 2.13.3
```

### 3.3 config 로드 검증 (`python -m engine.config`)

```
run_mode: paper
pairs: [('KRW-BTC', 'A'), ('KRW-ETH', 'A'), ('KRW-BTC', 'D')]
portfolio: init_cash=1,000,000, stake=100,000
strategy_a: MA=200, SL=0.08
strategy_d: Keltner=20, BB sigma=2.0
keychain services: upbit-api-access / upbit-api-secret
config OK (V2-01 골격)
```

## 4. 자동 검증

- venv Python 버전 3.11.15 (research/.venv와 일치) ✓
- pyupbit 0.2.34 PyPI 최신 확인 ✓ (2026-04-24 `pip index versions` 실측)
- config.yaml YAML 파싱 성공 ✓
- dataclass 타입 검증 통과 ✓
- Keychain 조회 함수 `get_keychain_secret` 작성 (실제 호출은 V2-05 integration 때)

## 5. 룰 준수

- 사전 지정 파라미터 (Strategy A/D) W2-02 v5 박제값 그대로 ✓
- year_freq='365 days' 명시 박제 (PT-04 cycle 1 #16 방지) ✓
- Secrets = Keychain 경로 박제 (v1 decisions-final.md 유지) ✓
- Docker 미도입 (v2 초기 단일 프로세스) ✓
- 외부 lib 실측 기반 (pyupbit 0.2.34 PyPI 최신, 2026-04-24 실측) ✓

## 6. 리뷰

- backtest-reviewer: N/A (V2-01은 백테스트 아닌 인프라 골격)
- 외부 감사: N/A (V2-04 완료 후 호출 예정)
- 사용자 승인: "착수해" (2026-04-24)

## 7. 다음 단계 (V2-02)

- `engine/market_data.py`: pyupbit `get_ohlcv_from` + 로컬 캐싱
- `engine/state.py`: SQLite 상태 DB + 재시작 복원
- `engine/logger.py`: 구조화 로깅 + 거래 JSON 영구 저장
- 예상 3~5일

---

End of V2-01 evidence. Generated 2026-04-24.

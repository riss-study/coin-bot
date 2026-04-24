# engine/ — Stage 1 v2 Custom bot (pyupbit 기반)

> **상태**: V2-01 골격 (2026-04-24)
> **목적**: 50만원 한정 라이브 투입 (페이퍼 2-4주 → 10만원 → 50만원 단계 투입)
> **의존성**: pyupbit 0.2.34 (실측 검증 2026-04-24)

## 설정 + 실행

### 1. venv 생성 (최초 1회)

```bash
cd engine
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Keychain에 API 키 저장 (사용자)

`docs/user-setup-guide.md` 참조. 3~4단계 완료 후:

```bash
security add-generic-password -s "upbit-api-access" -a "coin-bot" -w "<ACCESS_KEY>"
security add-generic-password -s "upbit-api-secret" -a "coin-bot" -w "<SECRET_KEY>"
security add-generic-password -s "discord-webhook" -a "coin-bot" -w "<WEBHOOK_URL>"
```

### 3. Config 검증

```bash
source .venv/bin/activate
python -m engine.config  # config.yaml 로드 sanity
```

### 4. 페이퍼 트레이딩 시작 (V2-04 이후)

TBD — V2-04에서 `main.py` 작성 후 실행 방법 추가.

## 디렉토리 구조

```
engine/
├── .venv/                        # 의존성 격리 (gitignored)
├── config.yaml                   # 사전 지정 파라미터 (git tracked)
├── requirements.txt              # pyupbit 0.2.34 + deps
├── .gitignore
├── engine/                       # 파이썬 패키지
│   ├── __init__.py               # (V2-01 완료)
│   ├── config.py                 # (V2-01 완료) Keychain + YAML
│   ├── market_data.py            # (V2-02 예정) OHLCV
│   ├── strategies/               # (V2-03 예정)
│   │   ├── strategy_a.py
│   │   └── strategy_d.py
│   ├── order.py                  # (V2-03 예정)
│   ├── state.py                  # (V2-02 예정) SQLite
│   ├── scheduler.py              # (V2-04 예정)
│   ├── position.py               # (V2-03 예정)
│   ├── notifier.py               # (V2-04 예정) Discord
│   ├── logger.py                 # (V2-02 예정)
│   └── main.py                   # (V2-04 예정) orchestration
├── tests/                        # (V2-05 예정)
├── logs/                         # 런타임 (gitignored)
├── data/                         # SQLite DB (gitignored)
└── secrets/                      # env 임시 (gitignored)
```

## 박제 출처

- `docs/stage1-v2-relaunch.md` v2 (v2 설계)
- `docs/decisions-final.md` "Stage 1 v2 Tech Stack 전환" (2026-04-24)
- `docs/candidate-pool.md` v7 (Strategy A/D 파라미터)
- `docs/user-setup-guide.md` (사용자 설정 가이드)

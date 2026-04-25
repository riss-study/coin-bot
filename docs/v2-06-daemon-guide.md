# V2-06 페이퍼 트레이딩 Daemon 가이드

Task: V2-06
Feature: STAGE1-V2-011
Date: 2026-04-26
Status: 가이드 (사용자 직접 실행 절차)

박제 출처: `docs/stage1-v2-relaunch.md` v2 §2.1 (V2-06 페이퍼 관측), `engine/launchd/com.coinbot.engine.plist`

---

## 0. 진입 조건 (모두 충족 필수)

- [x] V2-05 63 tests PASS + 실 Upbit 인증 sanity OK (2026-04-26)
- [x] Keychain 3종 발급: `upbit-api-access` / `upbit-api-secret` / `discord-webhook`
- [x] `engine/config.yaml` `run_mode: paper` 박제
- [x] `engine/logs/` 디렉토리 존재 (V2-04/05 sanity 시 자동 생성됨; 신규 환경에서는 §2 `--once` 1회 실행이 자동 생성)
- [ ] **본 가이드 절차 1~5 완료** (사용자 직접 실행)

---

## 1. macOS Sleep 비활성화 (필수)

페이퍼 daemon은 KST 09:05에 in-process scheduler로 트리거. macOS sleep 상태에서는 trigger missed → 거래 시뮬레이션 누락.

### 1.1 시스템 환경설정 변경

1. `시스템 설정` → `배터리` → `옵션…` (또는 `에너지 절약기`)
2. **"디스플레이가 꺼졌을 때 자동으로 잠자기"** → 끔
3. **"디스플레이 끄기 시간"** → '안 함' 권장 (또는 가능한 가장 긴 시간)
4. 노트북: 전원 어댑터 연결 시 sleep 끄기 (배터리 사용 시 sleep 허용)
5. 데스크톱: 항상 sleep 끄기

### 1.2 검증

```bash
pmset -g | grep -E "sleep|displaysleep"
# 기대: sleep 0, displaysleep 0 (또는 매우 큰 값)
```

### 1.3 대안 (sleep을 끌 수 없는 경우)

`caffeinate` 백그라운드 실행으로 sleep 방지:

```bash
# -i: idle sleep 방지 / -s: system sleep 방지 (AC 전원 시) / -d: display sleep 방지
nohup caffeinate -dis -t 86400 > /dev/null 2>&1 &
# -t 86400 = 24시간. cron 또는 launchctl로 일일 갱신 권장.
```

> **주의**: caffeinate는 idle/system sleep만 방지. **lid 닫음(clamshell) sleep은 막지 못함** — 노트북 사용 시 §1.1 시스템 환경설정 필수 + 외부 모니터/키보드/AC 연결 권장. 데스크톱은 영향 없음.

---

## 2. Daemon 사전 검증 (`--once` 모드)

launchctl 등록 전에 1회 cycle 수동 실행하여 정상 동작 확인.

```bash
cd /Users/riss/project/coin-bot/engine
source .venv/bin/activate
python -m engine.main --once 2>&1 | tee /tmp/coinbot-once.log
```

기대 출력:
- `engine_starting` (run_mode=paper, pairs=[(KRW-BTC, A), (KRW-ETH, A), (KRW-BTC, D)])
- `notifier_initialized` (Discord webhook 발견)
- `state_restored` (open_positions=0, open_orders=0)
- `cycle_start` → 각 cell `signal_evaluated` (action=hold 가능, 정상)
- `cycle_done`
- 종료 코드 0

**Discord 채널 확인**: 일일 요약 메시지 (`Daily summary (paper) — 2026-04-26 ...`) 1건 도착해야 정상.

문제 시:
- `Keychain secret 조회 실패` → `security find-generic-password -s discord-webhook -a coin-bot -w` 직접 호출하여 확인
- `pyupbit` 네트워크 오류 → 인터넷 + Upbit API 상태 확인
- 그 외 → `engine/logs/engine.log` 마지막 100줄 점검

---

## 3. launchd 등록

### 3.1 plist 복사 + 등록

```bash
cp /Users/riss/project/coin-bot/engine/launchd/com.coinbot.engine.plist ~/Library/LaunchAgents/

# Modern (macOS 10.10+, 권장):
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.coinbot.engine.plist

# Legacy (작동은 하나 향후 deprecated 가능):
# launchctl load ~/Library/LaunchAgents/com.coinbot.engine.plist

launchctl list | grep coinbot
# 기대: PID    Status    com.coinbot.engine
#       12345   0         com.coinbot.engine
```

PID가 표시되면 daemon 실행 중. Status `0` = 정상.

### 3.2 첫 cycle 확인

```bash
tail -f /Users/riss/project/coin-bot/engine/logs/launchd.out.log
# Ctrl+C로 빠져나오기
```

`scheduler_started` + `scheduler_next_trigger` 로그 보이면 성공. 다음 KST 09:05 까지 sleep.

### 3.3 종료/재시작

```bash
# Modern 종료:
launchctl bootout gui/$(id -u)/com.coinbot.engine

# Legacy 종료:
# launchctl unload ~/Library/LaunchAgents/com.coinbot.engine.plist

# 재등록 (코드 변경 후):
launchctl bootout gui/$(id -u)/com.coinbot.engine
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.coinbot.engine.plist
```

---

## 4. 모니터링

### 4.1 매일 (사용자 책무)

- [ ] **Discord 채널**에 매일 KST 09:05~09:10 사이 `Daily summary` 메시지 도착 확인
- [ ] 매수/매도 신호 발생 시 `BUY filled` / `SELL filled` 메시지 도착 확인 (notifier.py 본문 emoji는 Discord 채널에서만 표시)
- [ ] 에러 알림 `ERROR [key]` 발생 시 즉시 점검 (debounce 10분)

### 4.2 주 1회 (사용자 책무)

```bash
# daemon 살아있는지
launchctl list | grep coinbot

# 최근 7일 trades
ls -la engine/logs/trades-*.jsonl
wc -l engine/logs/trades-*.jsonl

# 비교 도구 (§5)
# CRITICAL 정정 (2026-04-26): compare 도구는 vectorbt 의존 → research/.venv 환경에서 호출.
# engine/.venv에는 vectorbt 미설치 (production 의존성 분리 유지).
cd /Users/riss/project/coin-bot
source research/.venv/bin/activate
PYTHONPATH=engine python -m engine.scripts.compare_backtest_paper --days 7
```

---

## 5. 1주차 마감 리뷰 체크리스트

페이퍼 시작 후 7일째 시점에 다음 항목 점검 (사용자 + Claude 협업).

### 5.1 정량

- [ ] daemon uptime ≥ 6일 (sleep/crash로 1일 정도 누락 허용)
- [ ] 매일 `Daily summary` Discord 알림 7건 (또는 daemon 가동 시간 비례)
- [ ] 신호 발생 횟수 (Strategy A Donchian 20 → 평균 월 1~2회 예상, 1주차 0회 정상 가능)
- [ ] 체결 지연 (signal → order placement < 5초)
- [ ] 체결가 vs 1초 후 현재가 슬리피지 < 0.05% (페이퍼 fee 모델 검증)

### 5.2 정성

- [ ] Discord 알림 텍스트 가독성 (cell_key, price, volume, fees 모두 표시)
- [ ] 에러 로그 (`engine.log`, `launchd.err.log`) 0건
- [ ] sleep으로 인한 missed cycle 횟수 (sleep 비활성화 검증)

### 5.3 Go/No-Go (4주 마감 후 판정)

박제 (`docs/stage1-v2-relaunch.md` §1.2):

| 기준 | 박제값 |
|------|-------|
| Sharpe (페이퍼 4주) | ≥ 0.8 |
| MDD (페이퍼 4주) | ≤ 50% |
| trades (페이퍼 4주) | ≥ 10 |
| 페이퍼 vs 백테스트 | ±30% 이내 |

미달 시 V2-07 라이브 진입 차단 + 학습 모드 또는 전략 패밀리 교체.

---

## 6. 트러블슈팅

| 증상 | 원인 후보 | 점검 |
|------|----------|------|
| daemon 즉시 종료 | venv path 오류 | `engine/launchd/com.coinbot.engine.plist` `ProgramArguments[0]` 경로 확인 |
| Keychain 조회 실패 | service/account 박제 불일치 | `security find-generic-password -s upbit-api-access -a coin-bot -w` 직접 호출 |
| 09:05 미트리거 | macOS sleep | `pmset -g log | grep -i sleep | tail -20` |
| Discord 미알림 | webhook URL 만료/삭제 | Discord 서버 webhook 재발급 → Keychain 갱신 |
| `pyupbit` rate limit | 호출 빈도 초과 | Upbit 10 req/s, 본 봇 1 cycle ≤ 10 호출 (정상) |

---

## 7. 다음 단계 (V2-07 진입 조건)

V2-06 4주 운영 + Go 기준 충족 시:

- V2-07 10만원 라이브 (config.yaml `run_mode: live` + Keychain 입금 후 잔고 확인)
- V2-08/09 50만원까지 단계적 투입 (V2-07 1주 안정 후)

V2-06 미달 시:
- V2-07 진입 차단 (사용자 무조건 결정 대기)
- 페이퍼 추가 관측 또는 전략 패밀리 교체 검토

---

End of V2-06 daemon guide. Generated 2026-04-26.

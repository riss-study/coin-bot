# Stage 1 v2 재시작 — 라이브 경로 (최소 박제)

> **Feature ID**: STAGE1-V2-001 / STAGE1-V2-002 (Tech Stack 전환)
> **작성일**: 2026-04-24
> **상태**: **v2** (Freqtrade → **Custom bot with pyupbit** 전환, 2026-04-24 실측 기반 사용자 재승인 "ㄱㄱ 그렇게 하자")
> **본질 목표**: 50만원 한정 라이브 투입. 학술 박제 루프 최소화.

---

## 0. 재시작 근거

### 0.1 v1 종결 확인

- Stage 1 v1 = 학습 모드 전환 (W3-01 No-Go, 사용자 옵션 C 채택 2026-04-22)
- Stage 1 v1 결과는 **역사 기록으로 보존** ([`stage1-retrospective-2026-04-24.md`](./stage1-retrospective-2026-04-24.md) 참조)
- v2는 **새 cycle**. v1 기준(DSR/Pardo/stability 5/5 등)에 얽매이지 않음.

### 0.2 v1 실패 원인 (재시작 필요성)

- **학술적 엄격성 과잉**: DSR V_reported floor → V_empirical 전환 + stability 5/5 + Pardo 70-80%가 **50만원 라이브 투입**이 아닌 **논문 제출용** 수준
- W2-03 Go cells (Sharpe > 0.8, MDD < 50%, Trade > 5) 5개는 **실용 기준으로는 충분**하나 W3-01 walk-forward stability 5/5에서 발목 잡힘
- 사용자 명시 ("당장 현금 넣고 돌리기 위한 걸 하고자 하는건데", 2026-04-24) = 본질 목표 라이브 투입 재확인

### 0.3 cycle 1 #5 재발 여부 (정직한 판정)

- **cycle 1 #5 = "Go 기준 사후 완화"** → **본 v2는 사후 완화 아님**
- 근거: v1은 공식 종결 (사용자 옵션 C "3" 2026-04-22). v1 결과를 "뒤집거나 재해석" 하지 않음. v2는 **독립된 새 cycle**.
- v1 학술 기준 → v2 실용 기준 전환은 **사용자의 본질 목표(50만원 라이브) 재인식**에서 비롯. 결과 본 후 기준 완화가 아닌, **프로젝트 목적 재평가**.

---

## 1. v2 핵심 원칙

### 1.1 전략 선택 (W2-03 Go cells 중 3개 채택)

| Strategy | Pair | v2 채택 여부 | 근거 |
|----------|------|:-----------:|------|
| **A** | **BTC** | ✓ | W2-03 Sharpe 1.04, MDD -22%, 14 trades. 5년 검증 + 평균 수익 양호 |
| **A** | **ETH** | ✓ | W2-03 Sharpe 1.14, MDD -20%, 10 trades. BTC와 독립 페어 |
| **D** | **BTC** | ✓ | W2-03 Sharpe 1.18, MDD -32%, 25 trades. 거래 활발 |
| D | ETH | 유예 | W2-03 Sharpe 1.09 but W3-01 fold 2/5 음수. 일단 제외, BTC_D 안정 시 추가 검토 |
| **C** | - | **제외** | W3-01 fold 5/5 N/A. 연 1 trade 수준 = 라이브 부적합 |
| B | - | 제외 유지 | W1 Deprecated (구조적 엣지 부재) |

**채택 확정**: **3 cells (BTC_A, ETH_A, BTC_D)**.

### 1.2 Go 기준 (라이브 진입용, v2 박제)

**학술 기준 제거**:
- ~~DSR_z > 0~~ (제거, Bailey 2014는 논문용)
- ~~Stability 5/5 fold pass~~ (제거, Pardo는 기관 자금 운용용)
- ~~다중 검정 Bonferroni 보정~~ (제거)

**실용 기준 (신규 박제)**:
- **백테스트 Sharpe > 0.8** (W2-03 3 cells 전부 충족)
- **백테스트 MDD < 50%** (W2-03 3 cells 전부 충족)
- **백테스트 Trade ≥ 10** (BTC_A 14 / ETH_A 10 / BTC_D 25 전부 충족)
- **페이퍼 트레이딩 2~4주 + 백테스트 대비 ±30% 이내** (결과 일치 확인)

### 1.3 walk-forward 처리

- **생략**: 학술적 validation 목적이었음. 라이브 기준 아님.
- **대체**: 페이퍼 트레이딩 2~4주 = 사실상 live forward test (out-of-sample)
- 근거: 5년 백테스트 + 2~4주 페이퍼 + 50만원 소액 라이브 = **총 3단계 검증**. Walk-forward 불필요

### 1.4 50만원 라이브 단계적 진입

- **페이퍼 2주 통과**: 10만원 라이브 (시험 운영 1~2주)
- **10만원 1~2주 통과**: 50만원 추가 (총 50만원 한도 내)
- 실제 주문/체결 오차 + 슬리피지 + 수수료 실측 확인

---

## 2. v2 실행 계획 (v2 Tech Stack 전환: Freqtrade → Custom bot)

### 2.0 Tech Stack 전환 근거 (2026-04-24 실측)

- **Freqtrade 공식 Upbit 미지원** (supported list: Binance/Kraken/Kucoin 등 글로벌 대형 중심, Upbit 없음)
- **ccxt Upbit 버그** (issue #7235): `order['amount'] = None` → Freqtrade `update_trade_state` `TypeError`. 라이브 에러 발생 위험
- **빗썸도 대안 아님**: python-bithumb 커뮤니티 성숙도 낮음 + Bithumb V2 API ccxt 미완전 지원
- **pyupbit 0.2.34 실측 확인 (2026-04-24)**:
  - PyPI 최신 버전
  - 주문 API 완전 기능: `buy/sell_market_order`, `buy/sell_limit_order`, `cancel_order`, `get_order`, `get_balance(s)`, WebSocket
  - Upbit API Rate Limit: 주문 8/s 200/min, 기타 30/s 900/min, 시세 10/s 600/min (3 cells 일봉 운영에 여유)
  - `Remaining-Req` 헤더 자가 모니터링 (`contain_req=True`)
- **Custom bot 전환 = cycle 1 #5 사후 완화 아님**: v1 "Freqtrade + ccxt + pyupbit" 박제는 Upbit 호환성 이슈 몰랐을 때. v2 실측 기반 교정

### 2.1 Task 목록 (v2 재조정)

| Task | 기간 | 설명 | Blocks | 상태 |
|------|:----:|------|--------|------|
| V2-01 | 1~2일 | `engine/` 디렉토리 신설 + venv 분리 + pyupbit 설치 + config.py 골격 | V2-02 | **DONE** 2026-04-25 |
| V2-02 | 3~5일 | Module 골격: `config` + `market_data` + `state` (SQLite) + `logger` | V2-03 | **DONE** 2026-04-25 |
| V2-03 | 3~5일 | Strategy 이식 (research/ 재사용) + `order` 모듈 (주문/취소/조회 + 재시도 + 멱등성) | V2-04 | **DONE** 2026-04-25 |
| V2-04 | 2~3일 | `scheduler` (일봉 close KST 09:00 트리거) + `main` orchestration + Discord `notifier` | V2-05 | **DONE** 2026-04-25 |
| V2-05 | 3~5일 | Unit test + integration test (주문 mock + 상태 복원 시나리오) | V2-06 | **DONE** 2026-04-26 (63 tests PASS) |
| V2-06 | 2~4주 | 페이퍼 트레이딩 관측 (BTC_A, ETH_A, BTC_D) + 백테스트 대비 오차 기록 | V2-07 | **IN PROGRESS** 2026-04-26 03:00 UTC daemon bootstrap (PID 87918) |
| V2-07 | - | 페이퍼 Go/No-Go + 10만원 라이브 결정 | V2-08 | 대기 (V2-06 4주 후) |
| V2-08 | 1~2주 | 10만원 라이브 운영 + 실체결 검증 | V2-09 | 대기 |
| V2-09 | - | 10만원 Go/No-Go + 50만원 추가 투입 결정 | - | 대기 |

**총 최소 5~7주** (실측 기반 현실적 추정).

### 2.2 환경 구축 스택 (v2 확정)

- **Custom bot**: 자체 Python 프로세스 (launchd macOS 24/7)
- **업비트 연동**: **pyupbit 0.2.34** (네이티브, 실측 검증)
- **DB**: **SQLite** (초기) → 라이브 운영 시 PostgreSQL 검토 (V2-08 이후)
- **Secrets**: **macOS Keychain → 환경 변수** (Docker는 미필요, 단일 프로세스)
- **알림**: Discord webhook (default, v1 박제 유지), KakaoTalk urgent (추후)
- **Host**: macOS 24/7 (v1 박제 유지)
- **Docker**: 초기 미도입 (단일 프로세스), 라이브 운영 후 재검토

### 2.3 v1 자산 재활용

- **Strategy 코드**: `research/notebooks/02_*.ipynb` (Strategy A) + `08_insample_grid.ipynb` (Strategy D) → **`engine/strategies/` Python 모듈로 이식** (Freqtrade Strategy class 아님, 자체 구조)
- **데이터**: `research/data/KRW-BTC_1d_frozen_20260412.parquet` + `KRW-ETH_*` (v1 freeze 그대로 활용)
- **파라미터**: `docs/candidate-pool.md` Strategy A/D 박제값 그대로
- **Evidence 경로**: `.evidence/v2-XX-*.md` 신설

### 2.4 Custom bot 모듈 구조 (예상 ~1,560 LOC)

```
engine/
├── .venv/                        # pyupbit 0.2.34 + 의존성 분리
├── engine/
│   ├── config.py                 # env/Keychain secrets 로드 (~50 LOC)
│   ├── market_data.py            # pyupbit get_ohlcv_from + 캐싱 (~100)
│   ├── strategies/
│   │   ├── strategy_a.py         # Trend Following (MA200 + Donchian + Volume) (~120)
│   │   └── strategy_d.py         # Volatility Breakout (Keltner + Bollinger) (~130)
│   ├── order.py                  # 주문 생성/취소/조회 + 재시도 + 멱등성 (~200)
│   ├── state.py                  # SQLite 상태 DB + 재시작 복원 (~150)
│   ├── scheduler.py              # 일봉 close KST 09:00 트리거 (~80)
│   ├── position.py               # 포지션 관리 + PnL + 세금 데이터 (~150)
│   ├── notifier.py               # Discord webhook (~80)
│   ├── logger.py                 # 구조화 로깅 + 거래 JSON 영구 저장 (~100)
│   └── main.py                   # 전체 orchestration (~150)
├── tests/
│   ├── test_strategy_a.py
│   ├── test_strategy_d.py
│   ├── test_order.py
│   ├── test_state.py
│   └── test_integration.py       # 통합 (~300 LOC)
├── config.yaml                   # 전략/페어/파라미터 사전 지정 (git tracked)
├── secrets/                      # gitignored (Keychain 추출 후 env 주입)
├── logs/                         # gitignored
└── data/                         # SQLite DB (gitignored)
```

### 2.5 숨은 복잡도 (솔직 고지)

1. **재시작 복원 로직**: 프로세스 crash 시 미체결 주문 / 포지션 상태 복원 (state.py 담당)
2. **동시성**: 3 cells (BTC_A, ETH_A, BTC_D) 병렬 실행 레이스 컨디션 주의. 초기 단순화: 순차 실행 → 검증 후 병렬 전환
3. **슬리피지 모니터링**: 백테스트 예상가 vs 실체결가 차이 지속 기록 → V2-06 페이퍼 단계 핵심
4. **멱등성**: 주문 재시도 시 이중 주문 방지 (client_oid 같은 고유 ID 필요)
5. **세금 데이터**: 모든 거래 JSON 영구 저장 (CLAUDE.md 박제), 연말 국세청 신고용
6. **자바 개발자 Python asyncio 학습 곡선**: ~1주 추가
7. **Discord webhook 설정**: 서버 생성 + webhook URL 발급 (10분 단순)

---

## 3. v2 의도된 단순화 (v1 대비)

| 항목 | v1 | v2 |
|------|----|----|
| Walk-forward | 5-fold × 6개월 엄격 | **생략** (페이퍼가 대체) |
| DSR (Bailey 2014) | Go 기준 포함 | **제거** |
| V 선택 논쟁 | V_reported floor vs V_empirical | **해당 없음** (DSR 제거) |
| Multiple testing | Bonferroni 고려 | **제거** |
| 외부 감사관 2차 호출 | 매 결정 전 | **축소** (주요 결정 시 1회) |
| 박제 sub-plan 개정 | v1→v2→...→v9 수준 | **최소 박제** (v1 직접 수정) |
| Go 기준 | Sharpe>0.8 AND DSR>0 AND stability 5/5 | **Sharpe>0.8 AND MDD<50% AND trades≥10 + 페이퍼 ±30%** |

**정당화**: 50만원 = 최대 손실 50만원. 감당 가능 규모. 엄격 기준은 기관 자금 운용용. 개인 학습 + 소액 라이브에는 과잉.

---

## 4. 리스크 + 완화

| 리스크 | 영향 | 완화 |
|--------|------|------|
| 학술 기준 제거 후 오버핏 전략 선택 | High | W2-03 Go cells 5개 중 3개만 채택 (stability W3-01에서 약함 확인된 것 제외) |
| Custom bot 이식 오차 (Strategy A/D 구현 불일치) | High | 페이퍼 2~4주 + 백테스트 ±30% 이내 확인 + unit test 커버리지 |
| 페이퍼와 라이브 체결 오차 (슬리피지/지연) | Medium | 10만원 → 50만원 2단계 투입 + 슬리피지 모니터링 모듈 (position.py) |
| 업비트 API 변경 / 제한 | Medium | pyupbit 0.2.34 검증된 API 버전 고정. Remaining-Req 헤더 자가 모니터링 |
| 재시작 복원 실패 (미체결 주문 상태 손실) | High | state.py SQLite + 시작 시 open orders 재조회 + 통합 테스트 |
| 동시성 레이스 컨디션 (3 cells 병렬) | Medium | 초기 순차 실행 → 페이퍼 검증 후 병렬 전환 |
| 멱등성 위반 (주문 재시도 시 이중 주문) | High | client_oid 고유 ID + 주문 전 state 확인 |
| 자바 개발자 Python asyncio 학습 곡선 | Medium | V2-01~V2-02 기간에 학습 시간 ~1주 할당 |
| cycle 1 #5 재발 "사후 완화" 의심 | Low | v1 공식 종결 + v2 새 cycle + 본질 목표 재인식 + Freqtrade 불가 실측 증거 (§2.0) |
| cycle 1 #16 "외부 lib 추측" 재발 | Low | 2026-04-24 pyupbit 실측 완료 (주문 API / rate limit / PyPI 최신). 재발 차단 |

---

## 5. 관련 문서

- v1 종결 상세: [`decisions-final.md`](./decisions-final.md) "W3-01 Walk-forward No-Go 결정 + 프레임 C 학습 모드 전환"
- v1 회고: [`stage1-retrospective-2026-04-24.md`](./stage1-retrospective-2026-04-24.md)
- 전략 파라미터: [`candidate-pool.md`](./candidate-pool.md) Strategy A/D 섹션
- v1 아키텍처: [`architecture.md`](./architecture.md) Freqtrade + Docker + Cloudflare Tunnel 설계

---

## 6. 다음 단계

### 지금 (오늘/내일)

1. 본 문서 박제 + handover/candidate-pool/execution-plan 갱신 + 커밋
2. V2-01 착수: Freqtrade 설치 + 업비트 연결 기본 확인

### 이번 주

- V2-01 ~ V2-05 (환경 구축 + Strategy A/D 이식 + 페이퍼 첫 실행 + 테스트)

### 다음 주부터 (2~4주)

- V2-06 페이퍼 트레이딩 관측 (launchd daemon)
- 백테스트 대비 오차 기록

### 페이퍼 통과 후

- V2-07 10만원 라이브
- V2-08/09 50만원까지 단계적 투입

(라벨 동기화 정정 2026-04-26 — §2.1 표 V2-05="Unit test + integration test"와 일치. 이전 V2-05="페이퍼 관측"은 stale 라벨)

---

End of Stage 1 v2 relaunch plan. Generated 2026-04-24.

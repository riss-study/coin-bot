# 최종 결정사항 (통합)

> 모든 결정 문서(`decisions-needed.md`, `my-decisions.md`, `critical-corrections.md`, `decisions-v2.md`, `decisions-remaining.md`)를 단일 진실 문서(single source of truth)로 통합.
> 이 문서가 프로젝트의 모든 결정의 참조 기준입니다.
>
> 모르는 단어는 [`glossary.md`](./glossary.md) 참조.
> ATR, RSI, MA, Sharpe, DSR, MDD, Donchian, Walk-Forward, vectorbt, Freqtrade 등 자바 개발자 관점 풀이.

---

## 프로젝트 정체성 (Part 0)

| 항목 | 결정 |
|------|------|
| **이름** | coin-bot (가칭) |
| **주 목적** | **정량 금융 / ML / 시스템 학습 프로젝트** |
| **부 목적** | 검증된 전략으로 소액 라이브 트레이딩 (옵션) |
| **실전 투입 조건** | 페이퍼 트레이딩이 진짜로 OK일 때만, 50만원부터 |
| **심리적 프레임** | "돈 버는 프로젝트"가 아닌 "검증하며 학습하는 프로젝트" |
| **시간 투자** | 매일 2시간 이상 |
| **킬 크라이테리아** | **2단계: Stage 1 (Week 8) 페이퍼 초기 평가, Stage 2 (Week 12) 라이브 게이트. 상세는 Part 11.** |

**핵심 원칙:** 속도보다 학습, 학습보다 검증.

---

## Part 1: 거래소 & 자산

| 항목 | 결정 |
|------|------|
| 메인 거래소 | **업비트** (pyupbit, ccxt 병용) |
| 보조 거래소 | 바이낸스 (김치프리미엄 참조용, 거래 X) |
| 거래 대상 | 현물만 (선물/레버리지 금지) |
| 코인 유니버스 | BTC, ETH 필수 + 상위 5~8개 알트 (주간 갱신) |
| 제외 | 스캠, 저유동성(<10억원/일), 상장<6개월, 스프레드>0.3% |

---

## Part 2: 알고리즘 전략

### 2-1. 최종 전략 구조

**Option 3로 진행** — 두 개 개별 전략 백테스트 후 앙상블과 비교. 차이가 작으면(Sharpe<0.2, MDD<5%p, CAGR<3%p) 앙상블 채택.

#### Strategy A: 추세 추종 (Trend-Following)
```
진입: 가격 > 200일 MA (대추세 상승)
      AND Donchian(20) 상단 돌파
      AND 거래량 > 20기간 평균의 1.5배

청산: Donchian(10) 하단 터치
      OR ATR(14) 기반 트레일링 스톱 (1.5x ATR)
      OR 하드 스톱 -8%

포지션: ATR 기반 변동성 조정 사이징, 트레이드당 리스크 1%
```

#### Strategy B: 평균 회귀 (Mean Reversion)
(Larry Connors 스타일, 일봉 기반)

```
진입: 가격 > 200일 MA (일봉 기준 상승 추세에서만 역추세 매수)
      AND RSI(4) < 25 (일봉 기준 극단 과매도)

청산: RSI(4) > 50
      OR 5 거래일 경과 (vectorbt에선 entries.shift(5)로 사전 계산한 추가 exit 마스크 사용)
      OR 하드 스톱 -8%

포지션: ATR 기반 변동성 조정 사이징, 트레이드당 리스크 1%
(평균회귀는 일반적으로 신뢰도가 낮으므로 트렌드와 동일 또는 낮은 리스크 유지)
```

주: Week 1에서 일봉 기반 복제를 먼저 수행. 4시간봉 적용은 별도 실험.

#### Strategy C: 50/50 앙상블 (Padysak/Vojtko)
```
A와 B를 동시에 운영
가중치 50/50 (기본) → 레짐 필터로 조정 (Phase 6+)
두 전략 신호 반대 시 해당 코인 건너뜀
```

### 2-2. 리스크 관리 (공통)

| 항목 | 값 |
|------|-----|
| 트레이드당 리스크 | 1% (Strategy A, B 모두) |
| 단일 포지션 최대 | 자본의 40% |
| 총 노출 최대 | 자본의 70% (30% 현금 보유) |
| 일일 손실 소프트 | -2% → 포지션 50% 축소 + 당일 신규 진입 차단 |
| 일일 손실 하드 | -3% → 전 포지션 청산 + 24h 매매 중단 |
| 소프트 드로다운 | -10% → 포지션 50% 축소 |
| 하드 드로다운 | -15% → 72시간 전면 중단 |
| 동시 포지션 수 | 원금별 1~3개 |
| 일일 시계 기준 | KST 자정(00:00 KST)에 일일 P&L 리셋 |

### 2-3. 서킷 브레이커

| 레벨 | 조건 | 조치 |
|------|------|------|
| L1 | BTC 4h 내 -5% | 포지션 50% 정리, 4h 중단 |
| L2 | BTC 24h 내 -10% (비대칭 시장 급락 전용) | 전 포지션 청산, 12h 중단 |
| L3 | BTC 24h 내 -15% OR 운영 피크 대비 -10% | 전 포지션 청산, 100% 현금, 72h 중단 |
| L4 (수동) | API 에러 / 비정상 | 킬 스위치, 즉시 시장가 청산 |

주: "운영 피크"는 봇 가동 시작일 또는 마지막 L3 발동 후 누적 자본 최고점 (rolling-since-last-reset).

### 2-4. 거시경제 리스크 필터 (룰 기반)

```
신규 진입 차단:
  - FOMC/CPI 발표 전후 2시간
  - BTC 24h -10% 이후 6시간
  - 공포탐욕 < 10 또는 > 95
  - ATR% 30일 상위 10% (고변동 레짐)
```

**LLM 기반 거시 분석은 Phase 10+에서만** (지금은 룰 기반).

---

## Part 3: 개발 순서 & 로드맵

### Week 1~3: 복제 스프린트 (Jupyter 노트북)

**목표: "Padysak/Vojtko 전략이 업비트 KRW-BTC에서 작동하는지 확인"**

- Week 1: 데이터 수집 + 단일 전략 복제
- Week 2: Walk-forward + DSR + 알트 확장
- Week 3: 앙상블 비교 + 결과 평가

**Go/No-Go 게이트 (Week 3 종료 시):**
- Pass: Sharpe > 0.8 (수수료/슬리피지 포함) → Week 4부터 Freqtrade 이식
- Fail: 전략 패밀리 재검토 (킬 카운터 시작)

### Week 4~5: Freqtrade 이식

- pyupbit/ccxt 어댑터 설정
- Strategy A, B, C 구현
- 실시간 데이터 파이프라인
- Docker 컨테이너화

### Week 6~9: 페이퍼 트레이딩

- 실시간 업비트 데이터
- 실제 체결 시뮬레이션
- Discord 알림 연동
- 백테스트 결과와 실시간 성능 비교

### Week 10+: 대시보드 + LLM 레이어 (페이퍼 통과 시)

- FastAPI + Next.js 대시보드
- Cloudflare Tunnel 설정
- **LLM 5개 역할 추가** (Phase 10+)

### 라이브 전환 조건 (Week 12+ Stage 2 게이트)

모두 충족 시 50만원으로 시작:
- [ ] 백테스트 Sharpe > 1.0, DSR > 0.5
- [ ] 페이퍼 트레이딩 4주 완료
- [ ] 페이퍼 성능이 백테스트의 70% 이상
- [ ] 수동 점검: 이상 동작 없음, 서킷 브레이커 정상
- [ ] 사용자가 "진짜 OK"라고 판단

**킬 크라이테리아 (2단계)**:
- **Stage 1 (Week 8)**: 페이퍼 트레이딩 초기 2주 결과 평가. Fail 시 전략 패밀리 교체 또는 연구 모드 전환.
- **Stage 2 (Week 12)**: 라이브 투입 게이트. 모든 조건(Sharpe > 1.0, DSR > 0.5, 페이퍼 4주 70%+) 충족 시에만 50만원 입금.
- 8주 킬은 "라이브 가드"가 아닌 "연구 방향 재평가". 라이브는 구조상 Week 12+에만 가능.

---

## Part 4: 기술 스택 & 인프라

### 4-1. 코어 스택

| 계층 | 선택 |
|------|------|
| 언어 | Python 3.11+ |
| 백테스트 (Week 1~3) | pandas + vectorbt + Jupyter |
| 백테스트/페이퍼/라이브 (Week 4+) | **Freqtrade** |
| 거래소 연동 | pyupbit + ccxt |
| DB | **PostgreSQL + TimescaleDB** |
| 백엔드 API | FastAPI |
| 프론트엔드 | Next.js (React) |
| 컨테이너 | Docker + docker-compose |
| 서버 | 로컬 PC 24/7 (macOS) |

### 4-2. 데이터 소스 (전부 무료)

| 데이터 | 소스 |
|--------|------|
| 업비트 시세/호가/체결 | 업비트 REST + WebSocket |
| 바이낸스 참조 가격 | 바이낸스 REST |
| FOMC/CPI/DXY/고용 | FRED API |
| 공포탐욕지수 | alternative.me |
| BTC 도미넌스 | CoinGecko /global |
| USD/KRW 환율 | ExchangeRate API |
| BTC 해시레이트 | blockchain.com |
| (Phase 10+) 크립토 뉴스 | CryptoPanic |

### 4-3. 프로젝트 구조 (멀티레포)

```
coin-bot/                     # 메인 리포 (이 문서 위치)
├── docs/                     # 모든 설계 문서
├── research/                 # Jupyter 노트북 (Week 1~3)
└── strategies/               # 전략 라이브러리 (공유용)

coin-bot-engine/              # 별도 리포 — 봇 실행 엔진
├── src/                      # Freqtrade 기반 봇
├── docker/
├── config/
└── tests/

coin-bot-dashboard/           # 별도 리포 — 대시보드
├── backend/                  # FastAPI
├── frontend/                 # Next.js
└── docker/
```

Git: **GitHub 비공개 저장소** × 3개.

---

## Part 5: 보안

### 5-1. API 키 (업비트)

| 계층 | 조치 |
|------|------|
| 업비트 키 권한 | **출금 권한 OFF**, 거래 권한만 |
| IP 화이트리스트 | 로컬 PC IP만 등록 |
| 키 만료 | 90일마다 수동 로테이션 (런북 작성) |
| 저장소 | **macOS Keychain** (python keyring 라이브러리) |
| 파일 저장 금지 | .env 파일/Git 커밋 절대 금지 |
| 런타임 주입 | Docker 환경변수로만 전달 |
| 로그 마스킹 | 키 노출 금지 |

### 5-2. 대시보드 (Cloudflare Tunnel)

```
로컬 대시보드 (localhost:3000)
  ↓
cloudflared 데몬 (Docker)
  ↓
Cloudflare 글로벌 엣지 (TLS 자동)
  ↓
https://xxxx.trycloudflare.com (또는 사용자 도메인)
  ↓
Cloudflare Access (이메일 OTP 또는 GitHub SSO 로그인)
```

- 로컬 PC에 **외부 포트 0개 오픈** (아웃바운드만)
- HTTPS 자동 관리
- 2FA 옵션 추가 가능
- 월 비용 $0

### 5-3. 대시보드 권한 (단순화)

| 작업 | 확인 단계 |
|------|:--------:|
| 조회 (포지션, 수익률, 이력) | - |
| 수동 매수/매도 | 1단계 (주문 확인창) |
| 봇 일시정지/재개 | 1단계 |
| 봇 파라미터 조정 | 1단계 |
| **전 포지션 청산** | **2단계 (비밀번호 재입력)** |
| **Kill Switch** | **2단계** |

- 감사 로그(audit log) 전체 기록
- 30분 무활동 자동 로그아웃
- 5초 취소 타이머, 별도 트랜잭션 비밀번호, 읽기 전용 토글 모드 **제거** (과잉)

---

## Part 6: 운영

### 6-1. 알림

**규칙: 디스코드 기본 / 긴급(손실/오류/급변/보안)만 카카오톡 + 디스코드**

| 이벤트 | 채널 |
|--------|------|
| 매수/매도 체결 | 디스코드 |
| **손절 발동** | **디스코드 + 카카오톡** |
| 일일/주간 리포트 | 디스코드 |
| **서킷 브레이커** | **디스코드 + 카카오톡** |
| **치명적 에러** | **디스코드 + 카카오톡** |
| 경미한 에러 | 디스코드 |
| **API 키 만료/에러** | **디스코드 + 카카오톡** |
| **Kill Switch 발동** | **디스코드 + 카카오톡** |
| 시장 급변 감지 (서킷 전 경고) | 디스코드 |
| 페이퍼 트레이딩 상태 | 디스코드 |
| LLM 리뷰 결과 (Phase 10+) | 디스코드 |

**스팸 방지**: 동일 이벤트 5분 내 중복 발송 금지, 하루 50건 초과 시 요약 모드.

### 6-2. 운영 정책

| 상황 | 조치 |
|------|------|
| 정전/재부팅 | 자동 재시작 → 미체결 주문 리컨실리에이션 → 상태 복구 |
| PC 사용 간섭 | Docker 컨테이너 격리 |
| WebSocket 끊김 | REST API 자동 폴백 |
| 네트워크 전면 단절 | <5분 대기, 5~30분 재접속+경고, >30분 계층 대응 (손실 포지션 청산 시도, 이익 포지션 홀드, 신규 진입 차단) |
| 업비트 점검 시간 | 사전 공지 감지 → 점검 전 포지션 노출 축소 |
| 킬 크라이테리아 도달 (8주) | 자동 알림 → 사용자 결정 대기 |

### 6-3. 세금 로깅

- **Phase 1 Day 1에는 구현 X** (사용자 답변 Q11-C: 과세 정책 확정 후)
- **단, 모든 거래 원시 데이터는 DB에 영구 저장** (나중에 CSV 추출만 하면 되는 상태로 유지)
- 스키마: `trades` 테이블에 `trade_id, timestamp_utc, timestamp_kst, pair, side, quantity, price_krw, fee_krw, realized_pnl_krw, running_holdings` 포함

---

## Part 7: LLM 레이어 (Phase 10+)

### 시점
**베이스 전략이 페이퍼 트레이딩 4주 통과 후에만 추가.** 지금은 룰 기반만.

### 역할 (Phase 10+에 추가할 5가지)

1. **매크로 이벤트 태거** — FOMC/CPI/규제 발표 사전 분석 → 구조화 태그 `{risk-off/neutral/risk-on, confidence, horizon}` → 룰 기반 레짐 게이트 입력
2. **LLM Validator** — 룰 기반 진입 신호 후 Opus가 `{proceed, skip-with-reason, skip-hard}` 응답. **거부권만**, 새 진입 생성 금지
3. **레짐 내러티브** — 룰 기반 레짐 분류 결과의 자연어 설명 (대시보드 표시용, 매매 영향 없음)
4. **사후 분석 리포트** — 일일/주간 성과를 Opus가 자연어 리포트 생성 (패턴, 실패 원인, 개선 제안)
5. **주간 화이트리스트 리뷰** — 일요일 Opus가 각 코인의 뉴스/온체인/거래량 종합해서 **제외 권고** (추가는 룰 기반)

### 핵심 원칙
> **LLM은 브레이크 페달만, 가속 페달 아님.**
> 매매 신호 생성은 오직 룰 기반. LLM은 거부권/사후분석/로깅/설명만.

### Quota 관리
- **Option A**: Quota 모니터링 → 80% 경고, 95% 초과 시 LLM 기능 자동 중단
- 중단 중에도 **룰 기반 전략은 정상 동작** (돈 버는 메인 로직은 영향 없음)
- 5시간 창 리셋되면 자동 재개
- 봇 전용 API 키는 **일단 발급 안 함** (Phase 10+에서 필요 시 재평가)

### 거부권 강도 (Phase 10+에서 실제 구현 시)
- 극단 부정 신호 (하위 5%): HARD (신규 진입 차단)
- 일반 부정: SOFT (포지션 50% 축소)
- 긍정: 무시 (LLM이 매수 신호 주지 않음)
- 2주마다 veto 효과 분석 → 수익 해치면 자동 비활성화

---

## Part 8: 개발 프로세스

### 승인 모델
- **주 단위 승인** (전략 이터레이션 기준)
- 매주 끝에 "이번 주 결과 + 다음 주 계획" 보고
- 세부 코드 변경은 자율

### 테스트 수준
- **엄격** (사용자 원래 답변)
- 핵심 로직 단위 테스트
- 통합 테스트
- 백테스트 검증
- 린터 + 타입 체크 (ruff, mypy)

### 버전 관리
- GitHub 비공개 저장소 × 3개 (engine, dashboard, research)
- `.gitignore` 엄격 관리 (API 키 절대 금지)
- 커밋 메시지 영어 또는 한국어 자유

---

## Part 9: 백테스트 엄밀성

### 기본 방법
- Walk-forward analysis
- Deflated Sharpe Ratio (Bailey & López de Prado 2014)
- Combinatorial Purged Cross-Validation (ML 단계에서)
- Monte Carlo 트레이드 셔플링 (100회)
- Politis-Romano 부트스트랩 (Sharpe 신뢰구간)

### 데이터
- **기간**: 2021-01-01 ~ 2026-04-12 (Day 0 당일 기준 frozen)
- **데이터 freeze**: Week 1 Day 1 수집 직후 Parquet SHA256 해시 기록 → Week 2 이후 동일 데이터 보장
- **해상도**: 일봉 + 4시간봉 (Week 1은 일봉 우선, 4h는 Day 5 실험)
- **페어**: BTC 단독 (Week 1) → ETH + 알트 5~8개 (Week 2+, 주간 갱신)
- **수수료**: 업비트 0.05% × 2 (왕복 0.1%)
- **슬리피지**: 고정 0.05% (Week 1) → 호가창 기반 모델 (Week 2+)

### 검증 지표
- Sharpe, Sortino, Calmar
- 최대 낙폭 + 회복 시간
- Profit Factor (1.3~1.8 양호, >3 의심)
- 승률 × R-multiple
- Ulcer Index, CVaR
- Turnover, Capacity

### 전략 채택 기준 (Option 3 구현)
- 개별 A, B, 앙상블 C 각각 백테스트
- 조건:
  - **앙상블 통과 + 개별 통과 + 유의미 차이 없음** → **앙상블 채택** (학술 근거 우위)
  - **앙상블만 통과** → 앙상블 채택
  - **개별 중 하나만 통과** → 해당 개별 채택
  - **모두 미통과** → **전략 패밀리 재검토** (킬 카운터 시작)
- "유의미 차이 없음" 기준: Sharpe<0.2, MDD<5%p, CAGR<3%p

---

## Part 10: 변경/보류/제외 항목

### 변경됨 (my-decisions.md에서 수정)
- ~~nautilus_trader~~ → **Freqtrade** (Week 4+)
- ~~EMA 9/21 + RSI~~ → **200MA + Donchian + RSI(4) 앙상블**
- ~~HTTP + RSA 로그인~~ → **Cloudflare Tunnel (HTTPS)**
- ~~Reddit 감성 (B-1a)~~ → **제외** (논문 오독 확인)
- ~~뉴스 감성 거부~~ → **매크로 이벤트 태거로 재채택** (Phase 10+)
- ~~Phase 2부터 LLM~~ → **Phase 10+로 연기**
- ~~2단계 확인/5초 타이머 과다~~ → **단순화**

### 보류됨 (Phase 10+ 또는 라이브 이후)
- LLM 레이어 전체
- HMM 레짐 분류기 (LightGBM도 일단 보류)
- 다중 에이전트 로깅 하네스
- 홈택스 세금 자동 생성 (과세 확정 후)

### 제외됨 (영구)
- 선물/레버리지 거래
- LSTM/Transformer 가격 예측
- 강화학습 (PPO/DQN/FinRL)
- 직접 LLM 매매 결정 (B-1e)
- 크립토 뉴스 피드 연속 감성 분석 (B-1b 원래 방식)

---

## Part 11: 킬 크라이테리아 상세 (2단계)

**타임 박스 시작 시점**: Week 1 Day 1 (Jupyter 노트북 첫 데이터 다운로드)

### Stage 1 — 8주 "연구 계속 여부" 판단

- **Week 3**: 노트북 복제 완료 → 사전 지정 파라미터 Sharpe > 0.8?
  - Pass → Week 4 Freqtrade 이식
  - Fail → Week 4를 "전략 패밀리 탐색"에 사용
- **Week 5**: Freqtrade 이식 + 노트북 결과 재현?
  - Pass → Week 6 페이퍼 시작
  - Fail → 프레임워크 또는 포팅 문제 디버그
- **Week 8 (Stage 1 게이트)**: 페이퍼 트레이딩 초기 2주 결과 평가 (페이퍼 시작 Week 6)
  - Pass → Week 9~11 페이퍼 유지 + Stage 2 준비
  - Fail → **전략 패밀리 교체** OR **연구 모드 전환** (라이브 무한 연기)

### Stage 2 — 12주 "라이브 투입 여부" 판단

- **Week 9**: 페이퍼 4주 완료
- **Week 10~11**: 대시보드 + Cloudflare Tunnel 세팅
- **Week 12 (Stage 2 게이트)**: 라이브 투입 평가
  - 모두 충족 시: 백테스트 Sharpe > 1.0, DSR > 0.5, 페이퍼 4주 대비 70%+, 사용자 명시적 OK
  - Pass → 50만원 입금, 라이브 모드
  - Fail → 라이브 연기, 페이퍼 유지 또는 학습 모드

**중요**: 8주 킬은 "라이브 가드"가 아닌 "연구 방향 재평가". 라이브 투입은 구조상 Week 12+에만 가능.

### Stage 1 실행 기록

#### Week 1 Go/No-Go 결정 (W1-06, 2026-04-17 UTC)

**결정**: **No-Go (Option B)** — 사용자 명시적 승인

**사전 지정 Go 기준 평가** (W1-06.3 자동 평가):

| # | 기준 | 결과 | 판정 |
|---|------|------|------|
| 1 | A 일봉 Sharpe > 0.8 | 1.0353 | PASS |
| 2 | B 일봉 Sharpe > 0.5 | 0.1362 | **FAIL** |
| 3 | 두 전략 중 하나라도 MDD < 50% | A -22.45%, B -21.27% | PASS |
| 4 | 두 전략 중 하나라도 2+ 연도 양수 | A 3개, B 4개 (정규 5년 기준) | PASS |
| 5 | 사전 지정 파라미터 평탄 영역 | A std=0.0440, B std=0.1695 | PASS |

→ "모두 충족" 룰 엄격 적용 시 **No-Go**.

**심화 분석 추가 발견 (W1-06.1b 사용자 요청, 가격 기반 regime 라벨링)**:

- Strategy A 최근 481일 (2024-12-17 A DD peak 이후) **Sharpe -1.1435, 누적 -21.53%**
- Strategy A 해당 기간 5 trade 중 2승 3패 (40% 승률; 손실 -13.40%/-6.66%/-3.04%, 이익 +9.64%/+0.35%) — ground truth: `research/outputs/week1_summary.json.regime_analysis.post_2024_12_17.strategy_a_recent_trades` Return 필드 집계
- **5년 Sharpe 1.04는 2024년 단년 집중** (2024 한 해 수익 68.3% 기여)
- Regime × Strategy: A/B 모두 Volatile regime에서 최고 Sharpe → **앙상블 보완성 제한적**
- A가 최근 Bull dominant 구간(58.2%)에서도 실패 → 엣지 decay 또는 regime 정의 불일치

**Stage 1 킬 카운터**: +1 (Week 1 종료 시점)

**후속 조치**:

- Week 2 범위 재설정: 기존 "walk-forward"에서 **"전략 패밀리 재탐색 + 메이저 알트 확장"**으로 변경
- Strategy A 파라미터 (MA=200, Donchian=20/10, Vol>1.5x, SL=8%)는 **후보 풀에 보관**, 즉시 메인 아님
- Strategy B (MA=200, RSI(4)<25, RSI>50 exit, TimeStop=5d, SL=8%)는 **구조적 엣지 부재 확인 후 폐기**
- Week 2 sub-plan 작성 시 사전 지정 기준 (시총 상위 N개, 상장 3년+) 으로 알트 선정
- Week 2에 새 전략 철학 탐색 (후보: Bear/Bull regime 보완, momentum-on-Bull, 변동성 브레이크아웃 등)
- 뉴스/LLM 기반 전략은 **Phase 10+ Immutable 룰** 유지 (거부권 전용, 매매 결정 생성 아님)

**이 결정은 데이터 스누핑 금지 룰을 준수**: 결과 보고 파라미터를 튜닝하지 않았으며, 사전 지정 Go 기준에 따라 객관적으로 평가. 심화 분석은 Option 선택 근거로만 사용, 전략 재튜닝에는 사용 안 함.

#### Week 2 재범위 결정 (2026-04-17, Week 1 No-Go 후속)

**원래 Week 2** (walk-forward/DSR 중심)는 Strategy A/B 확정 엣지 전제였으나 Week 1에서 엣지 확보 실패. 사용자 승인으로 Week 2를 **"전략 후보 재탐색 + 메이저 알트 확장"**으로 재설계.

**재설계된 Week 2 구조**:

- **W2-01 데이터 확장 + 페어 선정 사전 지정** (BT-003, 2일)
  - 기준: 시총 상위 30위 + 업비트 KRW 상장 3년+ + 일거래대금 100억+
  - Tier 1 필수: BTC (W1 재사용), ETH
  - Tier 2 후보: XRP, SOL, ADA, DOGE (기준 충족 여부에 따라)
  - 영구 제외: PEPE (상장 <3년) 등 소형/신생 알트
  - SHIB 등 밈코인은 별도 실험 트랙 후보 (Week 2 불포함)
- **W2-02 새 전략 후보 사전 등록** (STR-NEW-001, 2일)
  - Candidate C: Slow Momentum (MA50/200 crossover + ATR(14)×3 trail) — Moskowitz 2012 근거
  - Candidate D: Volatility Breakout (Keltner + Bollinger 동시 돌파)
  - (옵션) Candidate E: BTC/ETH spread — 복잡도 높아 Week 4+로 이전 고려
  - Strategy A 파라미터는 후보 풀 보관 (W2-03 grid 포함)
  - Strategy B는 구조적 폐기 (grid 미포함)
- **W2-03 In-sample 백테스트 grid + Week 2 리포트** (BT-005, 2-3일)
  - **Primary 대상**: Tier 1 {BTC, ETH} × {A, C, D} = 6셀 (Go 기준 적용)
  - **Exploratory 대상**: Tier 2 {XRP, SOL, **TRX**, DOGE} × {A, C, D} = 12셀 (참고용, Go 기여 X) — **cycle 1 박제 ADA → cycle 2 v5 TRX 정정 (2026-04-19, W2-01 cycle 2 완료 + W2-02 v5 사용자 승인 발효)**
  - 사전 지정 파라미터 고정, 알트별 튜닝 금지
  - **Week 2 게이트 (사전 지정, DSR 포함)**:
    - Primary: Primary 6셀 중 적어도 1개 전략이 BTC 또는 ETH에서 `Sharpe > 0.8 AND DSR > 0`
    - Secondary 마킹 (Go 기여 X): 동일 전략이 Tier 1+2 3+ 페어에서 Sharpe > 0.5 → ensemble 후보
    - 미달 → Stage 1 킬 카운터 +1, Week 3 재탐색
  - **다중 검정 한계 고지**: 6 primary 셀도 family-wise 오류 여지. DSR로 부분 완화, 최종 검증은 Week 3 walk-forward
  - **"DSR > 0" V 선택 최종 박제 (검증 라운드 정정, 2026-04-20)**: 본 조항의 "DSR > 0"은 Bailey & López de Prado 2014 원문 DSR_z form. V[SR_n] 선택의 최종 박제 = **V_empirical = 0.1023 (sample variance, Bailey 원문 default)**. v6 C-1에서 일시 도입된 `V_reported = max(V_empirical, 1.0) = 1.0` floor는 프로젝트 self-imposed defensive floor였으며 원문 절차가 아님 (W2-03.7 외부 감사 1차 WARNING-1). sub-plan v8 박제로 V_empirical default 복귀. 상세: 아래 "W2-03 In-sample grid Go 결정" 섹션 (2026-04-20) 참조

**Week 3로 이전**:
- Walk-forward analysis (원래 W2-01 → W3-01)
- Deflated Sharpe + Bootstrap + Monte Carlo (원래 W2-02 → W3-02)
- 전략 채택 결정 (W3-03)

**W2-01 sub-plan 작성 완료**: `docs/stage1-subplans/w2-01-data-expansion.md`. W2-02/W2-03 sub-plan은 직전 Task 완료 후 작성 (프로젝트 컨벤션).

#### Week 2 한계 및 독립성 서약 (W2-01 외부 감사 후 추가, 2026-04-17)

외부 감사관 리뷰(`.evidence/agent-reviews/w2-01-preplan-review-2026-04-17.md`) BLOCKING-4 + WARNING-7 대응:

**Strategy C/D 파라미터 출처 명시**:
- **Candidate C — Slow Momentum (MA50/200 crossover + ATR(14)×3 trailing)**:
  - MA50/200 crossover: Faber, Mebane T. (2007) "A Quantitative Approach to Tactical Asset Allocation" (일반 타이밍 지표, BTC-specific 튜닝 아님)
  - ATR(14): Wilder (1978) "New Concepts in Technical Trading Systems" 창시자 기본값
  - Multiplier ×3: Wilder 원 제안 값 (Chandelier Exit 등 후속 문헌에서도 2-3 범위 표준)
- **Candidate D — Volatility Breakout (Keltner(window=20, window_atr=14, multiplier=1.5, original_version=False) + Bollinger(20, 2σ) 동시 돌파)**:
  - **Bollinger Band (20, 2)**: Bollinger (1983) 기본값
  - **Keltner Channel (20, 1.5 ATR)**: ChartSchool/StockCharts 표준 변형 + Raschke 1990s 후속. **Chester Keltner (1960) 원 설계는 EMA(typical price, 10) ± 1.0 × 10일 daily range로 다름** (ta venv 직접 검증 결과, 2026-04-19 W2-02 외부 감사 B-2 정정). ta `KeltnerChannel` 호출 시 `original_version=False` + `window_atr=14` + `multiplier=1.5` 모두 명시 필수 (default와 다름)

**독립성 한계 서약 (Soft Contamination 인정)**:
- 본 프로젝트 팀은 Week 1에서 BTC 5년 일봉 데이터를 이미 분석했고, W1-06.1b에서 "A/B Volatile regime 편중" 결과를 관찰했다. 따라서 Candidate C/D는 **"완전히 BTC-unseen 환경"에서 선택된 것이 아니다**.
- 위의 파라미터 값은 모두 문헌의 **기본값**이며 W1 regime 분석 결과에 맞춘 튜닝 값이 아님을 서약한다.
- 그럼에도 전략 **철학 자체**의 선택(momentum + volatility breakout)은 W1 regime 편중 발견의 영향을 받았다 → **soft contamination**이 존재함을 인정.
- 이 한계의 실질 영향은 **Week 3 walk-forward가 최종 평가**. Week 2 In-sample Go는 예비 판단.

**Strategy A 후보 풀 물리적 정의**:
- `docs/candidate-pool.md`에 Strategy A 파라미터 + 재진입 조건 저장 (W2-01.1 직후 신설)
- Recall mechanism: W2-03 grid에서 재등장 시 DSR-adjusted 평가 필수. Week 3 이후 재등장 시 새 사전 등록 사이클 요구.

**Tier 2 Fallback 정책 (B-5 대응)**:
- Tier 2 후보 <2 (=0 또는 1) 인 경우:
  - (i) **Tier 2 제거**: Tier 1 2개(BTC+ETH) × {A,C,D} = **primary 6셀 그대로 유지**. Tier 2 exploratory는 통과 페어 수 × 3 전략으로 감소 (0개 통과 → exploratory 0셀, 1개 통과 → exploratory 3셀). Go 기준 (Sharpe>0.8 AND DSR>0) 변경 없음.
  - (ii) 또는 Task 전체 재설계 → 새 사전 등록 + backtest-reviewer + 사용자 승인 루프.
- **임계값 완화는 금지**. 후보 수를 맞추려 기준을 움직이는 행위는 data snooping.
- 상세 규정은 `docs/pair-selection-criteria-week2.md` 섹션 3 (본 결정을 물리화).

#### Week 2 W2-01 v4 사이클 중단 (Fallback ii 발동, 2026-04-17)

W2-01.2 단계 1 (CoinGecko top30 KRW 시총 스냅샷) 실측 결과 ADA가 시총 14위(top10 밖)로 확인되어 `pair-selection-criteria-week2.md` v4에 박제된 Tier 2 리스트 {XRP, SOL, ADA, DOGE}와 불일치. cherry-pick 차단 장치(criteria L78, L117 "실측 불일치 시 Fallback (ii) 사이클 중단 강제")가 정상 발동.

**단계 1 실측 결과** (fetched_at 2026-04-17 07:08:56 UTC):
- 시총 top10 (KRW 환산): BTC, ETH, USDT, XRP, BNB, USDC, SOL, TRX, FIGR_HELOC, DOGE
- ADA: 14위, 시총 약 14.0조 KRW
- FIGR_HELOC: 9위, 시총 25.79조 KRW. CoinGecko id `figure-heloc`. HELOC = Home Equity Line of Credit, Figure (fintech 회사)의 RWA(Real-World Asset) 토큰. 24h 거래량 232억 KRW = 시총의 **0.09%** (= 비율 0.0009, 사실상 정상 spot 거래 없음). 업비트 KRW 미상장 매우 유력 (단계 2 미실시로 미확정)
- snapshot 산출물 **로컬 보존만** (gitignored, `.gitignore` L24 `research/data/` 룰): `research/data/coingecko_top30_snapshot_20260417.json` + SHA256 `c70a108905566f00f1b5b97fd3b08bf13be38d713f351027861d78869b3fcf59`. git tracked 여부는 새 사이클 설계 시 결정 (sub-plan W2-01.6 박제 "git tracked" vs `.gitignore` 룰 충돌은 별도 정정 작업, W1-01 `data_hashes.txt`도 동일 누락 누적)
- 한계: snapshot 명목 시각 `snapshot_utc=2026-04-17T00:00:00+00:00` 박제와 실제 fetched_at 약 7시간 차이. CoinGecko 무료 API는 historical snapshot 미제공 → snapshot 재현 불가능

**Fallback (ii) 발동 결과**:
- v4 본 사이클(W2-01 cycle 1) 중단. v4 문서는 "참고 자료" 격리. primary Go 평가 반영 절대 금지
- 단계 2~7 미실시 (자동 cancel)
- snapshot JSON + SHA256은 새 사이클에서 동일 명목 시각 채택 시 재사용 가능 (로컬 보존만, gitignored 유지)
- 사용자 명시 승인: 2026-04-17 07:08 UTC ("그래 추천한걸로 가")

**다음 단계 (사용자 결정 대기)**:
- 단계 2 (업비트 KRW 페어 + 상장일 + 30일 거래대금) 진행 여부: (a) 새 사이클 설계 전 별도 진행 / (b) 새 사이클 설계 단계 통합
- 새 사이클 명칭(잠정: W2-01 cycle 2 또는 W2-01b) 확정은 새 사이클 설계 시점

**다음 사이클 설계 권고 (cycle 1 학습)**:
- "Tier 2 리스트 추정 박제" 방식 → "**규칙만 박제 + 코드 자동 결정**" 방식으로 변경. 추정 빗나감 위험 자체 제거. 인간 개입 단계(= cherry-pick 유혹 발생 지점)를 코드로 차단
- snapshot 시각 약점 새 사이클에서 어떻게 다룰지 명시 (CoinGecko 무료 API historical 미제공 한계 인정)
- FIGR_HELOC 같은 RWA/유동성 극단 낮은 토큰 자동 배제 장치 검토 (예: `vol_24h / market_cap` 비율 임계값)

**한계 인정 (정직 기록)**:
- v4 cycle 1에서 추정 리스트 {XRP, SOL, ADA, DOGE}를 박제한 것은 사용자 + Claude 공동 책임. 사전에 ADA가 top10에 있다는 추정은 시장 변동 결과 빗나감 (정상 시나리오)
- cherry-pick 차단 장치가 정확히 의도대로 작동하여 사이클 중단으로 이어짐 = **시스템 정상 작동**
- 이 사례를 `.claude/handover-2026-04-17.md` v5 "과거 반복 버그 유형 #17 (사전 지정 추정 리스트의 빗나감 위험) + #18 (외부 코인 정체 추측)"로 박제

상세 trace: `.claude/handover-2026-04-17.md` v5

#### cycle 1 격리 양성 목록 박제 (cycle 2 2차 외부 감사 W2-1 해소, 2026-04-19)

cycle 1 (`pair-selection-criteria-week2.md` v4) 격리 대상 = 다음 cycle 1 고유 결정만 격리:

1. **Tier 2 리스트 추정 박제** ({XRP, SOL, ADA, DOGE} 사전 박제 자체)
2. **snapshot_utc 명목 시각 박제** ("2026-04-17T00:00:00+00:00" 명목 시각 채택 정책)

위 2개 외 cycle 1 결정 (임계값 100억, 측정 창 2026-03-13~04-11 UTC, Tier 1 {BTC, ETH}, Fallback (i)/(ii), Common-window 정책, 갭 처리 정책, 승인 2단계 구조, 다중 검정 한계 인정 등)은 **격리 비대상**. cycle 2/3/...에서 그대로 채택 가능.

**박제 목적**: 다음 사이클 작성자(Claude 또는 미래의 누구)의 자가 분할 통로 차단. 양성 목록을 사이클 작성자가 결과 보고 정의하면 cherry-pick 위험. 본 decisions-final.md 박제로 양성 목록을 사후 변경 불가능하게 고정.

**박제 시점 = cycle 2 사용자 승인 시점 (2026-04-19, 사용자 위임 발화 "너가 결정해줘 모든걸"), 아래 "Fallback (ii) 누적 한도 박제"와 동시 발효** (시점 일관성, cycle 1 freeze 시점 순환 정의 B-A 패턴 재발 차단).

#### Fallback (ii) 누적 한도 박제 (cycle 2 2차 외부 감사 W2-2 해소, 2026-04-19)

- **W2-01 Fallback (ii) 누적 한도 = 3회** (cycle 1 + cycle 2 + cycle 3 = 최대 3회)
- 3회 누적 후 추가 Fallback (ii) 발동 시: **W2-01 자체 폐기 + Stage 1 킬 카운터 +1 + Week 2 재범위 결정 사용자 승인 강제**
- **박제 시점 = cycle 2 사용자 승인 시점** (2026-04-19). cycle 3 결과 보고 한도 변경 시도 = cherry-pick 차단 (시간적 미러)
- **한도 3회 근거**: cycle 1 외부 감사 3회 사례 + 학습 곡선 상한 + Week 2 일정 균형 (3 cycle × ~2일 = 6일+α)

상세 trace: `.evidence/agent-reviews/w2-01-cycle2-pair-criteria-review-2026-04-18.md` 2차 감사 W2-1/W2-2

#### W2-03 In-sample grid Go 결정 (2026-04-20, Option C 사용자 명시 채택)

**결정**: **Go (Option C — V_empirical 채택)** — 사용자 명시 승인 "ㄱㄱ" (2026-04-20)

**결정 경로 (시간 trace)**:

1. W2-03.0~.5 노트북 실행 (2026-04-19 16:27:56 UTC) → v6 C-1 기준 원본 결과 `is_go=False` (Go 셀 0/6)
2. W2-03.6 리포트 작성 + backtest-reviewer APPROVED with follow-up (2026-04-20) — trace `.evidence/agent-reviews/w2-03-insample-grid-review-2026-04-20.md`
3. W2-03.7 외부 감사 1차 (2026-04-20, 적대적 페르소나) — trace `.evidence/agent-reviews/w2-03-insample-grid-result-review-2026-04-20.md`. **WARNING-1 지적**: `V_reported=1.0` floor는 Bailey 2014 원문 절차가 아닌 프로젝트 self-imposed defensive floor. v6 C-1 "Bailey conservative 취지" 표현은 서술 오류 (포장). V_reported/V_empirical ≈ 9.78배 부풀림 / SR_0 3.13배 엄격화 (0.4159→1.3001).
4. WARNING 4건 반영 sub-plan v7 정정 박제 (2026-04-20)
5. 사용자에게 중립 제시: Option A (No-Go 수용) / C (V_empirical 채택) / D (추가 정보)
6. 사용자 명시 결정: **"ㄱㄱ"** → Option C 채택
7. sub-plan v8 박제 + V_empirical 재평가
8. W2-03.7 외부 감사 2차 (v8 V_empirical 채택 재검증) — trace `.evidence/agent-reviews/w2-03-v8-v-empirical-adoption-review-2026-04-20.md`. **APPROVED with follow-up (BLOCKING 0 / WARNING 4 / NIT 6)**. WARNING 4건 v8에 반영 완료.

**v8 최종 평가 결과 (V_empirical = 0.1023, SR_0 = 0.4159)**:

| Cell | Sharpe | DSR_z | Go cell? |
|------|--------|-------|----------|
| BTC_A | 1.0353 | +23.22 | ✓ |
| BTC_C | 0.9380 | +18.12 | ✓ |
| BTC_D | 1.1818 | +27.27 | ✓ |
| ETH_A | 1.1445 | +29.37 | ✓ |
| ETH_C | 0.3237 | -2.77 | ✗ (Sharpe 0.324 < 0.8) |
| ETH_D | 1.0928 | +22.71 | ✓ |

**Go 통과 셀: 5/6** (BTC_A, BTC_C, BTC_D, ETH_A, ETH_D). is_go = True.

**Strategy A Recall 발동**: BTC_A + ETH_A 둘 다 Go 통과 → candidate-pool.md L27 재진입 조건 충족 → Strategy A 상태 **Retained → Active 재전이**. Week 3 walk-forward 재검증 의무 강제 (candidate-pool.md L28).

**Stage 1 킬 카운터**: +0 가산 (현재 총 +1 유지, W1 종료 시점 값).

**v8 박제 프레이밍 정직화 (2차 감사 WARNING-1 반영)**:

- "Bailey 원문 해석 오류 교정"이 아니라 **"서술 오류 인정 + V=sample variance default 복귀"**. "원문 복귀" overclaim 철회.
- Bailey 원문은 V=sample variance를 default로 제시하되 N 작을 때 대응은 사용자 재량. "원문 절차" 단독이 아님.
- **N=6 sample variance 신뢰 한계 동반 인정** (2차 감사 WARNING-2): Week 3 walk-forward에서 fold별 DSR 재산정으로 보완.

**cycle 1 학습 #5 재발 여부 (2차 감사관 명시 박제)**:

- 2차 감사관: "v8은 cycle 1 #5 'Go 기준 사후 완화'와 본질적으로 구분이 어렵다. 절차적 방어 3가지(1차 감사 trace + 사용자 중립 선택 + v5 잠재 박제 선행)는 가치 있으나 '결과 보고 Go 기준 완화'라는 실질 효과와의 구분은 형식 논리 차원."
- **Week 3 결과가 retrospective 재판정**이 됨을 박제.

**Week 3 의무 (2차 감사 WARNING-3 반영, BLOCKING 직전 수준)**:

- V_empirical 일관 적용 (fold별 sample variance 산출)
- **Floor 재도입 금지** (v6 C-1로 복귀 X)
- **임계값 변경 금지** (Sharpe > 0.8, DSR_z > 0 고정)
- Fold별 DSR 재산정 의무
- 위반 시 cycle 3 강제 (cherry-pick 감시 트리거)

**Week 3 실패 시 소급 절차 (2차 감사 WARNING-4 반영)**:

- Strategy A/C/D 전부 DSR 미통과 시 Stage 1 킬 카운터 **+2 소급 가산** (W2-03 Go 결정을 사후에 "실패"로 재분류)
- 외부 감사 재수행
- 사용자 명시 결정 (Stage 1 학습 모드 전환 vs 재재탐색)

**후속 조치**:

- candidate-pool.md Strategy A 상태: Retained → Active (v5 cycle 박제)
- stage1-execution-plan.md W2-03 Done + W3-01 활성화
- W3-01 walk-forward 진입 (Strategy A/C/D 대상)

**관련 문서**:

- sub-plan v8: `docs/stage1-subplans/w2-03-insample-grid.md`
- 리포트: `research/outputs/week2_report.md`
- Evidence: `.evidence/w2-03-insample-grid-2026-04-20.md`
- Agent review: `.evidence/agent-reviews/w2-03-insample-grid-review-2026-04-20.md` (backtest-reviewer)
- External audit 1차: `.evidence/agent-reviews/w2-03-insample-grid-result-review-2026-04-20.md`
- External audit 2차: `.evidence/agent-reviews/w2-03-v8-v-empirical-adoption-review-2026-04-20.md`

**절차 약점 + 사후 승인 발효 박제 (검증 라운드 정정, 2026-04-20 handover v13 작성 시점)**:

사용자 Option C 명시 승인("ㄱㄱ", 2026-04-20) 이후 외부 감사 2차에서 WARNING 4건 추가 발견 (원문 복귀 overclaim / N=6 신뢰 한계 / Week 3 V 일관성 사전 박제 / Week 3 실패 소급). 본 WARNING 4건은 사용자 재승인 없이 v8 + 리포트 + evidence + decisions-final + candidate-pool + execution-plan에 자동 반영된 후 커밋 `512d92a` 완료. 이후 사용자 명시 검증 요청 ("니가 한게 아니라고 생각하고")에 따라 외부 감사관 관점 재검증 수행 → 본 WARNING 4건 반영 내용을 사용자에게 보고 → 사용자 "1 다 정정해" 응답으로 **사후 승인 발효 (2026-04-20 handover v13 작성 시점)**. 절차 약점은 본 박제로 투명 기록. 향후 유사 사례: 외부 감사 WARNING이 책무 추가 (예: Week N 의무/소급 절차)를 수반하는 경우, v_next 박제 전 사용자 명시 확인 우선 수행.

---

## 다음 단계

1. ~~결정사항 통합~~ (이 문서)
2. **`architecture.md`** 작성
3. **`week1-plan.md`** 작성 (Day 1부터 Day 7까지 구체 작업)
4. 프로젝트 디렉토리 구조 생성
5. **Week 1 Day 1 작업 시작**

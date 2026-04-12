# Day 0 검증 리포트

> Day 0 적용 후 외부 감사관 재검증 결과 + 후속 minor 수정 완료.
> 결과: **READY TO COMMIT**.

## 적용 요약

### 1. API 검증 (web search)

- **vectorbt 0.28.5**: `sl_stop` (fraction), `sl_trail` (boolean), `pf.sharpe_ratio()` 메서드, `cash_sharing=True+group_by=True` 앙상블, freq='1D'/'4h' 모두 검증.
- **vectorbt에 없음**: `ts_stop`, `td_stop`, `max_duration`, `time_stop`, `dt_stop` (vectorbtpro 유료에만).
- **pyupbit 0.2.34**: `get_ohlcv_from(ticker, interval, fromDatetime, to, period)` 시그니처 확인. `to=` 파라미터 존재. naive KST 반환. 에러 시 None.

### 2. decisions-final.md 수정

- Strategy B 일봉 기반 명시 + 1% 리스크 통일
- 일일 손실 -2% 소프트 / -3% 하드 분리
- 서킷 브레이커 L2에서 "일일 -2%" 제거
- Part 11 2단계 킬 (Stage 1 Week 8 / Stage 2 Week 12) 재정의
- 데이터 기간 frozen 명시
- Part 0 표 + Week 12 라이브 라벨 정합화
- 이모지 모두 제거

### 3. architecture.md 수정

- DB 스키마 순서: signals → trades (FK 의존성)
- DB 인덱스 추가 (시계열 조회 최적화)
- regime_states에 pair 컬럼 추가
- Docker secrets 파일 기반으로 변경 (Swarm 모드 아님)
- cloudflared `TUNNEL_TOKEN_FILE` → `env_file:` 방식
- 대시보드 → Freqtrade REST API → strategy-engine 흐름 명시
- dashboard-backend는 Upbit 키 미보유 (least privilege)

### 4. week1-plan.md 전면 재작성

- 검증된 vectorbt 0.28.5 + pyupbit 0.2.34 API 기반
- 5개 코드 버그 모두 수정 (MA200, Donchian, entry_price, bars_held, ensemble)
- 일봉 기준 우선, 4시간봉은 Day 5 참고용
- 앙상블 Week 1 제외 (Week 2로)
- 사전 지정 파라미터 vs 민감도 그리드 분리
- Wilder 스무딩 ATR 사용
- 타임존 localize 명시 + assert
- SHA256 해시 freeze 절차
- git init + requirements.lock 절차

### 5. CLAUDE.md 시스템 재작성 (3개 파일)

- **root** (124줄): SSoT 동기화, 외부 감사 룰 Immutable로 격상, Operational Commands를 현재 상태로 축소, AGENTS_md_Master_Prompt.md Context Map 추가
- **docs/CLAUDE.md** (131줄): Master Prompt 필수 섹션 추가 (Tech Stack & Constraints, Implementation Patterns, Testing Strategy)
- **research/CLAUDE.md** (163줄): 검증된 API 패턴, 사용 금지 패턴, Wilder/사전 지정 파라미터 룰

### 6. glossary.md 보강

- Section 9 추가: Wilder Smoothing, Padysak/Vojtko, Walk-Forward, CPCV, Politis-Romano, Almgren-Chriss, Donchian (보강), Pre-registered Parameters, Replication Sprint, Data Snooping (보강), vectorbt 0.28.5 검증된 파라미터, pyupbit 0.2.34 검증된 함수
- 모든 이모지 제거

## 검증 결과

### 이전 발견 21개 처리

| 항목 | 결과 |
|------|------|
| Stage 1/2 SSoT 동기화 | FIXED |
| 일일 손실 -2% vs -3% | FIXED (소프트/하드 분리) |
| Strategy A 1% vs B 2% | FIXED (둘 다 1%) |
| 킬 타임라인 불가능 | FIXED (2단계 재정의) |
| DB FK 순서 | FIXED |
| Docker secrets external:true | FIXED (file 기반) |
| cloudflared TUNNEL_TOKEN_FILE | FIXED (env_file) |
| 대시보드 → 업비트 보안 구멍 | FIXED (Freqtrade REST 경유) |
| vectorbt td_stop | FIXED (entries.shift) |
| vectorbt ts_stop | FIXED (sl_stop + sl_trail) |
| pyupbit to= | VERIFIED 존재 |
| MA200 = 30일 | FIXED (window=200 또는 1200) |
| entry_price NameError | FIXED (sl_stop 파라미터) |
| bars_held NameError | FIXED (entries.shift) |
| 앙상블 자본 이중계산 | FIXED (Week 1 제외, Week 2에서 cash_sharing) |
| Glossary 누락 용어 | FIXED (Section 9 추가) |
| Operational commands 실행 불가 | FIXED (현재 상태로 축소) |
| docs/CLAUDE.md 필수 섹션 | FIXED (3개 추가) |
| 외부 감사 룰 격하 | FIXED (Immutable로 격상) |
| 이모지 active docs | FIXED (decisions-final, glossary 청소) |
| AGENTS_md_Master_Prompt Context Map | FIXED |

### 후속 minor 수정 (NEW issues)

| 항목 | 처리 |
|------|------|
| glossary.md L80 ❌ 이모지 | FIXED |
| decisions-final.md L21 Part 0 표 stale | FIXED (2단계 표시) |
| decisions-final.md L155 "Week 10+" 라벨 | FIXED (Week 12+) |
| week1-plan.md TS_TRAIL_PCT dead 상수 | FIXED (제거) |
| week1-plan.md git add 누락 | FIXED (CLAUDE.md, AGENTS 추가) |
| week1-plan.md entries.shift 근사 주의 | FIXED (주석 추가) |

## 라인 수 검증

- root CLAUDE.md: 124 줄 (200 미만)
- docs/CLAUDE.md: 131 줄 (200 미만)
- research/CLAUDE.md: 163 줄 (200 미만)

## 잔여 비차단 항목

- AGENTS_md_Master_Prompt.md L1 `@#` stray character (편집 금지 정책)
- Historical 문서들의 이모지 (frozen, 편집 금지)

## 결론

**READY TO COMMIT**. 모든 차단 항목 해결, 검증된 API 사용, SSoT 일관성 확보.

### 다음 단계

1. Task #2 완료 표시
2. 사용자에게 검증 리포트 보고
3. Week 1 Day 1 시작 대기 ("Day 1 시작" 명령)

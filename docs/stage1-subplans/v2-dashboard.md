# V2-Dashboard sub-plan (Phase 1, V2-06 병행)

Task ID: V2-Dashboard (V2-06과 병행 트랙, 별도 task ID)
Feature: STAGE1-V2-012
Created: 2026-04-26
Status: **승인됨** (2026-04-26 사용자 명시) → V2-D-01 착수

**결정 박제 (2026-04-26)**:
1. Frontend: **Next.js 14+** (사용자 학습 의지 명시)
2. 외부 노출: **Cloudflare Tunnel** (Immutable 룰 준수, 사용자 일시 "공인 IP 직접" 옵션 정정)
3. 도메인: Cloudflare 무료 서브도메인 (`*.trycloudflare.com`) 또는 Cloudflare 소유 도메인 (V2-D-05 시점 결정)

박제 출처:
- `docs/architecture.md` §4 P7 dashboard 설계 (Week 10~11 → v2 V2-06 병행으로 시점 이동)
- `docs/stage1-v2-relaunch.md` §3 v2 의도된 단순화 (단축 우선, dashboard는 페이퍼 4주 빈 시간 활용)
- `CLAUDE.md` "dashboard-backend는 거래소 API 키에 접근 권한 없음" Immutable

---

## 0. 목적

V2-06 페이퍼 4주 동안 daemon 자동 동작 = 사용자 손 비어있음. 이 시간 활용해 v1 architecture 박제의 dashboard를 **Phase 1 스코프로** 작성. V2-07 10만원 라이브 진입 시점에 모니터링 도구로 즉시 활용.

**범위 분리** (Stage 1 v2 시점):
- ✅ Phase 1: FastAPI backend (read-only) + Next.js frontend + Cloudflare Tunnel + Access 인증
- ❌ Phase 2: engine REST 매매 제어 — V2-07 라이브 안정 후 별도 결정

---

## 1. 진입 조건

- ✅ V2-06 daemon 가동 (페이퍼 trades 누적 시작)
- ⏳ 사용자 Cloudflare 계정 (무료 가능)
- ⏳ 본 sub-plan 명시 승인

---

## 2. 작업 분해 (5~7일 추정)

| ID | 항목 | 추정 | 산출물 |
|----|------|:----:|--------|
| **V2-D-01** | dashboard/ 디렉토리 + venv 분리 | 0.5d | `dashboard/backend/`, `dashboard/frontend/` |
| **V2-D-02** | FastAPI backend (read-only API) | 1.5d | `app/main.py`, `app/routers/{state,trades,logs,summary}.py` |
| **V2-D-03** | Frontend (Next.js MVP 또는 단순 HTML) | 1.5d | 1-page 대시보드: 포지션 카드 + PnL 차트 + 최근 trades 테이블 |
| **V2-D-04** | 로컬 sanity (localhost:8000) | 0.5d | 모든 endpoint 200 응답 + frontend 정상 렌더 |
| **V2-D-05** | Cloudflare Tunnel + Access 가이드 | 1d | `docs/dashboard-cloudflare-guide.md` (사용자 절차) |
| **V2-D-06** | launchd plist (dashboard daemon) | 0.5d | `dashboard/launchd/com.coinbot.dashboard.plist` |
| **V2-D-07** | 통합 검증 + evidence | 0.5d | `.evidence/v2-dashboard-phase1-{date}.md` |

**총**: 6일 (사용자 직접 실행 절차 제외)

---

## 3. 보안 박제 (CLAUDE.md Immutable 준수)

- dashboard-backend는 **Upbit access/secret/discord-webhook Keychain 미접근** — 환경변수/keychain 읽기 0회
- engine state DB는 **read-only**로 열기 (sqlite3 `mode=ro` URI 사용) — 파일 lock 충돌 방지 + 우발 write 차단
- engine logs/* JSONL 읽기 전용
- Cloudflare Tunnel만 외부 노출 — dashboard-backend port (예: 8000)는 **localhost bind only**
- Cloudflare Access 이메일 OTP 인증 — 사용자 본인 외 접근 0
- engine 자체는 Tunnel 노출 X (배제), 대시보드 backend만 noexposed

---

## 4. 기술 스택 박제

| 계층 | 박제 |
|------|------|
| Backend | FastAPI 0.115+ (Python 3.11+, dashboard 별도 venv) |
| Frontend | Next.js 14+ (App Router, TypeScript) **또는** 단순 HTML+Chart.js (사용자 결정) |
| 외부 접속 | Cloudflare Tunnel (cloudflared) + Cloudflare Access (이메일 OTP) |
| State 접근 | sqlite3 `file:...?mode=ro` URI (read-only) |
| 호스트 | Mac mini 24/7, dashboard launchd LaunchAgent |

> Frontend는 사용자 학습 비용 고려해 **단순 HTML + Chart.js** 권장 (Next.js는 학습 부담). 본 sub-plan에서는 단순 HTML 가정. Next.js 선호 시 V2-D-03에서 분기.

---

## 5. API 설계 (V2-D-02)

| Method | Path | 응답 | 비고 |
|--------|------|------|------|
| GET | `/api/health` | `{status, daemon_alive, last_run_kst}` | daemon ping 간접 (state.meta last_run_ts 기준) |
| GET | `/api/positions` | `[{cell_key, entry_price, volume, krw_invested, current_price, unrealized_pnl}]` | open positions |
| GET | `/api/trades?days=N` | `[{ts_kst, side, pair, price, volume, fees, realized_pnl_krw}]` | trades-YYYY.jsonl 최근 N일 |
| GET | `/api/summary?days=N` | `{trade_count, total_realized_krw, cumulative_return_ratio, win_count, loss_count}` | compare 도구의 PaperStats 포맷 |
| GET | `/api/logs?level=ERROR&n=50` | `[{ts, level, event, ...}]` | engine.log JSONL tail |
| GET | `/api/orders/recent?n=20` | `[{order_uuid, side, status, ...}]` | state DB orders 테이블 최근 N |

전체 read-only. POST/PUT/DELETE 없음. 외부 IP에서 매매 제어 0.

---

## 6. 사용자 책무 (V2-Dashboard 신규 ⚠️)

| 책무 | 시점 | 사유 |
|------|------|------|
| **Cloudflare 계정 가입** (무료) | V2-D-05 진입 시 | Tunnel + Access 사용 |
| **도메인 1개 보유 또는 cf 무료 서브도메인 사용** | V2-D-05 | Tunnel 매핑 대상 |
| **Cloudflare Tunnel 등록 (cloudflared 설치 + 토큰 발급)** | V2-D-05 가이드 따라 | Tunnel 활성화 |
| **Cloudflare Access 정책 설정 (이메일 OTP)** | V2-D-05 | 본인 외 접근 차단 |
| **dashboard launchd load** | V2-D-06 후 | Mac mini 24/7 daemon 등록 |

---

## 7. 위험 + 완화

| 위험 | 완화 |
|------|------|
| dashboard-backend 우발적 write로 engine state 오염 | sqlite `mode=ro` URI 강제 + 코드 레벨 read-only 보장 |
| Cloudflare Tunnel 토큰 git 커밋 누출 | `.gitignore` + Keychain 보관, 환경변수 주입 |
| 외부 노출로 인한 brute force | Cloudflare Access 이메일 OTP (Cloudflare가 차단) + dashboard backend 자체 인증은 미구현 (Access 신뢰) |
| engine과 dashboard 동시 실행 시 SQLite lock | engine WAL 모드 + dashboard read-only mode → concurrent read 안전 |
| frontend 매매 제어 기능 향후 요청 | Phase 2 별도 결정. V2-07 라이브 안정 후 평가 |
| Next.js 학습 비용 | 단순 HTML 권장 분기 (사용자 결정) |

---

## 8. 진입 / 종료 기준

### 진입 (착수 조건)
- ✅ V2-06 daemon 가동 중
- ⏳ 사용자 sub-plan 명시 승인
- ⏳ 사용자 Cloudflare 계정 (V2-D-05 시점에 필요)

### 종료 (Phase 1 완료 조건)
- 모든 endpoint 200 응답 + 인증 0 우회
- Cloudflare Tunnel HTTPS 외부 접근 OK (사용자 모바일 등에서 검증)
- dashboard launchd 24/7 daemon 등록
- evidence 6단 박제

---

## 9. 진행 순서

```
V2-D-01 디렉토리/venv  →  V2-D-02 backend  →  V2-D-04 로컬 sanity
                                              │
                                              ↓
                                     V2-D-03 frontend  →  V2-D-04 sanity
                                              │
                                              ↓
                                     V2-D-06 launchd  →  V2-D-05 Cloudflare 가이드
                                              │
                                              ↓
                                     V2-D-07 사용자 Tunnel 등록 + evidence
```

V2-D-05 사용자 절차 전까지는 모든 작업이 localhost. 외부 노출은 마지막 단계.

---

End of V2-Dashboard sub-plan. Generated 2026-04-26.

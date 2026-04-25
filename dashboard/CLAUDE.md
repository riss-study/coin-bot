# dashboard/

## Module Context

V2-Dashboard Phase 1: read-only 모니터링 대시보드. engine state DB + trades JSONL + logs를 시각화. CLAUDE.md Immutable 룰 준수: dashboard-backend는 Upbit/Discord secrets 미접근, engine state DB는 read-only로 열기, 외부 노출은 Cloudflare Tunnel만.

## Tech Stack & Constraints

- Backend: FastAPI 0.115+ (Python 3.11+, dashboard/backend/.venv 분리)
- Frontend: Next.js 14+ (App Router, TypeScript)
- 외부 접속: Cloudflare Tunnel + Access OTP (V2-D-05 시점)
- 호스트: Mac mini 24/7, dashboard launchd LaunchAgent (V2-D-06)
- engine state DB 접근: sqlite3 `file:...?mode=ro` URI 강제 (write 차단)

## Local Golden Rules

### Immutable (Project root CLAUDE.md 상속)

- dashboard-backend는 거래소 API 키에 접근 권한 없음 (least privilege)
- 외부 인터넷 노출은 Cloudflare Tunnel 경유 필수. 로컬 포트 직접 노출 금지
- Cloudflare Tunnel만 dashboard-backend 노출. engine/DB는 노출 0
- API는 read-only. POST/PUT/DELETE 미구현 (Phase 2 별도 결정)

### Do's

- engine state DB는 `mode=ro` URI로 열기 (코드 레벨 read-only 보장)
- 사용자 책무 (Cloudflare 설정 등) 가이드 분리 박제
- 모든 endpoint 응답에 timestamp UTC + KST 동시 포함

### Don'ts

- Upbit access/secret/discord-webhook Keychain 호출 금지
- engine 코드 import 금지 (의존성 분리). 데이터는 DB/JSONL 파일 read만
- 외부 IP 직접 bind 금지. localhost (127.0.0.1) only

## File Layout (V2-D-01 시점)

```
dashboard/
├── backend/
│   ├── .venv/                  # FastAPI 의존성 (gitignored)
│   ├── requirements.txt
│   └── app/
│       ├── main.py             # FastAPI 진입점
│       ├── db/                 # state DB + JSONL reader (read-only)
│       └── routers/            # API endpoint 정의
├── frontend/                   # Next.js (V2-D-03 시점)
├── launchd/                    # com.coinbot.dashboard.plist (V2-D-06)
├── cloudflared/                # Tunnel 토큰 (gitignored)
└── CLAUDE.md                   # 본 파일
```

## Sub-plan

- `docs/stage1-subplans/v2-dashboard.md` — 7단계 작업 분해 (V2-D-01 ~ V2-D-07)

## Active Tasks

- **V2-D-01**: 디렉토리 + venv 분리 (IN PROGRESS)
- V2-D-02 ~ V2-D-07: 대기

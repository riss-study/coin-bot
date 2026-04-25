"""Dashboard backend config — engine 경로 + 보안 박제.

박제 출처:
- docs/stage1-subplans/v2-dashboard.md
- CLAUDE.md "dashboard-backend는 거래소 API 키에 접근 권한 없음"
"""
from __future__ import annotations

from pathlib import Path

# dashboard/backend/app/config.py → coin-bot/
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
ENGINE_ROOT = PROJECT_ROOT / "engine"
ENGINE_DATA = ENGINE_ROOT / "data"
ENGINE_LOGS = ENGINE_ROOT / "logs"
STATE_DB_PATH = ENGINE_DATA / "state.sqlite"

# 호스트 박제 (security): localhost only. 외부 노출은 Cloudflare Tunnel만.
HOST = "127.0.0.1"
PORT = 8001  # engine은 별도 프로세스, 다른 port

# CORS — frontend Next.js dev (localhost:3000) + 동일 호스트
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

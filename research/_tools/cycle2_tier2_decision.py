"""
W2-01 cycle 2 단계 2: Tier 2 결정 규칙 자동 적용

cycle 2 v4 L99-127 (의사 코드 L99-112 + stablecoin_set L114-118 + 새 스테이블 안전판 L123-127) 정확 구현.
- cycle 1 snapshot JSON 재사용 + SHA256 무결성 재검증
- top10 ∩ 업비트 KRW ∩ BTC/ETH 제외 ∩ stablecoin_set 제외
- 인간 개입 금지 (코드 산출 결과 = 최종)
- 새 스테이블 발견 안전판 (사용자 보고 + cycle 3 박제 강제)

사용:
    cd research && source .venv/bin/activate
    python _tools/cycle2_tier2_decision.py

박제 출처:
    - docs/pair-selection-criteria-week2-cycle2.md v4 (Tier 2 결정 규칙 + stablecoin_set)
    - docs/stage1-subplans/w2-01-data-expansion.md (W2-01.2 cycle 2 단계)

NIT2-3: 본 코드는 외부 감사관 검증 (APPROVED) 후에만 실행한다.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pyupbit

# 박제 값 (cycle 2 v4 L40-45)
# W-1 해소: 실행 위치 무관 절대 경로. docstring `cd research`/루트 실행 모두 OK
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_PATH = PROJECT_ROOT / "research" / "data" / "coingecko_top30_snapshot_20260417.json"
EXPECTED_SHA256 = "c70a108905566f00f1b5b97fd3b08bf13be38d713f351027861d78869b3fcf59"

# 박제 값 (cycle 2 v4 Tier 1)
TIER1_SET: frozenset[str] = frozenset({"BTC", "ETH"})

# 박제 값 (cycle 2 v4 L114-118 stablecoin_set, 11개)
STABLECOIN_SET: frozenset[str] = frozenset({
    "USDT", "USDC", "USDS", "DAI", "USDE", "USD1", "PYUSD",
    "BUSD", "TUSD", "FRAX", "FDUSD",
})


def load_snapshot_with_integrity_check() -> dict:
    """cycle 1 snapshot 로드 + SHA256 무결성 재검증. 불일치 시 cycle 2 중단."""
    if not SNAPSHOT_PATH.exists():
        sys.exit(f"ERROR: snapshot 파일 없음: {SNAPSHOT_PATH}")

    # NIT 정정: read 한 번으로 SHA256 + JSON 파싱
    data_bytes = SNAPSHOT_PATH.read_bytes()
    actual_sha = hashlib.sha256(data_bytes).hexdigest()
    if actual_sha != EXPECTED_SHA256:
        sys.exit(
            "CRITICAL: SHA256 불일치 → cycle 2 중단 (cycle 2 v4 L45 박제 위반)\n"
            f"  expected: {EXPECTED_SHA256}\n"
            f"  actual:   {actual_sha}"
        )
    print(f"[OK] SHA256 무결성 검증 PASS: {actual_sha}")
    return json.loads(data_bytes)


def decide_tier2(snapshot: dict, upbit_krw_tickers: list[str]) -> tuple[list[str], list[tuple[str, list[str]]]]:
    """
    cycle 2 v4 L99-104 의사 코드 정확 구현.

    Tier 2 = {coin ∈ snapshot[top10] |
                coin ∉ {BTC, ETH} AND
                coin.symbol ∉ stablecoin_set AND
                f"KRW-{coin.symbol}" ∈ upbit_krw_tickers}

    Returns:
        (tier2_candidates, excluded_with_reasons)
    """
    top10 = snapshot["data"][:10]
    tier2: list[str] = []
    excluded: list[tuple[str, list[str]]] = []

    for coin in top10:
        sym = coin["symbol"].upper()
        ticker = f"KRW-{sym}"
        reasons: list[str] = []
        if sym in TIER1_SET:
            reasons.append("Tier 1 (필수, 본 단계 Tier 2 결정 대상 아님 — 별도 처리)")
        if sym in STABLECOIN_SET:
            reasons.append("스테이블 제외")
        if ticker not in upbit_krw_tickers:
            reasons.append("업비트 KRW 미상장")
        if reasons:
            excluded.append((sym, reasons))
        else:
            tier2.append(sym)

    return tier2, excluded


def main() -> None:
    print("=" * 60)
    print("W2-01 cycle 2 단계 2: Tier 2 결정 (코드 자동 산출, 인간 개입 금지)")
    print("=" * 60)
    print(f"박제 stablecoin_set ({len(STABLECOIN_SET)}개): {sorted(STABLECOIN_SET)}")
    print()

    # 1. snapshot 로드 + 무결성 검증
    snapshot = load_snapshot_with_integrity_check()
    fetched_at = snapshot.get("fetched_at")
    print(f"[OK] snapshot fetched_at (진실 시각): {fetched_at}")
    print()

    # 2. top10 출력
    print("=== snapshot top10 (시총 상위 10) ===")
    for i, coin in enumerate(snapshot["data"][:10], 1):
        sym = coin["symbol"].upper()
        name = (coin.get("name") or "")[:30]  # NIT 정정: 30자 초과 시 truncation
        cap = coin.get("market_cap") or 0
        print(f"  {i:2}. {sym:12} {name:30} cap={cap:>22,}")
    print()

    # 3. 업비트 KRW 페어 조회
    print("=== 업비트 KRW 페어 조회 ===")
    upbit_krw_tickers = pyupbit.get_tickers("KRW")
    print(f"[OK] 업비트 KRW 페어 수: {len(upbit_krw_tickers)}")
    print()

    # 4. Tier 2 결정 규칙 자동 적용
    tier2, excluded = decide_tier2(snapshot, upbit_krw_tickers)

    print("=" * 60)
    print("=== Tier 2 결정 결과 (코드 자동 산출 = 최종) ===")
    print("=" * 60)
    print(f"Tier 1 (필수): BTC, ETH")
    print(f"Tier 2 후보 (top10 ∩ KRW ∩ BTC/ETH 제외 ∩ 스테이블 제외): {tier2}")
    print()
    print("--- top10 중 Tier 2 제외 사유 ---")
    for sym, reasons in excluded:
        print(f"  {sym:12} → {' / '.join(reasons)}")
    print()

    # 5. 새 스테이블 안전판 (cycle 2 v4 L123-127)
    print("=" * 60)
    print("=== 새 스테이블 안전판 (사용자 검토) ===")
    print("=" * 60)
    print("박제 stablecoin_set 외 가치 고정 토큰이 top10에 진입했는지 검토 필요.")
    print("발견 시: 즉시 사용자 보고 + cycle 3 신규 박제 (단순 추가 금지).")
    print()
    print("--- top10 코인 중 위 분류에 들어가지 않은 항목 (수동 검토 대상) ---")
    classified = TIER1_SET | STABLECOIN_SET | set(tier2)
    for coin in snapshot["data"][:10]:
        sym = coin["symbol"].upper()
        ticker = f"KRW-{sym}"
        if sym not in classified and ticker not in upbit_krw_tickers:
            print(f"  {sym:12} (업비트 KRW 미상장이지만 새 스테이블 가능성 검토)")
    print()

    # 6. 다음 단계 안내
    print("=" * 60)
    print("=== 다음 단계 ===")
    print("=" * 60)
    print(f"각 Tier 2 후보 ({len(tier2)}개)에 대해 다음 검증:")
    print("  - 기준 2: 업비트 KRW 상장일 ≤ 2023-04-17")
    print("  - 기준 3: 30 UTC-day 평균 거래대금 ≥ 100억 (측정 창 2026-03-13~04-11)")
    print()
    print("Tier 2 통과 페어가 0개 또는 1개면 Fallback 정책 발동:")
    print("  (i) Tier 2 제거 (primary 6셀 유지)")
    print("  (ii) cycle 3 재설계 (Fallback (ii) 누적 한도 = 3회 박제)")


if __name__ == "__main__":
    main()

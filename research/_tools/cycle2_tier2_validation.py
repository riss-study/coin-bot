"""
W2-01 cycle 2 단계 2-2: Tier 2 후보 상장일 + 거래대금 검증

cycle 2 v4 박제 기준 2, 3 적용:
- 기준 2: 업비트 KRW 상장일 ≤ 2023-04-17 (cycle 2 v4 L48-55)
- 기준 3: 30 UTC-day 평균 거래대금 ≥ 100억 (cycle 2 v4 L57-68, 측정 창 2026-03-13 ~ 2026-04-11 UTC inclusive)

cycle 1 단계 2 미실시 (사이클 중단). cycle 2가 처음 실측.

박제 우선순위 (cycle 2 v4 L52-53):
- 기준 2 측정: (1) 업비트 공식 공지 우선 (2) 공지 소실 시 pyupbit.get_ohlcv_from() 최초 캔들 폴백
- 본 코드는 자동화 어려움으로 pyupbit 폴백만 사용. 사용자가 업비트 공식 공지 수동 cross-check 권고.

박제 출처:
- docs/pair-selection-criteria-week2-cycle2.md v4 (기준 2 L48-55, 기준 3 L57-68)
- docs/stage1-subplans/w2-01-data-expansion.md (W2-01.2 cycle 2 단계)

NIT2-3은 Tier 2 결정 코드(cycle 2 v4 의사 코드 L99-122)에만 외부 감사 의무.
본 검증 코드는 단순 API 호출 + 산술이므로 외부 감사 의무 X (자가 검증 + 사용자 승인).

사용:
    cd /Users/kyounghwanlee/Desktop/coin-bot
    source research/.venv/bin/activate
    python research/_tools/cycle2_tier2_validation.py
"""
from __future__ import annotations

import time

import pandas as pd
import pyupbit

# Tier 2 후보 (cycle 2 단계 2 코드 산출 결과 = 최종 박제)
# 출처: .evidence/w2-01-cycle2-step2-tier2-decision-2026-04-19.md
TIER2_CANDIDATES: tuple[str, ...] = ("XRP", "SOL", "TRX", "DOGE")

# 기준 2 박제 (cycle 2 v4 L52)
LISTING_CUTOFF = "2023-04-17"

# 기준 3 박제 (cycle 2 v4 L61-62)
VOLUME_THRESHOLD_KRW = 100 * 10**8  # 100억
WINDOW_START = "2026-03-13"  # UTC inclusive
WINDOW_END = "2026-04-11"    # UTC inclusive
WINDOW_DAYS = 30


def fetch_listing_date(ticker: str) -> tuple[pd.Timestamp | None, dict]:
    """pyupbit.get_ohlcv_from으로 페어 상장일 조회 (최초 캔들 날짜)."""
    df = pyupbit.get_ohlcv_from(
        ticker=ticker, interval="day",
        fromDatetime="2017-01-01 00:00:00", to=None, period=0.2,
    )
    if df is None or df.empty:
        return None, {"error": "pyupbit None or empty"}

    # cycle 2 v4 L53 sanity: 최초 30캔들 7일 이상 갭 없음
    first30 = df.iloc[:30]
    if len(first30) >= 2:
        diffs = first30.index.to_series().diff().dt.total_seconds() / 86400
        max_gap = float(diffs.max())
        sanity_ok = max_gap < 7
    else:
        max_gap = 0.0
        sanity_ok = True

    return df.index.min(), {
        "first30_max_gap_days": max_gap,
        "sanity_ok": sanity_ok,
        "rows": len(df),
    }


def fetch_30day_volume(ticker: str) -> tuple[float | None, dict]:
    """측정 창 내 30 UTC-day 평균 거래대금."""
    # 측정 창 양끝 + 여유 (KST↔UTC 변환 시 누락 방지)
    df = pyupbit.get_ohlcv_from(
        ticker=ticker, interval="day",
        fromDatetime="2026-03-08 00:00:00", to="2026-04-15 00:00:00",
        period=0.2,
    )
    if df is None or df.empty:
        return None, {"error": "pyupbit None or empty"}

    # research/CLAUDE.md 패턴: naive KST → UTC
    assert df.index.tz is None, "pyupbit naive KST 가정 위반"
    df.index = df.index.tz_localize("Asia/Seoul").tz_convert("UTC")

    # 측정 창 slicing (UTC inclusive 양끝)
    window = df.loc[WINDOW_START:WINDOW_END]

    # pyupbit 응답 필드 확인 (cycle 2 v4 L64 박제: value/candle_acc_trade_price 우선)
    columns = list(window.columns)
    if "value" in columns:
        daily_value = window["value"]
        field_used = "value"
    elif "candle_acc_trade_price" in columns:
        daily_value = window["candle_acc_trade_price"]
        field_used = "candle_acc_trade_price"
    else:
        # 부재 시 기본 산식 (cycle 2 v4 L63)
        daily_value = window["close"] * window["volume"]
        field_used = "close × volume (근사)"

    avg_value = float(daily_value.mean())
    return avg_value, {
        "field_used": field_used,
        "rows": len(window),
        "expected_rows": WINDOW_DAYS,
        "rows_ok": len(window) == WINDOW_DAYS,
        "columns": columns,
    }


def main() -> None:
    print("=" * 60)
    print("W2-01 cycle 2 단계 2-2: Tier 2 후보 상장일 + 거래대금 검증")
    print("=" * 60)
    print(f"Tier 2 후보 (cycle 2 단계 2 산출): {TIER2_CANDIDATES}")
    print(f"기준 2 (상장일 cutoff): ≤ {LISTING_CUTOFF}")
    print(f"기준 3 (거래대금 임계): ≥ {VOLUME_THRESHOLD_KRW:,} KRW (100억)")
    print(f"측정 창 (UTC inclusive): {WINDOW_START} ~ {WINDOW_END} ({WINDOW_DAYS}일)")
    print()

    results: list[dict] = []

    for sym in TIER2_CANDIDATES:
        ticker = f"KRW-{sym}"
        print(f"--- {ticker} ---")

        # 1. 상장일
        listing_date, listing_meta = fetch_listing_date(ticker)
        if listing_date is None:
            print(f"  ERROR 상장일: {listing_meta}")
            results.append({"ticker": ticker, "error": "상장일 조회 실패"})
            time.sleep(1)
            continue

        # KST → UTC 변환
        if listing_date.tz is None:
            listing_date_utc = listing_date.tz_localize("Asia/Seoul").tz_convert("UTC")
        else:
            listing_date_utc = listing_date
        listing_date_str = listing_date_utc.strftime("%Y-%m-%d")
        crit2_pass = listing_date_str <= LISTING_CUTOFF
        print(
            f"  상장일 (UTC): {listing_date_str} | "
            f"기준 2 (≤{LISTING_CUTOFF}): {'PASS' if crit2_pass else 'FAIL'}"
        )
        print(
            f"  sanity (최초 30캔들 max gap): "
            f"{listing_meta['first30_max_gap_days']:.2f}일 → "
            f"{'OK' if listing_meta['sanity_ok'] else 'WARN'}"
        )

        time.sleep(0.5)  # rate limit 안전

        # 2. 거래대금
        avg_vol, vol_meta = fetch_30day_volume(ticker)
        if avg_vol is None:
            print(f"  ERROR 거래대금: {vol_meta}")
            results.append({
                "ticker": ticker, "listing_date": listing_date_str,
                "crit2_pass": crit2_pass, "error": "거래대금 조회 실패",
            })
            time.sleep(1)
            continue

        crit3_pass = avg_vol >= VOLUME_THRESHOLD_KRW
        print(
            f"  30일 평균 거래대금: {avg_vol:>22,.0f} KRW | "
            f"기준 3 (≥{VOLUME_THRESHOLD_KRW:,}): {'PASS' if crit3_pass else 'FAIL'}"
        )
        print(f"  필드 사용: {vol_meta['field_used']}")
        print(
            f"  측정 창 rows: {vol_meta['rows']} (expected {vol_meta['expected_rows']}) → "
            f"{'OK' if vol_meta['rows_ok'] else 'WARN'}"
        )

        results.append({
            "ticker": ticker,
            "listing_date": listing_date_str,
            "crit2_pass": crit2_pass,
            "avg_volume_krw": avg_vol,
            "crit3_pass": crit3_pass,
            "field_used": vol_meta["field_used"],
            "rows": vol_meta["rows"],
            "rows_ok": vol_meta["rows_ok"],
        })
        print()
        time.sleep(0.5)

    # 종합
    print("=" * 60)
    print("=== Tier 2 통과 결과 ===")
    print("=" * 60)
    passed: list[str] = []
    for r in results:
        ticker = r["ticker"]
        if "error" in r:
            print(f"  {ticker:12} → ERROR ({r['error']})")
            continue
        all_pass = r.get("crit2_pass") and r.get("crit3_pass")
        status = "PASS (Tier 2 확정)" if all_pass else "FAIL"
        print(
            f"  {ticker:12} → {status} | "
            f"상장 {r['listing_date']} | "
            f"거래대금 {r['avg_volume_krw']:>22,.0f} KRW"
        )
        if all_pass:
            passed.append(ticker)

    print()
    print("=" * 60)
    print(f"=== 최종 Tier 2 (코드 산출 = 최종 박제) ===")
    print("=" * 60)
    print(f"통과 페어 ({len(passed)}개): {passed}")

    if len(passed) >= 2:
        print(f"→ 정상 진행 (cycle 2 W2-01.3 사용자 승인 → 섹션 6.2 freeze)")
    elif len(passed) == 1:
        print(f"→ Fallback 발동 (사용자 결정): (i) Tier 2 제거 / (ii) cycle 3 재설계")
    else:
        print(f"→ Fallback 발동 (사용자 결정): (i) Tier 2 0개 + primary 6셀 / (ii) cycle 3 재설계")

    # 100억 sanity check (cycle 2 v4 L68)
    print()
    print("=" * 60)
    print("=== 100억 임계값 sanity check (cycle 2 v4 L68) ===")
    print("=" * 60)
    print(f"임계값: {VOLUME_THRESHOLD_KRW:,} KRW (100억)")
    valid_vols = [r["avg_volume_krw"] for r in results if "avg_volume_krw" in r]
    if valid_vols:
        median_vol = sorted(valid_vols)[len(valid_vols) // 2]
        ratio = median_vol / VOLUME_THRESHOLD_KRW
        print(f"본 4개 후보 거래대금 중앙값: {median_vol:,.0f} KRW (임계값 대비 {ratio:.2f}x)")
        if 0.7 <= ratio <= 1.3:
            print(f"→ ±30% 이내: 임계값 100억 유지, 후보 리스트 그대로 진행")
        else:
            print(f"→ ±30% 초과 (사용자 보고): 본 사이클은 100억 그대로 유지 완주, 임계값 변경은 cycle 3")

    # 박제 우선순위 안내 (cycle 2 v4 L52-53)
    print()
    print("=" * 60)
    print("=== 박제 우선순위 (사용자 수동 cross-check 권고) ===")
    print("=" * 60)
    print("기준 2 측정 방법 (cycle 2 v4 L52-53):")
    print("  (1) 업비트 공식 공지 우선")
    print("  (2) 공지 소실 시 pyupbit.get_ohlcv_from() 최초 캔들 폴백")
    print()
    print("본 코드는 (2)만 자동 사용. 위 페어별 상장일을 업비트 공식 공지로 cross-check 권고.")
    print("불일치 시 공지 우선 채택. 일치 시 본 결과 박제.")


if __name__ == "__main__":
    main()

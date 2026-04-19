"""Create notebook 07_data_expansion.ipynb programmatically.

W2-01.4 cycle 2 데이터 수집:
- Tier 1 (BTC W1 재사용 X) + ETH 신규 수집
- Tier 2: XRP, SOL, TRX, DOGE 신규 수집 (cycle 2 v5 박제)
- 일봉 + 4시간봉 = 5 페어 × 2 interval = 10 dataset
- UTC 변환 + advertised RANGE slicing + Parquet freeze + SHA256

박제 출처:
- docs/pair-selection-criteria-week2-cycle2.md v5 섹션 5 (Tier 2 확정 + Common-window 시작일 = 2021-10-15)
- docs/stage1-subplans/w2-01-data-expansion.md W2-01.4

Run with: python _tools/make_notebook_07.py
Output: notebooks/07_data_expansion.ipynb
"""
import nbformat as nbf
from pathlib import Path

nb = nbf.v4.new_notebook()

cells = []

# Cell 1: Header
cells.append(nbf.v4.new_markdown_cell("""\
# Task W2-01.4 — 데이터 수집 (cycle 2 데이터 확장)

**Feature ID**: BT-003 W2-01.4
**Sub-plan**: `docs/stage1-subplans/w2-01-data-expansion.md` (cycle 2 v5 박제 반영)
**Cycle**: cycle 2 (cycle 1 ADA → cycle 2 TRX 변경 박제)

cycle 2 W2-01.3 사용자 확정 리스트 = `[XRP, SOL, TRX, DOGE]` (4개 모두 PASS, 2026-04-19 사용자 승인 "ㄱㄱ").

## 수집 대상 (5 페어 × 일봉/4h = 10 dataset)
- Tier 1: KRW-ETH (BTC = W1-01에서 이미 freeze, 본 노트북 수집 X)
- Tier 2: KRW-XRP, KRW-SOL, KRW-TRX, KRW-DOGE

## 박제 사실 (cycle 2 v5 단계 2-2 검증 결과)
- KRW-ETH: 자동 통과 (장기 상장)
- KRW-XRP: 상장 2017-09-25 UTC
- KRW-SOL: 상장 2021-10-15 UTC (advertised 시작 2021-01-01 이후 → actual 범위 축소)
- KRW-TRX: 상장 2018-04-05 UTC
- KRW-DOGE: 상장 2021-02-24 UTC (advertised 시작 2021-01-01 이후 → actual 범위 축소)
- pyupbit 응답 거래대금 필드 = `value` 사용 확인
- Common-window 시작일 = 2021-10-15 UTC (SOL 기준, W2-03 secondary metric용)

## 검증된 API (Day 0 + W1-01 재사용)
- pyupbit `get_ohlcv_from(ticker, interval, fromDatetime, to, period)` — naive KST 반환
- KST → UTC 변환 필수
- 에러 시 None 반환 → fetch_with_retry wrapper 필수
"""))

# Cell 2: Imports
cells.append(nbf.v4.new_code_cell("""\
import pyupbit
import pandas as pd
import numpy as np
import hashlib
import time
from pathlib import Path
from datetime import datetime, timezone

from importlib.metadata import version
print(f"pyupbit: {version('pyupbit')}")
print(f"pandas: {version('pandas')}")
"""))

# Cell 3: Helpers (W1-01 fetch_with_retry 재사용)
cells.append(nbf.v4.new_code_cell("""\
def fetch_with_retry(ticker, interval, start, end, max_retries=5, period=0.2):
    \"\"\"pyupbit get_ohlcv_from with exponential backoff retry.

    검증된 pyupbit API. 반환: pd.DataFrame (naive KST index) or raise RuntimeError.
    \"\"\"
    for attempt in range(max_retries):
        df = pyupbit.get_ohlcv_from(
            ticker=ticker, interval=interval,
            fromDatetime=start, to=end, period=period,
        )
        if df is not None and not df.empty:
            return df
        time.sleep(2 ** attempt)
    raise RuntimeError(f"Failed after {max_retries} retries: {ticker} {interval}")


def check_gaps(df, expected_freq):
    \"\"\"갭 비율 계산 (W1-01 재사용 패턴).\"\"\"
    if len(df) < 2:
        return 0, 0.0
    expected = pd.date_range(df.index[0], df.index[-1], freq=expected_freq)
    missing = len(expected) - len(df)
    pct = missing / len(expected) * 100 if len(expected) > 0 else 0
    return missing, pct


def sha256_file(path):
    \"\"\"파일 SHA256 해시.\"\"\"
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
"""))

# Cell 4: 박제 상수 + 수집 설정
cells.append(nbf.v4.new_code_cell("""\
# 박제 (cycle 2 v5)
PAIRS = ["KRW-ETH", "KRW-XRP", "KRW-SOL", "KRW-TRX", "KRW-DOGE"]
RANGE = ("2021-01-01", "2026-04-12")  # W1-01과 동일 advertised 범위 (UTC)
FREEZE_DATE = "20260412"

# W-1 해소: DATA_DIR cwd 의존성 제거. research/ 또는 research/notebooks/ 모두 대응.
cwd = Path.cwd()
if (cwd / "data").exists() and (cwd / "_tools").exists():
    DATA_DIR = cwd / "data"          # cwd = research/
elif (cwd.parent / "data").exists() and (cwd.parent / "_tools").exists():
    DATA_DIR = cwd.parent / "data"   # cwd = research/notebooks/
else:
    raise RuntimeError(
        f"DATA_DIR 위치 감지 실패 (cwd={cwd}). "
        f"research/ 또는 research/notebooks/에서 실행 필요."
    )
DATA_DIR.mkdir(exist_ok=True)

# 상장일 박제 (cycle 2 v5 섹션 5 단계 2-2 결과)
LISTING_DATE_UTC = {
    "KRW-ETH":  None,           # 장기 상장 (2017 업비트 KRW, advertised 시작 이전 가정 — 본 노트북에서 실측 검증)
    "KRW-XRP":  "2017-09-25",   # advertised 이전
    "KRW-SOL":  "2021-10-15",   # advertised 이후 → actual 범위 축소
    "KRW-TRX":  "2018-04-05",   # advertised 이전
    "KRW-DOGE": "2021-02-24",   # advertised 이후 → actual 범위 축소
}

# W-2 해소: Common-window 박제값 (cycle 2 v5)
COMMON_WINDOW_START = "2021-10-15"  # SOL 상장일 기준

print(f"수집 대상: {len(PAIRS)} 페어 × 2 interval (1d/4h) = {len(PAIRS)*2} dataset")
print(f"Advertised RANGE: {RANGE[0]} ~ {RANGE[1]} UTC")
print(f"FREEZE_DATE: {FREEZE_DATE}")
print(f"DATA_DIR: {DATA_DIR.resolve()}")
print(f"Common-window 시작일 박제: {COMMON_WINDOW_START} UTC")
"""))

# Cell 5: 수집 + UTC 변환 + Parquet 저장
cells.append(nbf.v4.new_code_cell("""\
results = []

for pair in PAIRS:
    for interval, suffix, freq in [("day", "1d", "D"), ("minute240", "4h", "4h")]:
        print(f"\\n=== {pair} {interval} ===")
        df = fetch_with_retry(pair, interval, *RANGE)
        print(f"  fetched rows: {len(df)}")

        # 타임존 처리: naive KST → UTC (CLAUDE.md 박제)
        assert df.index.tz is None, f"pyupbit 응답이 naive KST 가정 위반: {pair} {interval}"
        df.index = df.index.tz_localize("Asia/Seoul").tz_convert("UTC")

        # Advertised RANGE slicing
        df = df.loc[RANGE[0]:RANGE[1]]
        print(f"  after slicing: {len(df)} rows")
        print(f"  actual range: {df.index[0]} ~ {df.index[-1]}")

        # Parquet 저장
        path = DATA_DIR / f"{pair}_{suffix}_frozen_{FREEZE_DATE}.parquet"
        df.to_parquet(path)
        sha = sha256_file(path)

        # 무결성 검증
        missing, gap_pct = check_gaps(df, freq)
        is_monotonic = bool(df.index.is_monotonic_increasing)
        has_dup = bool(df.index.duplicated().any())

        # W-4 해소: tz UTC 안전 비교 (pandas 2.x str(tz) 변동 대응)
        tz_is_utc = (
            df.index.tz is not None
            and df.index.tz.utcoffset(df.index[0]) == pd.Timedelta(0)
        )

        results.append({
            "pair": pair, "interval": interval, "rows": len(df),
            "actual_start": str(df.index[0]),
            "actual_end": str(df.index[-1]),
            "gap_count": int(missing),
            "gap_pct": float(gap_pct),
            "monotonic": is_monotonic,
            "has_duplicates": has_dup,
            "tz_utc": tz_is_utc,
            "sha256": sha,
            "file_size": path.stat().st_size,
        })

        time.sleep(0.5)  # rate limit 안전

print(f"\\n수집 완료: {len(results)} dataset")
"""))

# Cell 6: 결과 표 + 무결성 검증 종합 (assert 강제)
cells.append(nbf.v4.new_code_cell("""\
results_df = pd.DataFrame(results)

# NIT-1 해소: 핵심 컬럼만 출력 (가독성)
core_cols = ["pair", "interval", "rows", "actual_start", "gap_pct", "monotonic", "has_duplicates", "tz_utc"]
print(results_df[core_cols].to_string(index=False))
print()

# 무결성 검증 (W1-01 패턴)
all_monotonic = results_df["monotonic"].all()
all_no_dup = (~results_df["has_duplicates"]).all()
all_utc = results_df["tz_utc"].all()
all_low_gap = (results_df["gap_pct"] < 0.1).all()

print(f"무결성 검증:")
print(f"  monotonic 증가: {'PASS' if all_monotonic else 'FAIL'}")
print(f"  중복 없음:      {'PASS' if all_no_dup else 'FAIL'}")
print(f"  UTC 타임존:    {'PASS' if all_utc else 'FAIL'}")
print(f"  갭 < 0.1%:     {'PASS' if all_low_gap else 'FAIL'} (max: {results_df['gap_pct'].max():.4f}%)")

assert all_monotonic, "monotonic 위반 = 데이터 무결성 깨짐"
assert all_no_dup, "중복 인덱스 발견"
assert all_utc, "UTC 타임존 변환 실패"
assert all_low_gap, f"갭 0.1% 초과 = 데이터 누락 위험 (max: {results_df['gap_pct'].max():.4f}%)"  # backtest-reviewer W-1 해소

# W-2 해소: Common-window 박제 자동 assert (cycle 2 v5 = 2021-10-15 UTC)
sol_actual_start = results_df.loc[
    (results_df["pair"] == "KRW-SOL") & (results_df["interval"] == "day"),
    "actual_start"
].iloc[0]
print(f"\\nCommon-window 박제 검증:")
print(f"  cycle 2 v5 박제: {COMMON_WINDOW_START} UTC (SOL 기준)")
print(f"  KRW-SOL day actual_start: {sol_actual_start}")
assert sol_actual_start.startswith(COMMON_WINDOW_START), (
    f"cycle 2 v5 박제 위반: SOL day actual_start={sol_actual_start} ≠ {COMMON_WINDOW_START}. "
    f"단계 2-2 결과와 W2-01.4 실측 불일치 → cycle 2 중단 + 사용자 보고 필요"
)
print(f"  → PASS (박제 일치)")

# W-3 해소: ETH 상장일 박제 검증 (advertised 시작 이전 가정)
eth_actual_start = results_df.loc[
    (results_df["pair"] == "KRW-ETH") & (results_df["interval"] == "day"),
    "actual_start"
].iloc[0]
print(f"\\nETH 상장일 박제 검증:")
print(f"  cycle 2 v5 가정: ETH advertised 시작({RANGE[0]}) 이전 상장")
print(f"  KRW-ETH day actual_start: {eth_actual_start}")
# advertised slicing 후 actual_start는 RANGE[0] 이후. 즉 ETH가 advertised 이전 상장이면 actual_start = RANGE[0] 부근.
# advertised 이후 상장이면 actual_start > RANGE[0] → 박제 가정 위반.
assert eth_actual_start[:10] <= RANGE[0], (
    f"ETH 박제 가정 위반: actual_start={eth_actual_start} > {RANGE[0]}. "
    f"ETH가 advertised 시작 이후 상장 → cycle 2 v5 LISTING_DATE_UTC[KRW-ETH] 박제 갱신 필요"
)
print(f"  → PASS (박제 일치, ETH advertised 시작 이전 상장 확인)")
"""))

# Cell 7: actual 범위 metadata 박제 (gitignored data_hashes.txt 대체)
cells.append(nbf.v4.new_code_cell("""\
# data_hashes.txt 갱신 시도 (.gitignore 누적 문제 알림)
HASH_FILE = DATA_DIR / "data_hashes.txt"

new_lines = []
new_lines.append(f"# === W2-01.4 cycle 2 추가 (2026-04-19) ===")
new_lines.append(f"# Generated by 07_data_expansion.ipynb on {datetime.now(timezone.utc).isoformat()}")
new_lines.append(f"# Freeze date: {FREEZE_DATE}")
new_lines.append(f"# Advertised range (UTC, half-open): {RANGE[0]}T00:00:00+00:00 ~ {RANGE[1]}T00:00:00+00:00")
new_lines.append(f"# cycle 2 v5 박제: Tier 2 = [XRP, SOL, TRX, DOGE]")
new_lines.append(f"# Common-window 시작일: 2021-10-15 UTC (SOL 상장 기준)")
new_lines.append("")

for r in results:
    pair = r["pair"]
    suffix = "1d" if r["interval"] == "day" else "4h"
    new_lines.append(
        f"# {pair} {suffix}: rows={r['rows']}, actual={r['actual_start']} ~ {r['actual_end']}, "
        f"gap_count={r['gap_count']}, gap_pct={r['gap_pct']:.4f}%"
    )
    new_lines.append(f"{pair}_{suffix}_frozen_{FREEZE_DATE}.parquet: {r['sha256']}")
new_lines.append("")

# NIT-3 해소: 기존 data_hashes.txt에 안전 append (마지막 newline + 빈 파일 처리)
existing = HASH_FILE.read_text() if HASH_FILE.exists() else ""
existing_stripped = existing.rstrip()
separator = "\\n\\n" if existing_stripped else ""
HASH_FILE.write_text(existing_stripped + separator + "\\n".join(new_lines) + "\\n")
print(f"data_hashes.txt 갱신: {HASH_FILE.resolve()}")
print(f"파일 크기: {HASH_FILE.stat().st_size} bytes")
print()
print("--- 추가된 내용 ---")
print("\\n".join(new_lines))
"""))

# Cell 8: 종합 + 다음 단계
cells.append(nbf.v4.new_markdown_cell("""\
## 결과 요약 (cycle 2 v5 박제)

- 수집 dataset: 5 페어 × 2 interval = 10
- Advertised RANGE: 2021-01-01 ~ 2026-04-12 UTC
- Common-window 시작일: 2021-10-15 UTC (SOL 기준)

### 다음 단계 (cycle 2 W2-01.5/.6/.7)

1. **W2-01.5 무결성 검증**: 갭 < 0.1% / 중복 0 / UTC / monotonic — 위 셀에서 자동 검증
2. **W2-01.6 SHA256 + data_hashes.txt 갱신**: 위 셀에서 자동 갱신 (단 `.gitignore` `research/data/` 룰로 git tracked X — 별도 정정 작업 미정)
3. **W2-01.7 Evidence + backtest-reviewer**: `.evidence/w2-01-cycle2-step4-data-collection.md` 작성 + 외부 감사관 호출
"""))

# Save
nb["cells"] = cells
nb["metadata"] = {
    "kernelspec": {
        "display_name": "Python 3 (ipykernel)",
        "language": "python",
        "name": "python3",
    },
    "language_info": {"name": "python"},
}

OUT = Path(__file__).resolve().parent.parent / "notebooks" / "07_data_expansion.ipynb"
OUT.parent.mkdir(exist_ok=True)
nbf.write(nb, str(OUT))
print(f"Wrote {OUT}")

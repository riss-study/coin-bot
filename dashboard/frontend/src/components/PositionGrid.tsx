// PositionGrid — 3 cells (BTC_A, ETH_A, BTC_D) open position 카드.
// Server Component.

import { api, formatKRW, formatPct } from "@/lib/api";

const CELLS = ["KRW-BTC_A", "KRW-ETH_A", "KRW-BTC_D"];

export default async function PositionGrid() {
  let res;
  try {
    res = await api.positions();
  } catch {
    return <div className="text-red-600">positions fetch 실패</div>;
  }

  const byKey = new Map(res.positions.map((p) => [p.cell_key, p]));

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
      {CELLS.map((key) => {
        const pos = byKey.get(key);
        return (
          <div
            key={key}
            className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
          >
            <div className="flex items-center justify-between">
              <div className="font-mono text-sm font-semibold">{key}</div>
              {pos ? (
                <span className="rounded bg-blue-100 px-2 py-0.5 text-xs text-blue-900">
                  open
                </span>
              ) : (
                <span className="rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-600">
                  empty
                </span>
              )}
            </div>
            {pos ? (
              <div className="mt-2 space-y-1 text-sm">
                <Row label="entry" value={`${formatKRW(pos.entry_price_krw)} KRW`} />
                <Row label="volume" value={pos.volume.toFixed(8)} />
                <Row
                  label="invested"
                  value={`${formatKRW(pos.krw_invested)} KRW`}
                />
                <Row
                  label="current"
                  value={
                    pos.current_price_krw
                      ? `${formatKRW(pos.current_price_krw)} KRW`
                      : "—"
                  }
                />
                <Row
                  label="unrealized"
                  value={`${formatKRW(pos.unrealized_pnl_krw, true)} KRW (${formatPct(pos.unrealized_pnl_ratio)})`}
                  highlight={
                    pos.unrealized_pnl_krw == null
                      ? ""
                      : pos.unrealized_pnl_krw > 0
                        ? "text-green-700"
                        : pos.unrealized_pnl_krw < 0
                          ? "text-red-700"
                          : ""
                  }
                />
              </div>
            ) : (
              <div className="mt-2 text-sm text-gray-400">no position</div>
            )}
          </div>
        );
      })}
    </div>
  );
}

function Row({
  label,
  value,
  highlight = "",
}: {
  label: string;
  value: string;
  highlight?: string;
}) {
  return (
    <div className="flex justify-between gap-2">
      <span className="text-gray-500">{label}</span>
      <span className={`font-mono ${highlight}`}>{value}</span>
    </div>
  );
}

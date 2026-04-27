// PositionGrid — 동적 open positions (모든 strategies, 진입한 cell만).
// Server Component.

import { api, formatKRW, formatPct } from "@/lib/api";

export default async function PositionGrid() {
  let res;
  try {
    res = await api.positions();
  } catch {
    return <div className="text-red-600">positions fetch 실패</div>;
  }

  if (res.positions.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-4 text-sm text-gray-500">
        진입 중인 포지션 없음 (33 cells 평가 중, 매일 KST 09:05 cycle)
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {res.positions.map((pos) => (
        <div
          key={pos.cell_key}
          className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
        >
          <div className="flex items-center justify-between">
            <div className="font-mono text-sm font-semibold">{pos.cell_key}</div>
            <span className="rounded bg-blue-100 px-2 py-0.5 text-xs text-blue-900">
              open · {pos.strategy}
            </span>
          </div>
          <div className="mt-2 space-y-1 text-sm">
            <Row label="entry" value={`${formatKRW(pos.entry_price_krw)} KRW`} />
            <Row label="volume" value={pos.volume.toFixed(8)} />
            <Row label="invested" value={`${formatKRW(pos.krw_invested)} KRW`} />
            <Row
              label="current"
              value={pos.current_price_krw ? `${formatKRW(pos.current_price_krw)} KRW` : "—"}
            />
            <Row
              label="unrealized"
              value={`${formatKRW(pos.unrealized_pnl_krw, true)} KRW (${formatPct(pos.unrealized_pnl_ratio)})`}
              highlight={
                pos.unrealized_pnl_krw == null
                  ? ""
                  : pos.unrealized_pnl_krw > 0
                    ? "text-red-700"
                    : pos.unrealized_pnl_krw < 0
                      ? "text-blue-700"
                      : ""
              }
            />
          </div>
        </div>
      ))}
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

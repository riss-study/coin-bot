// TradesTable — 최근 trades-YYYY.jsonl 테이블.
// Server Component.

import { api, formatKRW, formatKstShort } from "@/lib/api";

export default async function TradesTable() {
  let res;
  try {
    res = await api.trades(28);
  } catch {
    return <div className="text-red-600">trades fetch 실패</div>;
  }

  if (res.trades.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-4 text-sm text-gray-500">
        최근 28일 trades 없음 (페이퍼 초기 정상)
      </div>
    );
  }

  const recent = res.trades.slice(-30).reverse();

  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm">
      <table className="min-w-full divide-y divide-gray-200 text-sm">
        <thead className="bg-gray-50 text-xs uppercase tracking-wide text-gray-600">
          <tr>
            <th className="px-3 py-2 text-left">time</th>
            <th className="px-3 py-2 text-left">side</th>
            <th className="px-3 py-2 text-left">pair</th>
            <th className="px-3 py-2 text-right">price</th>
            <th className="px-3 py-2 text-right">vol</th>
            <th className="px-3 py-2 text-right">fees</th>
            <th className="px-3 py-2 text-right">PnL</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {recent.map((t, idx) => {
            const pnl = t.realized_pnl_krw;
            const pnlClass =
              pnl == null
                ? "text-gray-400"
                : pnl > 0
                  ? "text-green-700"
                  : pnl < 0
                    ? "text-red-700"
                    : "text-gray-600";
            return (
              <tr key={`${t.order_uuid}-${idx}`}>
                <td className="px-3 py-1.5 font-mono text-xs">
                  {formatKstShort(t.ts_utc)}
                </td>
                <td className="px-3 py-1.5">
                  <span
                    className={`rounded px-1.5 py-0.5 text-xs ${
                      t.side === "buy"
                        ? "bg-green-100 text-green-800"
                        : "bg-red-100 text-red-800"
                    }`}
                  >
                    {t.side}
                  </span>
                </td>
                <td className="px-3 py-1.5 font-mono text-xs">{t.pair}</td>
                <td className="px-3 py-1.5 text-right font-mono">
                  {formatKRW(t.price_krw)}
                </td>
                <td className="px-3 py-1.5 text-right font-mono text-xs">
                  {t.volume.toFixed(6)}
                </td>
                <td className="px-3 py-1.5 text-right font-mono text-xs text-gray-500">
                  {formatKRW(t.fees_krw)}
                </td>
                <td className={`px-3 py-1.5 text-right font-mono ${pnlClass}`}>
                  {pnl == null ? "—" : formatKRW(pnl, true)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

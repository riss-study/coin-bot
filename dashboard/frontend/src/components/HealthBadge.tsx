// HealthBadge — daemon alive 상태 + 마지막 cycle 시각.
// Server Component (default). 매 요청 시 backend fetch.

import { api, formatKstShort } from "@/lib/api";

export default async function HealthBadge() {
  let health;
  try {
    health = await api.health();
  } catch {
    return (
      <div className="rounded-md bg-red-100 px-3 py-2 text-sm text-red-900">
        backend 연결 실패
      </div>
    );
  }

  const alive = health.daemon_alive;
  const color =
    alive === true
      ? "bg-green-100 text-green-900"
      : alive === false
        ? "bg-red-100 text-red-900"
        : "bg-gray-100 text-gray-700";
  const label =
    alive === true ? "alive" : alive === false ? "stale" : "unknown";

  return (
    <div className={`rounded-md px-3 py-2 text-sm ${color}`}>
      <div className="font-semibold">daemon: {label}</div>
      <div className="text-xs">
        last cycle: {formatKstShort(health.last_run_ts_utc) || "—"}
      </div>
    </div>
  );
}

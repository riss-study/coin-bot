// 메인 대시보드 — Server Component 조립.

import HealthBadge from "@/components/HealthBadge";
import LogsPanel from "@/components/LogsPanel";
import MarketsPanel from "@/components/MarketsPanel";
import PositionGrid from "@/components/PositionGrid";
import SummaryCards from "@/components/SummaryCards";
import TradesTable from "@/components/TradesTable";

export const dynamic = "force-dynamic"; // SSR 매번 fetch

export default function DashboardPage() {
  return (
    <main className="mx-auto max-w-7xl space-y-6 p-4 sm:p-6">
      <header className="flex flex-col items-start justify-between gap-3 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-2xl font-bold">coin-bot dashboard</h1>
          <p className="text-sm text-gray-500">
            V2-Dashboard Phase 1 · read-only · paper mode
          </p>
        </div>
        {/* @ts-expect-error Async Server Component */}
        <HealthBadge />
      </header>

      <section>
        <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-gray-600">
          summary
        </h2>
        {/* @ts-expect-error Async Server Component */}
        <SummaryCards />
      </section>

      <section>
        <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-gray-600">
          open positions
        </h2>
        {/* @ts-expect-error Async Server Component */}
        <PositionGrid />
      </section>

      <section>
        <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-gray-600">
          KRW markets (참고용)
        </h2>
        <MarketsPanel />
      </section>

      <section>
        <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-gray-600">
          recent trades (28d)
        </h2>
        {/* @ts-expect-error Async Server Component */}
        <TradesTable />
      </section>

      <section>
        <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-gray-600">
          recent logs (today)
        </h2>
        <LogsPanel />
      </section>
    </main>
  );
}

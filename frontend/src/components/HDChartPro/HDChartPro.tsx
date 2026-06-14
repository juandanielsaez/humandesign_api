import { useEffect } from "react";
import { useHDChart } from "../../hooks/useHDChart";
import type { CalculateRequestV2 } from "../../types/hdchart";
import GatesSidebar from "./GatesSidebar";
import BodyGraphPlaceholder from "./BodyGraphPlaceholder";

// ── Props ──────────────────────────────────────────────────────────────────
export interface HDChartProProps {
  /** Birth-data payload sent to /v2/calculate */
  request: CalculateRequestV2;
  /** Bearer token for API authentication */
  token: string;
  /** Optional API base URL override (defaults to VITE_HD_API_URL or localhost) */
  apiBaseUrl?: string;
}

// ── Component ──────────────────────────────────────────────────────────────
export default function HDChartPro({ request, token }: HDChartProProps) {
  const { data, loading, error, fetchChart } = useHDChart();

  // Fetch on mount & whenever the request payload changes
  useEffect(() => {
    fetchChart(request, token);
  }, [request, token, fetchChart]);

  // ── Derived data ─────────────────────────────────────────────────────────
  const general = data?.general;
  const variables = data?.variables;

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-4 md:p-8">
      {/* ── Header strip ──────────────────────────────────────────────────── */}
      {general && (
        <header className="mb-6 text-center space-y-1">
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight">
            {general.energy_type}{" "}
            <span className="text-indigo-400">— {general.profile}</span>
          </h1>
          <p className="text-sm text-gray-400">
            {general.strategy} · {general.inner_authority} ·{" "}
            {general.definition}
          </p>
          <p className="text-xs text-gray-500">
            {general.inc_cross}
          </p>
          {variables && (
            <p className="text-xs font-mono text-gray-500">
              Variable: {variables.short_code}
            </p>
          )}
        </header>
      )}

      {/* ── Loading / Error states ────────────────────────────────────────── */}
      {loading && (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin h-10 w-10 border-4 border-indigo-500 border-t-transparent rounded-full" />
        </div>
      )}

      {error && (
        <div className="mx-auto max-w-lg rounded-xl bg-red-900/40 border border-red-600 p-4 text-sm text-red-200 mb-6">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* ── 3-column grid: Design | BodyGraph | Personality ───────────────── */}
      {data && !loading && (
        <div className="grid grid-cols-1 lg:grid-cols-[minmax(220px,1fr)_2fr_minmax(220px,1fr)] gap-4 lg:gap-6">
          {/* Left — Design (unconscious) */}
          <GatesSidebar
            title="Design"
            subtitle="Unconscious · Body"
            accentColor="border-red-500"
            gates={data.gates?.design}
          />

          {/* Center — BodyGraph SVG placeholder */}
          <BodyGraphPlaceholder />

          {/* Right — Personality (conscious) */}
          <GatesSidebar
            title="Personality"
            subtitle="Conscious · Mind"
            accentColor="border-indigo-500"
            gates={data.gates?.personality}
          />
        </div>
      )}
    </div>
  );
}

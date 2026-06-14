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
  const { data, bodygraphSvg, loading, error, fetchChart } = useHDChart();

  // Fetch on mount & whenever the request payload changes
  useEffect(() => {
    fetchChart(request, token);
  }, [request, token, fetchChart]);

  return (
    <div className="min-h-screen bg-white text-gray-800 p-4 md:p-8">
      {/* ── Loading state ─────────────────────────────────────────────────── */}
      {loading && (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin h-10 w-10 border-4 border-gray-300 border-t-gray-600 rounded-full" />
        </div>
      )}

      {/* ── Error state (hidden once data arrives) ────────────────────────── */}
      {error && !data && (
        <div className="mx-auto max-w-lg rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-700 mb-6">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* ── 3-column grid: Design | BodyGraph | Personality ───────────────── */}
      {data && !loading && (
        <div className="grid grid-cols-1 lg:grid-cols-[minmax(120px,160px)_1fr_minmax(120px,160px)] gap-0 lg:gap-2 items-start max-w-5xl mx-auto">
          {/* Left — Design (unconscious, red) */}
          <GatesSidebar side="design" gates={data.gates?.design} />

          {/* Center — BodyGraph image */}
          {bodygraphSvg ? (
            <div
              className="w-full flex items-start justify-center [&>svg]:w-full [&>svg]:h-auto [&>svg]:max-h-[80vh]"
              dangerouslySetInnerHTML={{ __html: bodygraphSvg }}
            />
          ) : (
            <BodyGraphPlaceholder />
          )}

          {/* Right — Personality (conscious, dark) */}
          <GatesSidebar side="personality" gates={data.gates?.personality} />
        </div>
      )}
    </div>
  );
}

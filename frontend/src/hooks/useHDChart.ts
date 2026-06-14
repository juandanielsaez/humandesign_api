import { useState, useCallback } from "react";
import type {
  CalculateRequestV2,
  CalculateResponseV2,
} from "../types/hdchart";

const API_BASE_URL =
  import.meta.env.VITE_HD_API_URL ?? "http://localhost:8000";

interface UseHDChartReturn {
  data: CalculateResponseV2 | null;
  bodygraphSvg: string | null;
  loading: boolean;
  error: string | null;
  fetchChart: (params: CalculateRequestV2, token: string) => Promise<void>;
}

export function useHDChart(): UseHDChartReturn {
  const [data, setData] = useState<CalculateResponseV2 | null>(null);
  const [bodygraphSvg, setBodygraphSvg] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchChart = useCallback(
    async (params: CalculateRequestV2, token: string) => {
      setLoading(true);
      setError(null);

      try {
        // Build query string for /bodygraph GET endpoint
        const qs = new URLSearchParams({
          year: String(params.year),
          month: String(params.month),
          day: String(params.day),
          hour: String(params.hour),
          minute: String(params.minute),
          second: String(params.second ?? 0),
          place: params.place,
          fmt: "svg",
        });

        const authHeaders = { Authorization: `Bearer ${token}` };

        // Fire both requests in parallel
        const [calcRes, bgRes] = await Promise.all([
          fetch(`${API_BASE_URL}/v2/calculate`, {
            method: "POST",
            headers: { "Content-Type": "application/json", ...authHeaders },
            body: JSON.stringify(params),
          }),
          fetch(`${API_BASE_URL}/bodygraph?${qs.toString()}`, {
            headers: authHeaders,
          }),
        ]);

        if (!calcRes.ok) {
          const errBody = await calcRes.text();
          throw new Error(`API ${calcRes.status}: ${errBody}`);
        }

        const json: CalculateResponseV2 = await calcRes.json();
        setData(json);

        if (bgRes.ok) {
          const svgText = await bgRes.text();
          setBodygraphSvg(svgText);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
      } finally {
        setLoading(false);
      }
    },
    [],
  );

  return { data, bodygraphSvg, loading, error, fetchChart };
}

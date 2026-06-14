import { useState, useCallback } from "react";
import type {
  CalculateRequestV2,
  CalculateResponseV2,
} from "../types/hdchart";

const API_BASE_URL =
  import.meta.env.VITE_HD_API_URL ?? "http://localhost:8000";

interface UseHDChartReturn {
  data: CalculateResponseV2 | null;
  loading: boolean;
  error: string | null;
  fetchChart: (params: CalculateRequestV2, token: string) => Promise<void>;
}

export function useHDChart(): UseHDChartReturn {
  const [data, setData] = useState<CalculateResponseV2 | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchChart = useCallback(
    async (params: CalculateRequestV2, token: string) => {
      setLoading(true);
      setError(null);

      try {
        const res = await fetch(`${API_BASE_URL}/v2/calculate`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(params),
        });

        if (!res.ok) {
          const errBody = await res.text();
          throw new Error(`API ${res.status}: ${errBody}`);
        }

        const json: CalculateResponseV2 = await res.json();
        setData(json);
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
      } finally {
        setLoading(false);
      }
    },
    [],
  );

  return { data, loading, error, fetchChart };
}

import { useState } from "react";
import { HDChartPro } from "./components/HDChartPro";
import type { CalculateRequestV2 } from "./types/hdchart";

const DEFAULT_REQUEST: CalculateRequestV2 = {
  year: 1987,
  month: 6,
  day: 15,
  hour: 12,
  minute: 30,
  place: "Berlin, Germany",
};

export default function App() {
  const [token, setToken] = useState("");
  const [submitted, setSubmitted] = useState(false);

  if (!submitted) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center p-4">
        <div className="w-full max-w-md space-y-4">
          <h1 className="text-2xl font-bold text-gray-100 text-center">
            HD Chart Pro
          </h1>
          <p className="text-sm text-gray-400 text-center">
            Enter your API bearer token to load the chart.
          </p>
          <input
            type="text"
            placeholder="Bearer token"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            className="w-full rounded-lg bg-gray-800 border border-gray-700 text-gray-100 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <button
            onClick={() => setSubmitted(true)}
            disabled={!token.trim()}
            className="w-full rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white font-semibold py-2 transition-colors"
          >
            Load Chart
          </button>
        </div>
      </div>
    );
  }

  return <HDChartPro request={DEFAULT_REQUEST} token={token} />;
}

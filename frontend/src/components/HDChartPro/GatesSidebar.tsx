import type { GateV2 } from "../../types/hdchart";
import GatePlanetRow from "./GatePlanetRow";

interface GatesSidebarProps {
  title: string;
  subtitle: string;
  accentColor: string;       // Tailwind border-color class, e.g. "border-red-500"
  gates: Record<string, GateV2> | undefined;
}

const PLANET_ORDER = [
  "Sun",
  "Earth",
  "Moon",
  "North_Node",
  "South_Node",
  "Mercury",
  "Venus",
  "Mars",
  "Jupiter",
  "Saturn",
  "Uranus",
  "Neptune",
  "Pluto",
];

export default function GatesSidebar({
  title,
  subtitle,
  accentColor,
  gates,
}: GatesSidebarProps) {
  const sorted = gates
    ? PLANET_ORDER.filter((p) => p in gates).map((p) => ({
        planet: p,
        gate: gates[p],
      }))
    : [];

  return (
    <section
      className={`rounded-2xl border-2 ${accentColor} bg-gray-900/60 backdrop-blur-md p-4 flex flex-col`}
    >
      {/* Header */}
      <h2 className="text-lg font-bold tracking-wide uppercase">{title}</h2>
      <p className="text-xs text-gray-400 mb-3">{subtitle}</p>

      {/* Gate table */}
      {sorted.length === 0 ? (
        <p className="text-sm text-gray-500 italic">No gate data loaded.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="text-gray-400 text-xs uppercase border-b border-white/10">
                <th className="pb-1 pr-2">☆</th>
                <th className="pb-1 px-2">Gate</th>
                <th className="pb-1 px-2">Line</th>
                <th className="pb-1 px-2">C/T/B</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map(({ planet, gate }) => (
                <GatePlanetRow key={planet} planet={planet} gate={gate} />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

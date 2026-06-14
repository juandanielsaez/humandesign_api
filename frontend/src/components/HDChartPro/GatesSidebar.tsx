import type { GateV2 } from "../../types/hdchart";
import GatePlanetRow from "./GatePlanetRow";

interface GatesSidebarProps {
  side: "design" | "personality";
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

export default function GatesSidebar({ side, gates }: GatesSidebarProps) {
  const sorted = gates
    ? PLANET_ORDER.filter((p) => p in gates).map((p) => ({
        planet: p,
        gate: gates[p],
      }))
    : [];

  if (sorted.length === 0) return null;

  const isDesign = side === "design";

  return (
    <div className="flex flex-col py-2">
      {/* Column header — fixed-width underline centered in column */}
      <div className="flex justify-center mb-4">
        <div
          className={`w-24 text-center border-b-2 pb-1 ${
            isDesign
              ? "text-red-500 border-red-500"
              : "text-gray-800 border-gray-800"
          }`}
        >
          <span className="text-xs font-bold uppercase tracking-widest">
            {isDesign ? "Design" : "Personality"}
          </span>
        </div>
      </div>

      {/* Planet rows — stretched vertically to match bodygraph height */}
      <div className="flex flex-col justify-between flex-1 space-y-4">
        {sorted.map(({ planet, gate }) => (
          <GatePlanetRow key={planet} planet={planet} gate={gate} side={side} />
        ))}
      </div>
    </div>
  );
}

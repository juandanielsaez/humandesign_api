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
      {/* Column header */}
      <h2
        className={`text-xs font-bold uppercase tracking-widest pb-1 mb-2 ${
          isDesign
            ? "text-red-500 border-b-2 border-red-500 text-right"
            : "text-gray-800 border-b-2 border-gray-800 text-left"
        }`}
      >
        {isDesign ? "Design" : "Personality"}
      </h2>

      {/* Planet rows */}
      <div className="flex flex-col gap-px px-1">
        {sorted.map(({ planet, gate }) => (
          <GatePlanetRow key={planet} planet={planet} gate={gate} side={side} />
        ))}
      </div>
    </div>
  );
}

import type { GateV2 } from "../../types/hdchart";

export interface GatePlanetRowProps {
  planet: string;
  gate: GateV2;
  /** "design" = icon left / number right (red), "personality" = number left / icon right (dark) */
  side: "design" | "personality";
}

const PLANET_GLYPHS: Record<string, string> = {
  Sun: "☉",
  Earth: "⊕",
  Moon: "☽",
  North_Node: "☊",
  South_Node: "☋",
  Mercury: "☿",
  Venus: "♀",
  Mars: "♂",
  Jupiter: "♃",
  Saturn: "♄",
  Uranus: "♅",
  Neptune: "♆",
  Pluto: "♇",
};

function FixationIndicator({ fixation }: { fixation?: Record<string, unknown> | null }) {
  if (!fixation) return null;

  const hasExaltation = "exaltation" in fixation;
  const hasDetriment = "detriment" in fixation;

  if (!hasExaltation && !hasDetriment) return null;

  return (
    <span className="inline-flex flex-col items-center justify-center leading-none text-[10px]">
      {hasExaltation && <span title="Exaltation">▲</span>}
      {hasDetriment && <span title="Detriment">▼</span>}
    </span>
  );
}

export default function GatePlanetRow({ planet, gate, side }: GatePlanetRowProps) {
  const glyph = PLANET_GLYPHS[planet] ?? planet;
  const gateLineStr = `${gate.gate}.${gate.line}`;

  const icon = (
    <span className="text-base leading-none text-center" title={planet}>
      {glyph}
    </span>
  );

  const number = (
    <span className="font-mono text-sm font-semibold tabular-nums text-right whitespace-nowrap">
      {gateLineStr}
    </span>
  );

  const tri = <FixationIndicator fixation={gate.fixation} />;

  if (side === "design") {
    // Icon | Gate.Line | Triangle
    return (
      <div className="grid grid-cols-[20px_44px_14px] gap-1 items-center justify-end mx-auto text-red-500">
        {icon}
        {number}
        <span className="flex justify-center">{tri}</span>
      </div>
    );
  }

  // Triangle | Gate.Line | Icon
  return (
    <div className="grid grid-cols-[14px_44px_20px] gap-1 items-center justify-start mx-auto text-gray-800">
      <span className="flex justify-center">{tri}</span>
      <span className="font-mono text-sm font-semibold tabular-nums text-left whitespace-nowrap">
        {gateLineStr}
      </span>
      {icon}
    </div>
  );
}

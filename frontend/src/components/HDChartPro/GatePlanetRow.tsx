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
    <span className="inline-flex flex-col items-center leading-none ml-0.5 text-[10px]">
      {hasExaltation && <span title="Exaltation">▲</span>}
      {hasDetriment && <span title="Detriment">▼</span>}
    </span>
  );
}

export default function GatePlanetRow({ planet, gate, side }: GatePlanetRowProps) {
  const glyph = PLANET_GLYPHS[planet] ?? planet;
  const gateLineStr = `${gate.gate}.${gate.line}`;

  const icon = (
    <span className="text-base leading-none" title={planet}>
      {glyph}
    </span>
  );

  const number = (
    <span className="font-mono text-sm font-semibold tabular-nums">
      {gateLineStr}
      <FixationIndicator fixation={gate.fixation} />
    </span>
  );

  if (side === "design") {
    return (
      <div className="flex items-center justify-end py-0.5 text-red-500">
        <span className="inline-flex items-center gap-2">
          {icon}
          {number}
        </span>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-start py-0.5 text-gray-800">
      <span className="inline-flex items-center gap-2">
        {number}
        {icon}
      </span>
    </div>
  );
}

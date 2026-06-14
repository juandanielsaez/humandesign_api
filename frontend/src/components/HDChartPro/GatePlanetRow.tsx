import type { GateV2 } from "../../types/hdchart";

interface GatePlanetRowProps {
  planet: string;
  gate: GateV2;
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

export default function GatePlanetRow({ planet, gate }: GatePlanetRowProps) {
  const glyph = PLANET_GLYPHS[planet] ?? planet;

  return (
    <tr className="border-b border-white/10 hover:bg-white/5 transition-colors">
      <td className="py-1.5 pr-2 text-lg" title={planet}>
        {glyph}
      </td>
      <td className="py-1.5 px-2 font-mono font-semibold">
        {gate.gate}
      </td>
      <td className="py-1.5 px-2 font-mono text-sm opacity-80">
        {gate.line}
      </td>
      <td className="py-1.5 px-2 font-mono text-xs opacity-60">
        {gate.color}/{gate.tone}/{gate.base}
      </td>
    </tr>
  );
}

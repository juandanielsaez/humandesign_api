import { MoveLeft, MoveRight } from "lucide-react";
import type { VariablesV2 } from "../../types/hdchart";

interface VariableArrowsProps {
  variables: VariablesV2;
}

function VarArrow({ direction }: { direction: "left" | "right" }) {
  const Icon = direction === "left" ? MoveLeft : MoveRight;
  return <Icon className="w-6 h-6" strokeWidth={1.5} />;
}

export default function VariableArrows({ variables }: VariableArrowsProps) {
  const resolve = (value: string): "left" | "right" =>
    value.toLowerCase() === "left" ? "left" : "right";

  return (
    <>
      {/* ── Left side (Design, red) — optically centered ─────────────── */}
      <div className="absolute top-[14%] left-[14%] text-red-500">
        <VarArrow direction={resolve(variables.top_left.value)} />
      </div>
      <div className="absolute top-[22%] left-[14%] text-red-500">
        <VarArrow direction={resolve(variables.bottom_left.value)} />
      </div>

      {/* ── Right side (Personality, dark) ──────────────────────────────── */}
      <div className="absolute top-[14%] right-[20%] text-gray-800">
        <VarArrow direction={resolve(variables.top_right.value)} />
      </div>
      <div className="absolute top-[22%] right-[20%] text-gray-800">
        <VarArrow direction={resolve(variables.bottom_right.value)} />
      </div>
    </>
  );
}

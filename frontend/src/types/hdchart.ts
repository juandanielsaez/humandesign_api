// ---------------------------------------------------------------------------
// TypeScript interfaces for the /v2/calculate API response
// Derived from: openapi.yaml  → CalculateResponseV2 & related schemas
// ---------------------------------------------------------------------------

// ── Variable (arrow) detail ────────────────────────────────────────────────
export interface VariableItemV2 {
  value: string;       // "left" | "right"
  name: string;        // e.g. "Motivation", "Perspective", "Digestion", "Environment"
  aspect: string;      // e.g. "Personality (Mind)", "Design (Body)"
  def_type: string;    // e.g. "Strategic", "Receptive", "Passive", "Observer"
}

export interface VariablesV2 {
  top_right: VariableItemV2;
  bottom_right: VariableItemV2;
  top_left: VariableItemV2;
  bottom_left: VariableItemV2;
  short_code: string;  // e.g. "PLR DRR"
}

// ── General section ────────────────────────────────────────────────────────
export interface GeneralSectionV2 {
  birth_date: string;
  create_date: string;
  birth_place: string;
  age: number;
  gender: string;
  islive: boolean;
  zodiac_sign: string;
  energy_type: string;
  strategy: string;
  signature: string;
  not_self: string;
  aura: string;
  inner_authority: string;
  inc_cross: string;
  profile: string;
  definition: string;
}

// ── Centers ────────────────────────────────────────────────────────────────
export interface CentersV2 {
  defined: string[];
  undefined: string[];
}

// ── Gate (single planetary activation) ─────────────────────────────────────
export interface GateV2 {
  gate: number;
  line: number;
  color: number;
  tone: number;
  base: number;
  lon: number;
  gate_name?: string | null;
  gate_summary?: string | null;
  line_name?: string | null;
  line_description?: string | null;
  fixation?: Record<string, unknown> | null;
}

// ── Gates section – keyed by planet name ───────────────────────────────────
export interface GatesV2 {
  personality: Record<string, GateV2>;
  design: Record<string, GateV2>;
}

// ── Channels ───────────────────────────────────────────────────────────────
export interface ChannelV2 {
  channel: string;
  [key: string]: unknown;
}

// ── Advanced sub‑sections ──────────────────────────────────────────────────
export interface DreamRaveOutput {
  activated_centers: string[];
  activated_gates: number[];
  status: string;
}

export interface GlobalCycleOutput {
  great_cycle: string;
  cycle_cross: string;
  gates: number[];
  description: string;
}

export interface AdvancedSectionV2 {
  dream_rave?: DreamRaveOutput | null;
  global_cycle?: GlobalCycleOutput | null;
}

// ── Top‑level V2 response ──────────────────────────────────────────────────
export interface CalculateResponseV2 {
  general?: GeneralSectionV2;
  centers?: CentersV2;
  channels?: ChannelV2[] | null;
  variables?: VariablesV2;
  gates?: GatesV2;
  mechanics?: Record<string, unknown> | null;
  advanced?: AdvancedSectionV2;
}

// ── Request payload ────────────────────────────────────────────────────────
export interface CalculateRequestV2 {
  year: number;
  month: number;
  day: number;
  hour: number;
  minute: number;
  second?: number;
  place: string;
  gender?: string;
  islive?: boolean;
  latitude?: number | null;
  longitude?: number | null;
  include?: string[] | null;
  exclude?: string[] | null;
}

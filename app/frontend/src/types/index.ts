// ── Tipos base ─────────────────────────────────────────────

export interface ScenarioFilters {
  down?: number;
  ytf_min?: number;
  ytf_max?: number;
  ytg_max?: number;
  score_diff_min?: number;
  score_diff_max?: number;
  off?: string;
  qtr?: number;
}

export interface PlayMetrics {
  n: number;
  avg_yards: number | null;
  median_yards: number | null;
  first_down_rate: number | null;
  turnover_rate: number | null;
  penalty_rate: number | null;
  touchdown_rate: number | null;
  sack_rate: number | null;
}

export interface ScenarioResponse {
  total: number;
  filters_applied: ScenarioFilters;
  overall: PlayMetrics;
  by_category: Record<string, PlayMetrics>;
  by_shotgun: { shotgun: PlayMetrics; no_shotgun: PlayMetrics };
  by_pass_direction: Record<string, PlayMetrics>;
  ytf_distribution: Record<string, number>;
}

// ── Comparativas ───────────────────────────────────────────

export interface ZoneMetrics {
  n: number; avg: number | null; median: number | null;
  fd_rate: number | null; to_rate: number | null; pen_rate: number | null;
  direction: string; label: string; usage_pct: number;
}

export interface ZonesResponse {
  comparative: "A";
  title: string;
  data: Record<string, { total_pass_plays: number; zones: ZoneMetrics[] }>;
}

export interface FormationRow {
  n: number; avg: number | null; median: number | null;
  fd_rate: number | null; to_rate: number | null; pen_rate: number | null;
  formation: string; play_type: string; usage_pct: number;
}

export interface FormationResponse {
  comparative: "B";
  title: string;
  data: Record<string, { total_plays: number; breakdown: FormationRow[] }>;
}

export interface TempoMetrics {
  n: number; avg: number | null; median: number | null;
  fd_rate: number | null; to_rate: number | null; pen_rate: number | null;
  is_no_huddle: boolean;
}

export interface TempoQuarter {
  total_plays: number;
  no_huddle: TempoMetrics;
  normal: TempoMetrics;
  filtered_q4_close: boolean;
  delta: Record<string, number | null>;
}

export interface TempoResponse {
  comparative: "C";
  title: string;
  data: Record<string, TempoQuarter>;
}

// ── Coach Advice ───────────────────────────────────────────

export interface CoachAdviceRequest {
  down: number;
  yards_to_first: number;
  yards_to_goal: number;
  score_diff: number;
  qtr: number;
  off_team?: string;
  avg_yards_pass?: number;
  avg_yards_run?: number;
  fd_rate_shotgun?: number;
  fd_rate_no_shotgun?: number;
  best_pass_zone?: string;
  no_huddle_delta?: number;
}

export interface CoachAdviceResponse {
  advice: string;
  rule_based_advice: string;
  source: "strands-agents" | "rule-based";
  scenario: {
    down: number; yards_to_first: number; yards_to_goal: number;
    score_diff: number; qtr: number;
  };
}

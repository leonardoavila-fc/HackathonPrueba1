import { useState, useEffect } from "react";
import { useScenario, useCoachAdvice, useTeams } from "../hooks/useApi";
import type { ScenarioFilters } from "../types";
import MetricCard from "./MetricCard";

export default function ScenarioPanel() {
  const { data, loading, error, fetch: fetchScenario } = useScenario();
  const { data: advice, loading: advLoading, fetch: fetchAdvice } = useCoachAdvice();
  const { data: teamsData, fetch: fetchTeams } = useTeams();
  const [filters, setFilters] = useState<ScenarioFilters>({ down: 3, ytf_min: 7, qtr: 3 });

  useEffect(() => { fetchTeams(); }, []);
  useEffect(() => { fetchScenario(filters); }, [filters]);

  const set = (k: keyof ScenarioFilters, v: any) =>
    setFilters(prev => ({ ...prev, [k]: v === "" ? undefined : Number(v) || v }));

  const overall = data?.overall;
  const passM   = data?.by_category?.pase;
  const runM    = data?.by_category?.carrera;
  const shotM   = data?.by_shotgun?.shotgun;
  const noShotM = data?.by_shotgun?.no_shotgun;

  const bestZone = data?.by_pass_direction
    ? Object.entries(data.by_pass_direction)
        .filter(([, m]) => m.n >= 10)
        .sort((a, b) => (b[1].first_down_rate ?? 0) - (a[1].first_down_rate ?? 0))[0]?.[0]
    : undefined;

  const handleAdvice = () => {
    fetchAdvice({
      down: filters.down ?? 1,
      yards_to_first: filters.ytf_min ?? 10,
      yards_to_goal: filters.ytg_max ?? 50,
      score_diff: ((filters.score_diff_min ?? 0) + (filters.score_diff_max ?? 0)) / 2 | 0,
      qtr: filters.qtr ?? 2,
      off_team: filters.off,
      avg_yards_pass: passM?.avg_yards ?? undefined,
      avg_yards_run: runM?.avg_yards ?? undefined,
      fd_rate_shotgun: shotM?.first_down_rate ?? undefined,
      fd_rate_no_shotgun: noShotM?.first_down_rate ?? undefined,
      best_pass_zone: bestZone,
    });
  };

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-green-400">🏈 Simulador de Escenario</h2>

      {/* Filtros */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 bg-gray-900 border border-gray-700 rounded-xl p-4">
        {[
          { label: "Down", key: "down", opts: [1,2,3,4] },
          { label: "Cuarto", key: "qtr", opts: [1,2,3,4] },
        ].map(({ label, key, opts }) => (
          <div key={key}>
            <label className="text-xs text-gray-400 block mb-1">{label}</label>
            <select
              className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-sm text-white"
              value={(filters as any)[key] ?? ""}
              onChange={e => set(key as keyof ScenarioFilters, e.target.value)}
            >
              <option value="">Todos</option>
              {opts.map(o => <option key={o} value={o}>{o}</option>)}
            </select>
          </div>
        ))}

        <div>
          <label className="text-xs text-gray-400 block mb-1">YTF Mín</label>
          <input type="number" min={0} max={70}
            className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-sm text-white"
            value={filters.ytf_min ?? ""} onChange={e => set("ytf_min", e.target.value)} />
        </div>
        <div>
          <label className="text-xs text-gray-400 block mb-1">YTF Máx</label>
          <input type="number" min={0} max={70}
            className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-sm text-white"
            value={filters.ytf_max ?? ""} onChange={e => set("ytf_max", e.target.value)} />
        </div>
        <div>
          <label className="text-xs text-gray-400 block mb-1">Yardas para anotación (máx)</label>
          <input type="number" min={0} max={100}
            className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-sm text-white"
            value={filters.ytg_max ?? ""} onChange={e => set("ytg_max", e.target.value)} />
        </div>
        <div>
          <label className="text-xs text-gray-400 block mb-1">Dif. Marcador Mín</label>
          <input type="number" min={-59} max={59}
            className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-sm text-white"
            value={filters.score_diff_min ?? ""} onChange={e => set("score_diff_min", e.target.value)} />
        </div>
        <div>
          <label className="text-xs text-gray-400 block mb-1">Dif. Marcador Máx</label>
          <input type="number" min={-59} max={59}
            className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-sm text-white"
            value={filters.score_diff_max ?? ""} onChange={e => set("score_diff_max", e.target.value)} />
        </div>
        <div>
          <label className="text-xs text-gray-400 block mb-1">Equipo Ofensivo</label>
          <select
            className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-sm text-white"
            value={filters.off ?? ""} onChange={e => set("off", e.target.value || undefined)}
          >
            <option value="">Todos</option>
            {teamsData?.teams.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>
      </div>

      {/* Estado */}
      {loading && <p className="text-gray-400 text-sm">Calculando…</p>}
      {error   && <p className="text-red-400 text-sm">Error: {error}</p>}

      {/* Métricas generales */}
      {data && (
        <>
          <div className="text-sm text-gray-400">
            <strong className="text-white">{data.total.toLocaleString()}</strong> jugadas en este escenario
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <MetricCard label="Yds/jugada" value={overall?.avg_yards ?? "—"} color="green" />
            <MetricCard label="Mediana yds" value={overall?.median_yards ?? "—"} />
            <MetricCard label="Tasa 1er Down" value={overall?.first_down_rate ? `${overall.first_down_rate}%` : "—"} color="blue" />
            <MetricCard label="Tasa Turnover" value={overall?.turnover_rate ? `${overall.turnover_rate}%` : "—"} color="red" />
          </div>

          {/* Pase vs Carrera */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[["pase","Pase 🏈", passM],["carrera","Carrera 🏃", runM]].map(([key, lbl, m]: any) => m?.n > 0 && (
              <div key={key} className="bg-gray-900 border border-gray-700 rounded-xl p-4 space-y-2">
                <h3 className="text-sm font-semibold text-gray-300">{lbl}</h3>
                <div className="grid grid-cols-3 gap-2">
                  <MetricCard label="Yds" value={m.avg_yards} color="green" />
                  <MetricCard label="1er Down" value={m.first_down_rate ? `${m.first_down_rate}%` : "—"} color="blue" />
                  <MetricCard label="Turnovers" value={m.turnover_rate ? `${m.turnover_rate}%` : "—"} color="red" />
                </div>
              </div>
            ))}
          </div>

          {/* Shotgun */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[["shotgun","Shotgun ✓", shotM],["no_shotgun","Shotgun ✗", noShotM]].map(([k, lbl, m]: any) => m?.n > 0 && (
              <div key={k} className="bg-gray-900 border border-gray-700 rounded-xl p-4 space-y-2">
                <h3 className="text-sm font-semibold text-gray-300">{lbl} <span className="text-gray-500">({m.n.toLocaleString()} jugadas)</span></h3>
                <div className="grid grid-cols-3 gap-2">
                  <MetricCard label="Yds" value={m.avg_yards} color="green" />
                  <MetricCard label="1er Down" value={m.first_down_rate ? `${m.first_down_rate}%` : "—"} color="blue" />
                  <MetricCard label="Penalidad" value={m.penalty_rate ? `${m.penalty_rate}%` : "—"} color="yellow" />
                </div>
              </div>
            ))}
          </div>

          {/* Mejor zona de pase */}
          {bestZone && (
            <div className="bg-green-950 border border-green-800 rounded-xl p-4">
              <p className="text-xs text-green-400 uppercase tracking-wider mb-1">Zona de pase más eficiente en este escenario</p>
              <p className="text-lg font-bold text-white">{bestZone.replace(/_/g," ").toUpperCase()}</p>
              <p className="text-sm text-green-300">
                {data.by_pass_direction[bestZone].first_down_rate}% tasa de 1er Down ·{" "}
                {data.by_pass_direction[bestZone].avg_yards} yds/jugada
              </p>
            </div>
          )}

          {/* Botón consejo */}
          <button
            onClick={handleAdvice}
            disabled={advLoading}
            className="w-full bg-green-600 hover:bg-green-500 disabled:opacity-50 text-white font-semibold py-3 rounded-xl transition-colors"
          >
            {advLoading ? "Consultando al coach…" : "🧠 Pedir consejo al Coach"}
          </button>

          {/* Consejo */}
          {advice && (
            <div className="bg-gray-900 border border-green-700 rounded-xl p-5 space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-green-400 uppercase tracking-wider">Coach Advice</h3>
                <span className={`text-xs px-2 py-1 rounded-full ${advice.source === "strands-agents" ? "bg-blue-900 text-blue-300" : "bg-gray-800 text-gray-400"}`}>
                  {advice.source}
                </span>
              </div>
              <div className="text-sm text-gray-200 leading-relaxed whitespace-pre-wrap">{advice.advice}</div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

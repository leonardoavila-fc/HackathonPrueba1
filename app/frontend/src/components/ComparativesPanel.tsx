import { useEffect, useState } from "react";
import { useZones, useFormation, useTempo } from "../hooks/useApi";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, Legend,
  LineChart, Line, CartesianGrid, ResponsiveContainer,
} from "recharts";

const COLORS = ["#22c55e","#3b82f6","#f59e0b","#ef4444","#a855f7","#06b6d4"];

type Tab = "zones" | "formation" | "tempo";

export default function ComparativesPanel() {
  const [tab, setTab] = useState<Tab>("zones");
  const zones     = useZones();
  const formation = useFormation();
  const tempo     = useTempo();

  useEffect(() => { zones.fetch(); formation.fetch(); tempo.fetch(); }, []);

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-green-400">📊 Comparativas Tácticas</h2>

      {/* Tabs */}
      <div className="flex gap-2">
        {([["zones","A — Zonas de Pase"],["formation","B — Formación"],["tempo","C — Ritmo"]] as [Tab,string][]).map(([t,l]) => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${tab===t ? "bg-green-700 text-white" : "bg-gray-800 text-gray-400 hover:bg-gray-700"}`}>
            {l}
          </button>
        ))}
      </div>

      {/* ── Comparativa A ── */}
      {tab === "zones" && zones.data && (
        <div className="space-y-6">
          {[1,2,3,4].map(d => {
            const key = `down_${d}`;
            const down = (zones.data as any)[key];
            if (!down) return null;
            const chartData = down.zones.map(z => ({
              name: z.label, fd: z.fd_rate, avg: z.avg, to: z.to_rate, n: z.n,
            }));
            return (
              <div key={d} className="bg-gray-900 border border-gray-700 rounded-xl p-4">
                <h3 className="text-sm font-semibold text-gray-300 mb-3">
                  {d}er Down — {down.total_pass_plays.toLocaleString()} jugadas de pase
                </h3>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={chartData} margin={{ top:5, right:10, left:0, bottom:5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="name" tick={{ fill:"#9ca3af", fontSize:11 }} />
                    <YAxis tick={{ fill:"#9ca3af", fontSize:11 }} />
                    <Tooltip contentStyle={{ background:"#1f2937", border:"1px solid #374151", borderRadius:8 }} />
                    <Legend wrapperStyle={{ fontSize:12 }} />
                    <Bar dataKey="fd"  name="Conv 1er Down %" fill="#22c55e" radius={[4,4,0,0]} />
                    <Bar dataKey="avg" name="Yds Media"       fill="#3b82f6" radius={[4,4,0,0]} />
                    <Bar dataKey="to"  name="Turnover %"      fill="#ef4444" radius={[4,4,0,0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            );
          })}
        </div>
      )}

      {/* ── Comparativa B ── */}
      {tab === "formation" && formation.data && (
        <div className="space-y-6">
          {[1,3].map(d => {
            const key = `down_${d}`;
            const down = (formation.data as any)[key];
            if (!down) return null;
            const chartData = down.breakdown
              .filter(r => r.n > 50)
              .map(r => ({ name: `${r.formation} ${r.play_type}`, fd: r.fd_rate, avg: r.avg, pct: r.usage_pct }));
            return (
              <div key={d} className="bg-gray-900 border border-gray-700 rounded-xl p-4">
                <h3 className="text-sm font-semibold text-gray-300 mb-3">
                  {d}er Down — {down.total_plays.toLocaleString()} jugadas
                </h3>
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={chartData} margin={{ top:5, right:10, left:0, bottom:5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="name" tick={{ fill:"#9ca3af", fontSize:10 }} />
                    <YAxis tick={{ fill:"#9ca3af", fontSize:11 }} />
                    <Tooltip contentStyle={{ background:"#1f2937", border:"1px solid #374151", borderRadius:8 }} />
                    <Legend wrapperStyle={{ fontSize:12 }} />
                    <Bar dataKey="fd"  name="Conv 1er Down %" fill="#22c55e" radius={[4,4,0,0]} />
                    <Bar dataKey="avg" name="Yds Media"       fill="#3b82f6" radius={[4,4,0,0]} />
                    <Bar dataKey="pct" name="% Uso"           fill="#f59e0b" radius={[4,4,0,0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            );
          })}
        </div>
      )}

      {/* ── Comparativa C ── */}
      {tab === "tempo" && tempo.data && (
        <div className="space-y-4">
          {/* Line chart delta yardas */}
          <div className="bg-gray-900 border border-gray-700 rounded-xl p-4">
            <h3 className="text-sm font-semibold text-gray-300 mb-3">
              Delta Yds/jugada No Huddle vs Normal por cuarto
              <span className="text-xs text-yellow-400 ml-2">(Q4 = solo partido cerrado ≤8 pts)</span>
            </h3>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart
                data={[1,2,3,4].map(q => {
                  const qd = (tempo.data as any)[`qtr_${q}`];
                  return {
                    qtr: `Q${q}`,
                    noh: qd?.no_huddle.avg,
                    normal: qd?.normal.avg,
                    delta: qd?.delta.avg_yards,
                  };
                })}
                margin={{ top:5, right:20, left:0, bottom:5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="qtr" tick={{ fill:"#9ca3af" }} />
                <YAxis tick={{ fill:"#9ca3af", fontSize:11 }} />
                <Tooltip contentStyle={{ background:"#1f2937", border:"1px solid #374151", borderRadius:8 }} />
                <Legend wrapperStyle={{ fontSize:12 }} />
                <Line type="monotone" dataKey="noh"    name="No Huddle Yds" stroke="#22c55e" strokeWidth={2} dot={{ r:4 }} />
                <Line type="monotone" dataKey="normal" name="Normal Yds"    stroke="#3b82f6" strokeWidth={2} dot={{ r:4 }} />
                <Line type="monotone" dataKey="delta"  name="Δ Yds"         stroke="#f59e0b" strokeWidth={2} strokeDasharray="5 5" dot={{ r:4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Tabla de tasas */}
          <div className="bg-gray-900 border border-gray-700 rounded-xl overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-800">
                <tr>
                  {["Cuarto","Tipo","Yds Media","1er Down%","Penalidad%","Turnover%"].map(h => (
                    <th key={h} className="px-4 py-2 text-left text-xs text-gray-400 font-semibold uppercase">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {[1,2,3,4].flatMap(q => {
                  const qd = (tempo.data as any)[`qtr_${q}`];
                  if (!qd) return [];
                  return [
                    { qtr: `Q${q}`, tipo: "No Huddle ✓", ...qd.no_huddle, closedQ4: qd.filtered_q4_close },
                    { qtr: "",       tipo: "Normal ✗",   ...qd.normal,    closedQ4: false },
                  ];
                }).map((row, i) => (
                  <tr key={i} className={i % 4 < 2 ? "bg-gray-900" : "bg-gray-800/40"}>
                    <td className="px-4 py-2 font-mono text-gray-300">
                      {row.qtr}{row.closedQ4 && <span className="text-yellow-400 text-xs ml-1">cerrado</span>}
                    </td>
                    <td className="px-4 py-2 text-gray-300">{row.tipo}</td>
                    <td className="px-4 py-2 text-green-400">{row.avg ?? "—"}</td>
                    <td className="px-4 py-2 text-blue-400">{row.fd_rate != null ? `${row.fd_rate}%` : "—"}</td>
                    <td className="px-4 py-2 text-yellow-400">{row.pen_rate != null ? `${row.pen_rate}%` : "—"}</td>
                    <td className="px-4 py-2 text-red-400">{row.to_rate != null ? `${row.to_rate}%` : "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

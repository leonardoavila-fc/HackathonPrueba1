import { useState } from "react";
import ScenarioPanel from "./components/ScenarioPanel";
import ComparativesPanel from "./components/ComparativesPanel";

type View = "scenario" | "comparatives";

export default function App() {
  const [view, setView] = useState<View>("scenario");

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* Header */}
      <header className="bg-gray-900 border-b border-gray-800 px-6 py-4 flex items-center gap-4">
        <div className="text-2xl">🏈</div>
        <div>
          <h1 className="text-lg font-bold text-white leading-tight">NFL Coach Analytics</h1>
          <p className="text-xs text-gray-400">Play-by-Play · NFL 2002–2012 · 411K jugadas</p>
        </div>
        <nav className="ml-auto flex gap-2">
          {([["scenario","Simulador"],["comparatives","Comparativas"]] as [View,string][]).map(([v,l]) => (
            <button key={v} onClick={() => setView(v)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${view===v ? "bg-green-700 text-white" : "bg-gray-800 text-gray-300 hover:bg-gray-700"}`}>
              {l}
            </button>
          ))}
        </nav>
      </header>

      {/* Main */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        {view === "scenario"     && <ScenarioPanel />}
        {view === "comparatives" && <ComparativesPanel />}
      </main>
    </div>
  );
}

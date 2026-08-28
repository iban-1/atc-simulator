import { useEffect, useState } from "react";
import { fetchProgression, fetchScenarios, startScenario } from "../services/api.js";

export default function ScenarioSelectPage({ onScenarioStarted, onViewAnalytics }) {
  const [scenarios, setScenarios] = useState([]);
  const [progression, setProgression] = useState(null);
  const [error, setError] = useState(null);
  const [starting, setStarting] = useState(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const [scenarioList, progressionRecord] = await Promise.all([fetchScenarios(), fetchProgression()]);
        if (!cancelled) {
          setScenarios(scenarioList);
          setProgression(progressionRecord);
        }
      } catch (err) {
        if (!cancelled) setError(err.message);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  async function handleSelect(scenario) {
    if (!scenario.unlocked || starting) return;
    setStarting(scenario.id);
    setError(null);
    try {
      await startScenario(scenario.id);
      onScenarioStarted();
    } catch (err) {
      setError(err.message);
      setStarting(null);
    }
  }

  return (
    <div className="flex h-screen flex-col items-center overflow-y-auto bg-black px-6 py-10 text-zinc-200">
      <h1 className="text-2xl font-bold text-emerald-400">ATC SIMULATOR</h1>
      <p className="mb-1 text-xs uppercase tracking-widest text-zinc-500">fictional &middot; educational</p>
      <p className="mb-8 max-w-xl text-center text-sm text-zinc-400">
        Choose a scenario below. Harder scenarios unlock as you complete easier ones.
      </p>

      {progression && (
        <div className="mb-8 flex flex-wrap justify-center gap-6 rounded border border-zinc-800 bg-zinc-950 px-6 py-3 text-xs">
          <div>
            <span className="text-zinc-500">Best Score </span>
            <span className="font-mono text-emerald-400">{progression.best_score.toLocaleString()}</span>
          </div>
          <div>
            <span className="text-zinc-500">Games Played </span>
            <span className="font-mono text-zinc-200">{progression.games_played}</span>
          </div>
          <div>
            <span className="text-zinc-500">Aircraft Handled </span>
            <span className="font-mono text-zinc-200">{progression.total_aircraft_safely_handled}</span>
          </div>
          <div>
            <span className="text-zinc-500">Highest Difficulty </span>
            <span className="font-mono text-zinc-200">{progression.highest_difficulty_completed}</span>
          </div>
        </div>
      )}

      <button
        onClick={onViewAnalytics}
        className="mb-8 rounded border border-zinc-700 px-4 py-1.5 text-xs font-semibold text-zinc-300 hover:border-emerald-500 hover:text-emerald-400"
      >
        View Analytics
      </button>

      {error && <div className="mb-4 rounded bg-red-950/50 px-3 py-2 text-xs text-red-300">{error}</div>}

      <div className="grid w-full max-w-4xl grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {scenarios.map((s) => (
          <button
            key={s.id}
            onClick={() => handleSelect(s)}
            disabled={!s.unlocked}
            className={`flex flex-col rounded border p-4 text-left transition ${
              s.unlocked
                ? "border-zinc-700 bg-zinc-950 hover:border-emerald-500 hover:bg-zinc-900"
                : "cursor-not-allowed border-zinc-900 bg-zinc-950/50 opacity-50"
            }`}
          >
            <div className="mb-1 flex items-center justify-between">
              <span className="font-bold text-zinc-100">{s.name}</span>
              <span className="text-[10px] uppercase tracking-widest text-zinc-500">Lvl {s.difficulty}</span>
            </div>
            <p className="mb-2 text-xs text-zinc-400">{s.description}</p>
            <p className="mt-auto text-[11px] text-zinc-500">{s.objective_description}</p>
            {!s.unlocked && <p className="mt-2 text-[10px] font-semibold uppercase tracking-widest text-amber-500">Locked</p>}
            {starting === s.id && <p className="mt-2 text-[10px] text-emerald-400">Starting…</p>}
          </button>
        ))}
      </div>
    </div>
  );
}

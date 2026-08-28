import { useSimulation } from "../hooks/useSimulation.jsx";

export default function BottomBar() {
  const { scenario, stateUpdate, errorMessage, clearError } = useSimulation();
  const score = stateUpdate?.score;

  return (
    <footer className="border-t border-zinc-800 bg-zinc-950 px-4 py-2 text-xs">
      <div className="flex flex-wrap items-center gap-6">
        <div className="flex-1 min-w-[240px]">
          <span className="text-zinc-500">Objective: </span>
          <span className="text-zinc-300">{scenario?.objective_description ?? "—"}</span>
        </div>
        <div className="flex gap-4 font-mono text-zinc-400">
          <span>SAFE: {score?.aircraft_safe ?? 0}</span>
          <span>HANDLED: {score?.aircraft_handled ?? 0}</span>
          <span>CONFLICTS: {score?.conflicts_detected ?? 0}</span>
          <span>VIOLATIONS: {score?.separation_violations ?? 0}</span>
          <span>AVG DELAY: {(score?.average_delay_s ?? 0).toFixed(1)}s</span>
        </div>
        <div className="text-zinc-500">
          Status: <span className="text-zinc-300">{(stateUpdate?.status ?? "stopped").toUpperCase()}</span>
        </div>
      </div>
      {errorMessage && (
        <div className="mt-1 flex items-center justify-between rounded bg-red-950/50 px-2 py-1 text-red-300">
          <span>{errorMessage}</span>
          <button onClick={clearError} className="text-red-400 hover:text-red-200">
            dismiss
          </button>
        </div>
      )}
    </footer>
  );
}

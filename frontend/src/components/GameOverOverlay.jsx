import { useSimulation } from "../hooks/useSimulation.jsx";

const REASON_LABEL = {
  collision: "Simulated Collision",
  too_many_violations: "Too Many Separation Violations",
  objective_failed: "Objective Failed",
  objective_complete: "Objective Complete",
};

function rate(results) {
  const score = results.score ?? 0;
  if (results.separation_violations > 2) return "TRAINEE CONTROLLER";
  if (score >= 400) return "SENIOR CONTROLLER";
  if (score >= 150) return "CERTIFIED CONTROLLER";
  return "TRAINEE CONTROLLER";
}

export default function GameOverOverlay({ onExitToSelect }) {
  const { gameOverResult, sendSimControl } = useSimulation();
  if (!gameOverResult) return null;

  const { reason, results } = gameOverResult;

  return (
    <div className="absolute inset-0 z-20 flex items-center justify-center bg-black/80">
      <div className="w-full max-w-md rounded-lg border border-zinc-700 bg-zinc-950 p-6 text-center">
        <h2 className="mb-1 text-xl font-bold text-emerald-400">ATC PERFORMANCE</h2>
        <p className="mb-4 text-xs uppercase tracking-widest text-zinc-500">{REASON_LABEL[reason] ?? reason}</p>

        <p className="mb-4 text-3xl font-bold text-zinc-100">{(results.score ?? 0).toLocaleString()}</p>

        <div className="mb-4 grid grid-cols-2 gap-2 text-left text-xs">
          <div className="text-zinc-500">Aircraft Handled</div>
          <div className="text-right text-zinc-200">{results.aircraft_handled}</div>
          <div className="text-zinc-500">Safely Completed</div>
          <div className="text-right text-zinc-200">{results.aircraft_safe}</div>
          <div className="text-zinc-500">Conflicts</div>
          <div className="text-right text-zinc-200">{results.conflicts_detected}</div>
          <div className="text-zinc-500">Separation Violations</div>
          <div className="text-right text-zinc-200">{results.separation_violations}</div>
          <div className="text-zinc-500">Average Delay</div>
          <div className="text-right text-zinc-200">{results.average_delay_s.toFixed(1)}s</div>
        </div>

        <p className="mb-4 text-sm font-semibold tracking-wide text-amber-400">{rate(results)}</p>

        <div className="flex justify-center gap-2">
          <button
            onClick={() => sendSimControl("restart")}
            className="rounded bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-500"
          >
            Restart Scenario
          </button>
          {onExitToSelect && (
            <button
              onClick={onExitToSelect}
              className="rounded bg-zinc-800 px-4 py-2 text-sm font-semibold text-zinc-200 hover:bg-zinc-700"
            >
              Select Another Scenario
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

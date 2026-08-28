import { useSimulation } from "../hooks/useSimulation.jsx";

function formatSimTime(seconds) {
  const total = Math.floor(seconds);
  const h = String(Math.floor(total / 3600)).padStart(2, "0");
  const m = String(Math.floor((total % 3600) / 60)).padStart(2, "0");
  const s = String(total % 60).padStart(2, "0");
  return `${h}:${m}:${s}`;
}

const SPEEDS = [1, 2, 5];

export default function TopBar() {
  const { scenario, stateUpdate, connectionStatus, sendSimControl, setSpeed } = useSimulation();

  const status = stateUpdate?.status ?? "stopped";
  const score = stateUpdate?.score?.score ?? 0;
  const speedMultiplier = stateUpdate?.speed_multiplier ?? 1;

  return (
    <header className="flex items-center gap-6 border-b border-zinc-800 bg-zinc-950 px-4 py-2 text-sm">
      <div className="flex flex-col leading-tight">
        <span className="text-base font-bold tracking-wide text-emerald-400">ATC SIMULATOR</span>
        <span className="text-[10px] uppercase tracking-widest text-zinc-500">fictional &middot; educational</span>
      </div>

      <div className="flex flex-col leading-tight">
        <span className="text-zinc-500">Scenario</span>
        <span className="font-medium text-zinc-200">{scenario?.name ?? "—"}</span>
      </div>

      <div className="flex flex-col leading-tight">
        <span className="text-zinc-500">Sim Time</span>
        <span className="font-mono text-zinc-200">{formatSimTime(stateUpdate?.sim_time_s ?? 0)}</span>
      </div>

      <div className="flex flex-col leading-tight">
        <span className="text-zinc-500">Score</span>
        <span className="font-mono font-semibold text-emerald-400">{score.toLocaleString()}</span>
      </div>

      <div className="flex items-center gap-1">
        {SPEEDS.map((s) => (
          <button
            key={s}
            onClick={() => setSpeed(s)}
            className={`rounded px-2 py-1 text-xs font-semibold ${
              speedMultiplier === s ? "bg-emerald-500 text-black" : "bg-zinc-800 text-zinc-300 hover:bg-zinc-700"
            }`}
          >
            x{s}
          </button>
        ))}
      </div>

      <div className="flex items-center gap-2">
        {status !== "running" ? (
          <button
            onClick={() => sendSimControl(status === "paused" ? "resume" : "start")}
            className="rounded bg-emerald-600 px-3 py-1 text-xs font-semibold text-white hover:bg-emerald-500"
          >
            {status === "paused" ? "Resume" : "Start"}
          </button>
        ) : (
          <button
            onClick={() => sendSimControl("pause")}
            className="rounded bg-amber-600 px-3 py-1 text-xs font-semibold text-white hover:bg-amber-500"
          >
            Pause
          </button>
        )}
        <button
          onClick={() => sendSimControl("restart")}
          className="rounded bg-zinc-800 px-3 py-1 text-xs font-semibold text-zinc-200 hover:bg-zinc-700"
        >
          Restart
        </button>
      </div>

      <div className="ml-auto flex items-center gap-2 text-xs">
        <span
          className={`h-2 w-2 rounded-full ${
            connectionStatus === "open" ? "bg-emerald-400" : connectionStatus === "connecting" ? "bg-amber-400" : "bg-red-500"
          }`}
        />
        <span className="text-zinc-500">{connectionStatus === "open" ? "connected" : connectionStatus}</span>
      </div>
    </header>
  );
}

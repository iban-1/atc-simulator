import { useSimulation } from "../hooks/useSimulation.jsx";

export default function LandingSequencePanel() {
  const { stateUpdate } = useSimulation();
  const queue = stateUpdate?.landing_queue ?? [];

  if (queue.length === 0) return null;

  return (
    <div className="border-t border-zinc-800 px-3 py-2 text-xs">
      <div className="mb-1 font-semibold uppercase tracking-wide text-zinc-500">Landing Sequence</div>
      <div className="space-y-1">
        {queue.map((entry) => (
          <div key={entry.aircraft_id} className="flex justify-between">
            <span className="text-zinc-300">
              {entry.position}. {entry.callsign}
            </span>
            <span className={entry.phase === "landing" ? "text-emerald-400" : "text-amber-400"}>
              {entry.phase.toUpperCase()}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

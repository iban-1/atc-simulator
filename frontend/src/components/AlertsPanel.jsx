import { useSimulation } from "../hooks/useSimulation.jsx";

const RISK_STYLE = {
  caution: "border-amber-600/50 bg-amber-950/30 text-amber-300",
  warning: "border-orange-600/50 bg-orange-950/30 text-orange-300",
  violation: "border-red-600/50 bg-red-950/40 text-red-300",
};

export default function AlertsPanel() {
  const { stateUpdate, selectAircraft, setView } = useSimulation();
  const conflicts = stateUpdate?.conflicts ?? [];
  const aircraftById = new Map((stateUpdate?.aircraft ?? []).map((a) => [a.id, a]));

  function focusPair(w) {
    const a = aircraftById.get(w.aircraft_a);
    const b = aircraftById.get(w.aircraft_b);
    if (a && b) {
      selectAircraft(a.id);
      setView({ centerX: (a.x + b.x) / 2, centerY: (a.y + b.y) / 2 });
    }
  }

  return (
    <div className="border-t border-zinc-800">
      <div className="px-3 py-2 text-xs font-semibold uppercase tracking-wide text-zinc-500">
        Active Alerts ({conflicts.length})
      </div>
      <div className="max-h-40 space-y-1 overflow-y-auto px-2 pb-2 text-xs">
        {conflicts.length === 0 && <div className="px-1 text-zinc-600">No conflicts predicted.</div>}
        {conflicts.map((w, i) => {
          const a = aircraftById.get(w.aircraft_a);
          const b = aircraftById.get(w.aircraft_b);
          return (
            <button
              key={i}
              onClick={() => focusPair(w)}
              className={`block w-full rounded border px-2 py-1 text-left ${RISK_STYLE[w.risk_level]}`}
            >
              <div className="font-semibold">
                {w.is_active_violation ? "⚠ CONFLICT — SEPARATION VIOLATION" : "⚠ CONFLICT PREDICTED"}
              </div>
              <div>
                {a?.callsign ?? w.aircraft_a} ↔ {b?.callsign ?? w.aircraft_b}
              </div>
              <div className="text-[11px] opacity-80">
                Time to conflict: {Math.round(w.time_to_conflict_s)}s &middot; Sep:{" "}
                {w.predicted_separation_nm.toFixed(1)} NM &middot; Vert: {Math.round(w.vertical_separation_ft)} ft
              </div>
              <div className="text-[11px] font-semibold uppercase">Risk: {w.risk_level}</div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

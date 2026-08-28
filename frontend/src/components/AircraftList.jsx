import { useSimulation } from "../hooks/useSimulation.jsx";
import AircraftSearch from "./AircraftSearch.jsx";

const STATUS_COLOR = {
  none: "text-zinc-400",
  caution: "text-amber-400",
  warning: "text-red-400",
};

export default function AircraftList() {
  const { stateUpdate, selectedAircraftId, selectAircraft } = useSimulation();
  const aircraft = stateUpdate?.aircraft ?? [];

  return (
    <div className="flex h-full flex-col border-r border-zinc-800 bg-zinc-950">
      <div className="border-b border-zinc-800 px-3 py-2 text-xs font-semibold uppercase tracking-wide text-zinc-500">
        Aircraft ({aircraft.length})
      </div>
      <AircraftSearch />
      <div className="flex-1 overflow-y-auto">
        {aircraft.length === 0 && <div className="px-3 py-4 text-xs text-zinc-600">No aircraft in airspace.</div>}
        {aircraft.map((ac) => (
          <button
            key={ac.id}
            onClick={() => selectAircraft(ac.id)}
            className={`block w-full border-b border-zinc-900 px-3 py-2 text-left text-xs hover:bg-zinc-900 ${
              selectedAircraftId === ac.id ? "bg-zinc-900" : ""
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="font-semibold text-zinc-100">
                {ac.emergency && <span className="mr-1 text-red-500">⚠</span>}
                {ac.callsign}
              </span>
              <span className={`uppercase ${STATUS_COLOR[ac.conflict_status]}`}>{ac.conflict_status}</span>
            </div>
            <div className="mt-0.5 flex justify-between text-zinc-500">
              <span>{ac.aircraft_type}</span>
              <span>FL{Math.round(ac.altitude_ft / 100)}</span>
              <span>{Math.round(ac.speed_kt)} kt</span>
            </div>
            <div className={ac.emergency ? "text-red-400" : "text-zinc-600"}>{ac.phase.toUpperCase()}</div>
          </button>
        ))}
      </div>
    </div>
  );
}

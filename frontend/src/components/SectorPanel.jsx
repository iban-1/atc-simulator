import { useSimulation } from "../hooks/useSimulation.jsx";

const DENSITY_COLOR = {
  low: "text-emerald-400",
  medium: "text-amber-400",
  high: "text-red-400",
};

export default function SectorPanel() {
  const { stateUpdate } = useSimulation();
  const sectorList = stateUpdate?.sectors ?? [];

  if (sectorList.length === 0) return null;

  return (
    <div className="border-t border-zinc-800 px-3 py-2 text-xs">
      <div className="mb-1 font-semibold uppercase tracking-wide text-zinc-500">Sectors</div>
      <div className="space-y-1">
        {sectorList.map((s) => (
          <div key={s.id} className="flex justify-between">
            <span className="text-zinc-300">{s.name}</span>
            <span className={DENSITY_COLOR[s.density]}>
              {s.aircraft_count} &middot; {s.density.toUpperCase()}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

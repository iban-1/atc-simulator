import { useState } from "react";
import { useSimulation } from "../hooks/useSimulation.jsx";

export default function AircraftSearch() {
  const { stateUpdate, selectAircraft, setView } = useSimulation();
  const [query, setQuery] = useState("");
  const [notFound, setNotFound] = useState(false);

  function handleSearch(e) {
    e.preventDefault();
    const term = query.trim().toUpperCase();
    if (!term) return;
    const aircraft = (stateUpdate?.aircraft ?? []).find((a) => a.callsign.toUpperCase().includes(term));
    if (aircraft) {
      selectAircraft(aircraft.id);
      setView({ centerX: aircraft.x, centerY: aircraft.y });
      setNotFound(false);
    } else {
      setNotFound(true);
    }
  }

  return (
    <form onSubmit={handleSearch} className="flex gap-1 p-2">
      <input
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          setNotFound(false);
        }}
        placeholder="Search callsign…"
        className="w-full rounded border border-zinc-700 bg-zinc-900 px-2 py-1 text-xs text-zinc-200 placeholder-zinc-600 focus:border-emerald-500 focus:outline-none"
      />
      <button
        type="submit"
        className="rounded bg-zinc-800 px-2 py-1 text-xs text-zinc-300 hover:bg-zinc-700"
      >
        Go
      </button>
      {notFound && <span className="self-center text-xs text-red-400">not found</span>}
    </form>
  );
}

import { useSimulation } from "../hooks/useSimulation.jsx";

function Row({ label, value }) {
  return (
    <div className="flex justify-between border-b border-zinc-900 py-1">
      <span className="text-zinc-500">{label}</span>
      <span className="font-mono text-zinc-200">{value}</span>
    </div>
  );
}

export default function SelectedAircraftInfo() {
  const { stateUpdate, waypoints, selectedAircraftId } = useSimulation();
  const aircraft = (stateUpdate?.aircraft ?? []).find((a) => a.id === selectedAircraftId);

  if (!aircraft) {
    return <div className="p-3 text-xs text-zinc-600">Select an aircraft on the radar or list.</div>;
  }

  const destName = waypoints.find((w) => w.id === aircraft.destination)?.name ?? aircraft.destination;
  const currentWpId = aircraft.route[aircraft.route_index];
  const currentWpName = waypoints.find((w) => w.id === currentWpId)?.name ?? "—";

  return (
    <div className="p-3 text-xs">
      <div className="mb-2 flex items-baseline justify-between">
        <span className="text-lg font-bold text-emerald-400">{aircraft.callsign}</span>
        <span className="text-zinc-500">{aircraft.aircraft_type}</span>
      </div>
      {aircraft.emergency && (
        <div className="mb-2 rounded border border-red-700/50 bg-red-950/40 px-2 py-1 text-[11px] text-red-300">
          ⚠ {aircraft.emergency.message}
        </div>
      )}
      <Row label="Altitude" value={`FL${Math.round(aircraft.altitude_ft / 100)} (${Math.round(aircraft.altitude_ft)} ft)`} />
      <Row label="Speed" value={`${Math.round(aircraft.speed_kt)} kt`} />
      <Row label="Heading" value={`${Math.round(aircraft.heading_deg)}°`} />
      <Row label="Vertical Speed" value={`${Math.round(aircraft.vertical_speed_fpm)} fpm`} />
      <Row label="Origin" value={aircraft.origin} />
      <Row label="Destination" value={destName} />
      <Row label="Current Waypoint" value={currentWpName} />
      <Row label="Distance to Dest" value={`${aircraft.distance_to_destination_nm.toFixed(1)} NM`} />
      <Row label="ETA" value={aircraft.eta_minutes != null ? `${aircraft.eta_minutes.toFixed(1)} min` : "—"} />
      <Row label="Status" value={aircraft.phase.toUpperCase()} />
      <Row label="Conflict Status" value={aircraft.conflict_status.toUpperCase()} />
      {aircraft.assigned_runway && <Row label="Assigned Runway" value={aircraft.assigned_runway} />}
    </div>
  );
}

import { useState } from "react";
import { useSimulation } from "../hooks/useSimulation.jsx";

export default function CommandPanel() {
  const { stateUpdate, waypoints, routes, scenario, selectedAircraftId, sendCommand } = useSimulation();
  const aircraft = (stateUpdate?.aircraft ?? []).find((a) => a.id === selectedAircraftId);

  const [headingInput, setHeadingInput] = useState("");
  const [altitudeInput, setAltitudeInput] = useState("");
  const [speedInput, setSpeedInput] = useState("");

  if (!aircraft) {
    return <div className="p-3 text-xs text-zinc-600">No aircraft selected.</div>;
  }

  const send = (command) => sendCommand(aircraft.id, command);

  return (
    <div className="space-y-4 p-3 text-xs">
      <section>
        <h3 className="mb-1 font-semibold uppercase tracking-wide text-zinc-500">
          Heading — target {Math.round(aircraft.target_heading_deg)}°
        </h3>
        <div className="flex items-center gap-1">
          <button
            className="rounded bg-zinc-800 px-2 py-1 hover:bg-zinc-700"
            onClick={() => send({ kind: "heading", value: (aircraft.target_heading_deg + 350) % 360 })}
          >
            ⟲ L10
          </button>
          <button
            className="rounded bg-zinc-800 px-2 py-1 hover:bg-zinc-700"
            onClick={() => send({ kind: "heading", value: (aircraft.target_heading_deg + 10) % 360 })}
          >
            R10 ⟳
          </button>
          <input
            value={headingInput}
            onChange={(e) => setHeadingInput(e.target.value)}
            placeholder="deg"
            className="w-16 rounded border border-zinc-700 bg-zinc-900 px-1 py-1 text-zinc-200 focus:border-emerald-500 focus:outline-none"
          />
          <button
            className="rounded bg-emerald-700 px-2 py-1 text-white hover:bg-emerald-600"
            onClick={() => {
              const v = Number(headingInput);
              if (!Number.isNaN(v) && v >= 0 && v < 360) send({ kind: "heading", value: v });
            }}
          >
            Set
          </button>
        </div>
      </section>

      <section>
        <h3 className="mb-1 font-semibold uppercase tracking-wide text-zinc-500">
          Altitude — target FL{Math.round(aircraft.target_altitude_ft / 100)}
        </h3>
        <div className="flex items-center gap-1">
          <button
            className="rounded bg-zinc-800 px-2 py-1 hover:bg-zinc-700"
            onClick={() => send({ kind: "altitude", value: Math.max(0, aircraft.target_altitude_ft - 2000) })}
          >
            ↓ Descend
          </button>
          <button
            className="rounded bg-zinc-800 px-2 py-1 hover:bg-zinc-700"
            onClick={() => send({ kind: "altitude", value: Math.min(45000, aircraft.target_altitude_ft + 2000) })}
          >
            ↑ Climb
          </button>
          <input
            value={altitudeInput}
            onChange={(e) => setAltitudeInput(e.target.value)}
            placeholder="ft"
            className="w-16 rounded border border-zinc-700 bg-zinc-900 px-1 py-1 text-zinc-200 focus:border-emerald-500 focus:outline-none"
          />
          <button
            className="rounded bg-emerald-700 px-2 py-1 text-white hover:bg-emerald-600"
            onClick={() => {
              const v = Number(altitudeInput);
              if (!Number.isNaN(v) && v >= 0 && v <= 45000) send({ kind: "altitude", value: v });
            }}
          >
            Set
          </button>
        </div>
      </section>

      <section>
        <h3 className="mb-1 font-semibold uppercase tracking-wide text-zinc-500">
          Speed — target {Math.round(aircraft.target_speed_kt)} kt
        </h3>
        <div className="flex items-center gap-1">
          <button
            className="rounded bg-zinc-800 px-2 py-1 hover:bg-zinc-700"
            onClick={() => send({ kind: "speed", value: Math.max(100, aircraft.target_speed_kt - 20) })}
          >
            − Slower
          </button>
          <button
            className="rounded bg-zinc-800 px-2 py-1 hover:bg-zinc-700"
            onClick={() => send({ kind: "speed", value: Math.min(600, aircraft.target_speed_kt + 20) })}
          >
            + Faster
          </button>
          <input
            value={speedInput}
            onChange={(e) => setSpeedInput(e.target.value)}
            placeholder="kt"
            className="w-16 rounded border border-zinc-700 bg-zinc-900 px-1 py-1 text-zinc-200 focus:border-emerald-500 focus:outline-none"
          />
          <button
            className="rounded bg-emerald-700 px-2 py-1 text-white hover:bg-emerald-600"
            onClick={() => {
              const v = Number(speedInput);
              if (!Number.isNaN(v) && v >= 100 && v <= 600) send({ kind: "speed", value: v });
            }}
          >
            Set
          </button>
        </div>
      </section>

      <section>
        <h3 className="mb-1 font-semibold uppercase tracking-wide text-zinc-500">Route</h3>
        <div className="flex flex-wrap gap-1">
          {waypoints.map((wp) => (
            <button
              key={wp.id}
              onClick={() => send({ kind: "route", waypoint_id: wp.id })}
              className="rounded bg-zinc-800 px-2 py-1 hover:bg-zinc-700"
            >
              Direct {wp.name}
            </button>
          ))}
        </div>
        {routes.length > 0 && (
          <div className="mt-1 text-zinc-600">
            Current route: {aircraft.route.map((id) => waypoints.find((w) => w.id === id)?.name ?? id).join(" → ")}
          </div>
        )}
      </section>

      {aircraft.phase === "approach" && (
        <section>
          <h3 className="mb-1 font-semibold uppercase tracking-wide text-amber-400">Landing Clearance</h3>
          <div className="flex flex-wrap gap-1">
            {(scenario?.runways ?? [])
              .filter((rw) => rw.airport_id === aircraft.destination)
              .map((rw) => (
                <button
                  key={rw.id}
                  onClick={() => send({ kind: "land", runway_id: rw.id })}
                  className="rounded bg-emerald-700 px-2 py-1 text-white hover:bg-emerald-600"
                >
                  Clear to Land — {rw.name}
                </button>
              ))}
          </div>
        </section>
      )}
    </div>
  );
}

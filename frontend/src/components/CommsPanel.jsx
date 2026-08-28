import { useSimulation } from "../hooks/useSimulation.jsx";

export default function CommsPanel() {
  const { stateUpdate, commsLog, approveRequest, denyRequest } = useSimulation();
  const pending = stateUpdate?.pending_requests ?? [];

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-zinc-800 px-3 py-2 text-xs font-semibold uppercase tracking-wide text-zinc-500">
        Pilot Communications
      </div>

      {pending.length > 0 && (
        <div className="border-b border-zinc-800 bg-zinc-900/50 p-2">
          {pending.map((req) => (
            <div key={req.id} className="mb-2 rounded border border-amber-700/50 bg-amber-950/30 p-2 text-xs last:mb-0">
              <div className="mb-1 text-amber-300">PILOT: {req.message}</div>
              <div className="flex gap-1">
                <button
                  onClick={() => approveRequest(req.id)}
                  className="rounded bg-emerald-700 px-2 py-0.5 text-white hover:bg-emerald-600"
                >
                  Approve
                </button>
                <button
                  onClick={() => denyRequest(req.id)}
                  className="rounded bg-zinc-700 px-2 py-0.5 text-zinc-200 hover:bg-zinc-600"
                >
                  Deny
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="flex-1 space-y-1 overflow-y-auto p-2 text-xs">
        {commsLog.length === 0 && <div className="text-zinc-600">No communications yet.</div>}
        {[...commsLog].reverse().map((msg) => (
          <div key={msg.id} className={`border-b pb-1 ${msg.kind === "pilot_report" ? "border-red-900/50" : "border-zinc-900"}`}>
            <span className={`font-semibold ${msg.kind === "pilot_report" ? "text-red-400" : "text-emerald-400"}`}>
              {msg.kind === "pilot_report" ? "⚠ " : ""}
              {msg.from}:
            </span>{" "}
            <span className={msg.kind === "pilot_report" ? "text-red-200" : "text-zinc-300"}>{msg.text}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

# ATC Simulator — Project Context

## What this is
A fictional, educational Air Traffic Control simulator game — a portfolio project, not a real ATC system. The player controls simulated aircraft on a radar, issues commands (heading/altitude/speed/route), responds to pilot requests, and avoids conflicts. All callsigns, airports, routes, and separation rules are entirely fictional game mechanics — never present them as real aviation data or standards.

## Tech stack
- **Backend**: Python, FastAPI, WebSockets (real-time sim → frontend), NumPy, Pandas
- **Frontend**: React + Vite, Tailwind CSS, HTML Canvas or SVG for the radar, Recharts for stats

## Folder structure
```
atc-simulator/
├── backend/
│   ├── app/
│   │   ├── api/          # REST endpoints
│   │   ├── models/       # Aircraft, waypoint, sector data models
│   │   ├── simulation/   # Core sim loop, physics/movement
│   │   ├── services/     # Supporting logic
│   │   ├── game/         # Scoring, game-over conditions, progression
│   │   ├── conflict/     # Conflict prediction & detection
│   │   ├── scenarios/    # Scenario/difficulty definitions
│   │   ├── websocket/    # WS connection + message handling
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # Radar, aircraft list, command panel, comms panel, alerts
│   │   ├── pages/
│   │   ├── hooks/        # WebSocket hook, etc.
│   │   ├── services/
│   │   └── App.jsx
│   └── package.json
├── data/simulated/
├── README.md
└── .env.example
```

## Build order — follow this strictly, do not skip ahead
This project is being built in phases. Do not attempt to implement later phases until the current phase is confirmed working and played end-to-end.

1. **Core loop (current phase)**: radar rendering (aircraft, trails, range rings, compass), one working scenario, aircraft movement/physics, selection + command panel (heading/altitude/speed/route), pilot request generation, conflict detection with warnings, basic scoring, WebSocket real-time sync, start/pause/resume/restart, sim speed x1/x2/x5.
2. **Breadth**: remaining difficulty levels, all 6 scenarios, airspace sectors, emergency events, arrivals/departures + landing sequences, progression tracking.
3. **Finish**: full test suite (movement, heading/altitude/speed changes, distance calcs, conflict detection/prediction, route following, scoring, scenario generation, game-over conditions), analytics screen, polished README with disclaimer, full pass for broken imports/paths/API mismatches/WebSocket bugs.

## Conventions
- No real aviation data, no real airport/callsign names — fictional only.
- No hardcoded secrets or API keys — use `.env` / `.env.example`.
- No placeholder/TODO functionality — every system must actually work end-to-end before moving on.
- Clearly label separation rules and emergencies as fictional game mechanics, not real standards.
- Aircraft must genuinely respond to commands (real trajectory changes), not cosmetic-only state changes.

## Running it
- Backend: `cd backend && uvicorn app.main:app --reload`
- Frontend: `cd frontend && npm run dev`

## Testing
- Backend: pytest in `backend/tests/`
- Run tests before considering any phase "done"

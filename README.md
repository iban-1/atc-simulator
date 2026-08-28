# ATC Simulator

A fictional, educational air traffic control simulator. You are the controller: watch aircraft on a radar, issue heading/altitude/speed/route instructions, respond to pilot requests, sequence arrivals onto a runway, and keep everyone separated as traffic builds from a quiet single-scenario sector up to a 30+ aircraft rush hour.

> **Educational disclaimer** — This is a portfolio/learning project, not a real ATC system. Every callsign, airport, waypoint, route, separation rule, and emergency procedure in this project is **entirely fictional** and simplified for gameplay. Nothing here should be used, referenced, or relied on for real aviation operations, training, or decision-making.

---

## Contents

- [Gameplay](#gameplay)
- [Features](#features)
- [Screenshots](#screenshots)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Simulation Engine](#simulation-engine)
- [Conflict Detection](#conflict-detection)
- [Scoring System](#scoring-system)
- [Installation](#installation)
- [Running the Backend](#running-the-backend)
- [Running the Frontend](#running-the-frontend)
- [Game Instructions](#game-instructions)
- [Testing](#testing)
- [Future Improvements](#future-improvements)

## Gameplay

Aircraft spawn at the edge of your airspace and fly pre-assigned routes toward a destination — usually an airport. You:

1. Watch them move in real time on the radar.
2. Get live conflict warnings before two aircraft actually get too close.
3. Issue commands (turn, climb/descend, speed up/slow down, direct-to-waypoint) to keep things safe and efficient.
4. Respond to pilot requests (descent, direct routing, speed changes) via the comms panel — approving one actually executes the underlying command.
5. Clear arriving aircraft to land once they're established on approach, respecting a minimum runway-spacing rule.
6. Handle simulated in-flight emergencies on harder scenarios.
7. Get scored on how safely and efficiently you handled the session, and see your results on a performance summary when the game ends.

## Features

- Real-time radar (HTML canvas) with range rings, compass, airspace boundary, waypoints, aircraft trails, routes, and sector overlays — pan, zoom, and click-to-select.
- Six scenarios spanning difficulty 1–5: Quiet Airspace, Normal Traffic, Busy Airspace, Heavy Traffic, Conflict Challenge, and Emergency Challenge — each with its own traffic density, route layout, and objective.
- A scenario select screen with a difficulty-gated unlock system (finish an easier scenario to unlock the next).
- Full heading/altitude/speed/route command panel, with commands producing genuine, physically-bounded trajectory changes (turns, climbs, and acceleration all happen gradually, not instantly).
- Dynamic pilot request generation with one-click approve/deny that actually drives the aircraft.
- Continuous conflict prediction (not just reactive detection) with lead time to react, shown as caution/warning/violation alerts.
- Airspace sectors with live aircraft-count and traffic-density readouts.
- Five simulated emergency event types (altitude control loss, priority landing, abnormal speed, runway unavailable, route deviation), all clearly labeled as fictional game mechanics.
- Simplified arrivals: an aircraft must be cleared to land once established on approach, with a minimum landing-spacing rule enforced.
- A scoring system that rewards safe handling and penalizes violations, excursions, and collisions, plus a results/game-over screen with a controller rating.
- Backend-persisted progression (best score, highest difficulty completed, aircraft handled, play time, conflicts avoided) that gates scenario unlocks.
- An analytics screen (Recharts) showing score history, aircraft handled, conflict history, average delay, and performance by scenario across your play history.
- start/pause/resume/restart controls and x1/x2/x5 simulation speed.

## Screenshots

_Add screenshots or a short GIF of the radar in action here before publishing — e.g. the scenario select screen, a mid-game radar view with an active conflict alert, and the game-over results screen._

## Architecture

```
atc-simulator/
├── backend/
│   ├── app/
│   │   ├── api/          # REST endpoints (scenarios, progression, health)
│   │   ├── models/       # Pydantic models: aircraft, waypoint, route, scenario, messages...
│   │   ├── simulation/   # Tick loop, physics, geometry, sectors, landing sequencing
│   │   ├── services/     # Pilot requests, emergencies, progression persistence
│   │   ├── game/         # Scoring and game-over rules
│   │   ├── conflict/     # Conflict prediction (closest point of approach)
│   │   ├── scenarios/    # The six scenario definitions + registry
│   │   ├── websocket/    # Connection manager + message handling
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # Radar, aircraft list, command panel, comms, alerts, sectors...
│   │   ├── pages/        # Scenario select, game, analytics
│   │   ├── hooks/        # WebSocket connection + simulation state context
│   │   ├── services/     # REST client, radar coordinate transforms
│   │   └── App.jsx
│   └── package.json
├── data/simulated/       # Backend-persisted progression.json (gitignored)
├── README.md
└── .env.example
```

The frontend is a thin, server-authoritative renderer: the backend simulation engine is the single source of truth, and the browser only ever displays the latest state it was sent and sends back command intents — it never predicts or fabricates outcomes locally.

## Tech Stack

**Backend:** Python, FastAPI, WebSockets, NumPy, Pandas, Pydantic
**Frontend:** React, Vite, Tailwind CSS, HTML Canvas (radar), Recharts (analytics)

## Simulation Engine

The airspace is modeled as a flat 2D Cartesian plane in nautical miles (not real lat/lon) — `x` is East(+)/West(-), `y` is North(+)/South(-), headings are standard aviation degrees (0 = North, 90 = East). This keeps the math simple (plain Euclidean distance, no map projection) while mapping directly onto the radar canvas with a single scale/pan transform.

A single `SimulationEngine` instance holds all aircraft and ticks on a fixed real-time interval. Each tick:

1. Any active emergency effects are applied (target drift, etc.).
2. Every aircraft is stepped: heading turns toward its target at a fixed turn rate, altitude and speed ease toward their targets at fixed climb/accel rates, and position is integrated from the resulting heading and speed — commands only ever set *targets*, so every trajectory change is gradual and physically bounded, never an instant jump.
3. Aircraft near their destination airport (if it has a runway) enter an APPROACH phase and wait for a landing clearance; otherwise they exit the sector once they reach their destination or leave the boundary.
4. Conflict detection, scoring, pilot-request generation, sector occupancy, and the landing queue are recomputed.
5. New aircraft spawn according to the scenario's cadence, and game-over conditions are checked.

The frontend receives the full aircraft/conflict/score snapshot every tick over a WebSocket and renders it — no client-side physics simulation.

## Conflict Detection

Conflict prediction uses a classic closest-point-of-approach (CPA) calculation: given each aircraft's position and velocity vector, the relative velocity between a pair determines the time at which their separation would be smallest, and what that separation would be. Pairs already vertically separated by the (fictional) minimum are skipped; the rest are flagged as `caution`, `warning`, or an active `violation` depending on how close and how soon.

**All separation minimums, lookahead windows, and lead times used here are simplified, fictional game-balance numbers — not real-world separation standards.** The system only ever predicts and displays conflicts; it never resolves them automatically, so the player always has to make the call.

## Scoring System

Points are simplified, fictional game mechanics documented directly in `backend/app/game/scoring.py`:

| Event | Points |
|---|---|
| Aircraft exits cleanly (or lands) without ever violating separation | +50 |
| Pilot request approved | +10 |
| New separation-violation episode begins (once per episode, not per tick) | −100 |
| Aircraft exits the airspace without reaching its destination | −25 |

Game-over triggers on a simulated collision (two aircraft violating separation at very close range), too many separation-violation episodes, or reaching the scenario's aircraft target (with a different outcome depending on whether all of them were handled safely). The results screen shows the final score, aircraft handled/safe, conflicts, violations, average delay, and a controller rating.

## Installation

Requires Python 3.11+ and Node 18+.

```bash
git clone <this-repo>
cd atc-simulator
cp .env.example .env   # adjust ports/origins if needed
```

## Running the Backend

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate   # .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API and WebSocket server run on `http://localhost:8000` by default (`GET /api/health` should return `{"status": "ok"}`).

## Running the Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. It connects to the backend over `VITE_WS_URL`/`VITE_API_URL` (see `.env.example`).

## Game Instructions

1. Pick a scenario on the select screen — harder ones unlock as you complete easier ones.
2. Click **Start**. Aircraft will begin appearing on the radar.
3. Click an aircraft (on the radar or in the left list) to select it and open the command panel.
4. Use **Heading** (turn buttons or set an exact heading), **Altitude** (climb/descend or set a target), **Speed** (faster/slower or set a target), and **Route** (direct-to-waypoint) to manage traffic. Changes happen gradually, not instantly.
5. Watch the **Active Alerts** panel for predicted conflicts — the earlier you act, the more separation you keep.
6. Respond to pilot requests in the **Pilot Communications** panel — Approve executes the request's underlying command.
7. Once an aircraft reaches an airport with a runway, it enters **APPROACH**; use the **Clear to Land** button that appears in the command panel (respecting the minimum spacing between landings).
8. On harder scenarios, watch for red-flagged aircraft — those have an active simulated emergency; the matching command (heading/altitude/speed) clears it.
9. Use the speed buttons (x1/x2/x5) and pause/restart as needed. The game ends on a collision, too many violations, or once the scenario's aircraft target is reached — then you can restart or pick another scenario.
10. Check the **Analytics** screen (from the scenario select page) to see your history across games.

## Testing

Backend:

```bash
cd backend
pytest
```

Covers movement/physics, heading/altitude/speed command behavior, route following, distance/bearing/geometry calculations, conflict detection and prediction, scoring rules, scenario generation (registry integrity), game-over conditions, and simulation engine command handling.

Frontend (build check — this is a UI-heavy project without a component test harness, so the primary frontend check is a clean production build plus manual/scripted playtesting):

```bash
cd frontend
npm run build
```

## Future Improvements

- Full multi-runway approach patterns and staggered sequencing (today's landing model is intentionally simplified: one runway per airport, a basic minimum-spacing rule).
- Persist analytics history in a real database instead of a JSON file, and support multiple player profiles.
- Client-side interpolation between server ticks for smoother aircraft motion at high zoom.
- Multiplayer/shared-airspace sessions.
- Additional emergency variety and scenario editor for custom traffic layouts.

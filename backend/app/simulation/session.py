import asyncio

from app.models.progression import ProgressionRecord
from app.scenarios.registry import get_scenario
from app.services.progression_store import record_game_result, save_progression
from app.simulation.engine import SimulationEngine
from app.websocket.connection_manager import ConnectionManager


class SimulationSession:
    """Holds the single sim engine instance plus the WS broadcast loop."""

    def __init__(self, progression: ProgressionRecord, scenario_id: str = "quiet-airspace"):
        self.engine = SimulationEngine(_require_scenario(scenario_id))
        self.manager = ConnectionManager()
        self.progression = progression
        self._comms_sent = 0
        self._game_over_sent = False

    def set_scenario(self, scenario_id: str) -> None:
        self.engine = SimulationEngine(_require_scenario(scenario_id))
        self._comms_sent = 0
        self._game_over_sent = False

    def build_state_update(self) -> dict:
        e = self.engine
        return {
            "type": "state_update",
            "tick": e.tick_count,
            "sim_time_s": e.sim_time_s,
            "status": e.status,
            "speed_multiplier": e.speed_multiplier,
            "aircraft": [a.model_dump(mode="json") for a in e.aircraft.values()],
            "conflicts": [c.model_dump(mode="json") for c in e.conflicts],
            "score": e.score_tracker.state.model_dump(mode="json"),
            "pending_requests": [r.model_dump(mode="json") for r in e.pending_requests.values()],
            "sectors": [s.model_dump(mode="json") for s in e.sectors_status],
            "landing_queue": [q.model_dump(mode="json") for q in e.landing_queue],
        }

    def build_full_snapshot(self) -> dict:
        e = self.engine
        return {
            "type": "full_snapshot",
            "scenario": e.scenario.model_dump(mode="json"),
            "waypoints": [w.model_dump(mode="json") for w in e.waypoints.values()],
            "routes": [r.model_dump(mode="json") for r in e.routes.values()],
            "airspace_bounds": list(e.scenario.airspace_bounds),
            "state_update": self.build_state_update(),
        }

    async def run_forever(self, tick_interval_s: float) -> None:
        while True:
            await asyncio.sleep(tick_interval_s)
            self.engine.tick()
            await self._broadcast_new_comms()
            await self.manager.broadcast(self.build_state_update())
            await self._broadcast_game_over_if_needed()

    async def _broadcast_new_comms(self) -> None:
        log = self.engine.comms_log
        while self._comms_sent < len(log):
            msg = log[self._comms_sent]
            await self.manager.broadcast({"type": "comms_message", "message": msg.model_dump(mode="json", by_alias=True)})
            self._comms_sent += 1

    async def _broadcast_game_over_if_needed(self) -> None:
        if self.engine.game_over is not None and not self._game_over_sent:
            self._game_over_sent = True
            self.engine.status = "stopped"
            self._persist_progression()
            await self.manager.broadcast(
                {
                    "type": "game_over",
                    "reason": self.engine.game_over.reason,
                    "results": self.engine.game_over.results.model_dump(mode="json"),
                }
            )

    def _persist_progression(self) -> None:
        state = self.engine.score_tracker.state
        conflicts_avoided = max(0, state.conflicts_detected - state.separation_violations)
        objective_completed = self.engine.game_over.reason == "objective_complete"
        record_game_result(
            self.progression,
            score=state.score,
            scenario_id=self.engine.scenario.id,
            scenario_name=self.engine.scenario.name,
            difficulty=self.engine.scenario.difficulty,
            aircraft_handled=state.aircraft_handled,
            aircraft_safe=state.aircraft_safe,
            conflicts_detected=state.conflicts_detected,
            separation_violations=state.separation_violations,
            average_delay_s=state.average_delay_s,
            conflicts_avoided=conflicts_avoided,
            play_time_s=self.engine.sim_time_s,
            objective_completed=objective_completed,
        )
        save_progression(self.progression)


def _require_scenario(scenario_id: str):
    scenario = get_scenario(scenario_id)
    if scenario is None:
        raise ValueError(f"Unknown scenario: {scenario_id}")
    return scenario

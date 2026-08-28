import random
import uuid

from app.conflict.detector import detect_conflicts
from app.game.game_over import GameOverResult, check_game_over
from app.game.scoring import ScoreTracker
from app.models.aircraft import (
    Aircraft,
    AltitudeCommand,
    Command,
    ConflictStatus,
    FlightPhase,
    HeadingCommand,
    LandCommand,
    RouteCommand,
    SpeedCommand,
)
from app.models.emergency import EmergencyType
from app.models.messages import CommsMessage, ConflictWarning, LandingQueueEntry, PilotRequest, SectorStatus
from app.models.scenario import ScenarioConfig
from app.models.waypoint import Waypoint
from app.services import emergencies, pilot_requests
from app.simulation import landing, movement, sectors
from app.simulation.callsigns import generate_aircraft_type, generate_callsign, reset_callsign_pool
from app.simulation.constants import DESTINATION_EXIT_RADIUS_NM, LANDING_GRACE_TICKS, TICK_SECONDS
from app.simulation.geometry import bearing_to, distance_xy
from app.simulation.landing import RunwayState

CRUISE_ALTITUDES = [18000.0, 22000.0, 26000.0, 30000.0]
CRUISE_SPEED_KT = 420.0
EXIT_GRACE_TICKS = 3  # keeps an EXITING aircraft visible briefly so its trail can fade on the radar

CORRECTING_COMMAND_EMERGENCY = {
    HeadingCommand: EmergencyType.ROUTE_DEVIATION,
    AltitudeCommand: EmergencyType.ALTITUDE_CONTROL_LOSS,
    SpeedCommand: EmergencyType.ABNORMAL_SPEED,
}


class SimulationEngine:
    def __init__(self, scenario: ScenarioConfig):
        self.scenario = scenario
        self.waypoints: dict[str, Waypoint] = {wp.id: wp for wp in scenario.waypoints}
        self.routes = {r.id: r for r in scenario.routes}

        self.runways = landing.runways_by_id(scenario.runways)
        self.airport_ids_with_runways = landing.airports_with_runways(scenario.runways)
        self.runway_state = RunwayState()

        self.aircraft: dict[str, Aircraft] = {}
        self.tick_count = 0
        self.sim_time_s = 0.0
        self.speed_multiplier = 1
        self.status = "stopped"

        self.score_tracker = ScoreTracker()
        self.conflicts: list[ConflictWarning] = []
        self.comms_log: list[CommsMessage] = []
        self.pending_requests: dict[str, PilotRequest] = {}
        self.sectors_status: list[SectorStatus] = []
        self.landing_queue: list[LandingQueueEntry] = []

        self._last_request_time: dict[str, float] = {}
        self._last_emergency_time: dict[str, float] = {}
        self._last_runway_emergency_time: dict[str, float] = {}
        self._exit_countdown: dict[str, int] = {}
        self._spawn_sim_time: dict[str, float] = {}
        self._expected_duration_s: dict[str, float] = {}

        self._spawned_count = 0
        self._route_cycle = list(self.routes.keys())
        self._route_cycle_index = 0
        self._next_spawn_time = 0.0

        self.game_over: GameOverResult | None = None

    # --- sim controls ---

    def start(self) -> None:
        if self.status == "stopped":
            self._reset_state()
        self.status = "running"

    def pause(self) -> None:
        if self.status == "running":
            self.status = "paused"

    def resume(self) -> None:
        if self.status == "paused":
            self.status = "running"

    def restart(self) -> None:
        self._reset_state()
        self.status = "running"

    def set_speed(self, multiplier: int) -> None:
        self.speed_multiplier = multiplier

    def _reset_state(self) -> None:
        reset_callsign_pool()
        self.runway_state = RunwayState()
        self.aircraft = {}
        self.tick_count = 0
        self.sim_time_s = 0.0
        self.score_tracker = ScoreTracker()
        self.conflicts = []
        self.comms_log = []
        self.pending_requests = {}
        self.sectors_status = []
        self.landing_queue = []
        self._last_request_time = {}
        self._last_emergency_time = {}
        self._last_runway_emergency_time = {}
        self._exit_countdown = {}
        self._spawn_sim_time = {}
        self._expected_duration_s = {}
        self._spawned_count = 0
        self._route_cycle_index = 0
        self._next_spawn_time = 0.0
        self.game_over = None

    # --- commands ---

    def apply_command(self, aircraft_id: str, command: Command) -> None:
        ac = self.aircraft.get(aircraft_id)
        if ac is None:
            raise ValueError(f"Unknown aircraft: {aircraft_id}")
        if isinstance(command, HeadingCommand):
            ac.target_heading_deg = command.value
        elif isinstance(command, AltitudeCommand):
            ac.target_altitude_ft = command.value
        elif isinstance(command, SpeedCommand):
            ac.target_speed_kt = command.value
        elif isinstance(command, RouteCommand):
            self._apply_route_command(ac, command.waypoint_id)
        elif isinstance(command, LandCommand):
            landing.land_aircraft(ac, command.runway_id, self.runways, self.runway_state, self.sim_time_s)
        else:
            raise ValueError(f"Unsupported command: {command}")

        cleared_type = CORRECTING_COMMAND_EMERGENCY.get(type(command))
        if cleared_type is not None and ac.emergency is not None and ac.emergency.type == cleared_type:
            ac.emergency = None

    def _apply_route_command(self, ac: Aircraft, waypoint_id: str) -> None:
        wp = self.waypoints.get(waypoint_id)
        if wp is None:
            raise ValueError(f"Unknown waypoint: {waypoint_id}")
        if waypoint_id in ac.route:
            ac.route_index = ac.route.index(waypoint_id)
        else:
            ac.route.insert(ac.route_index, waypoint_id)
        ac.target_heading_deg = bearing_to(ac.x, ac.y, wp.x, wp.y)

    def approve_request(self, request_id: str) -> None:
        req = self.pending_requests.get(request_id)
        if req is None:
            raise ValueError(f"Unknown request: {request_id}")
        req.status = "approved"
        self.apply_command(req.aircraft_id, req.suggested_command)
        self.score_tracker.record_request_approved()
        del self.pending_requests[request_id]

    def deny_request(self, request_id: str) -> None:
        req = self.pending_requests.get(request_id)
        if req is None:
            raise ValueError(f"Unknown request: {request_id}")
        req.status = "denied"
        del self.pending_requests[request_id]

    # --- tick loop ---

    def tick(self) -> None:
        if self.status != "running" or self.game_over is not None:
            return
        for _ in range(self.speed_multiplier):
            self._advance(TICK_SECONDS)
        self.tick_count += 1

    def _advance(self, dt: float) -> None:
        self.sim_time_s += dt

        for ac in self.aircraft.values():
            emergencies.apply_emergency_effects(ac, dt)

        for ac in list(self.aircraft.values()):
            movement.step_aircraft(ac, dt, self.waypoints, self.scenario.airspace_bounds)

        for ac in self.aircraft.values():
            landing.promote_to_approach(ac, self.airport_ids_with_runways)

        self.conflicts = detect_conflicts(self.aircraft)
        self._apply_conflict_status()
        self.score_tracker.update_conflicts(self.conflicts)

        self._generate_requests()
        self._process_emergencies()
        self.sectors_status = sectors.compute_sector_stats(self.aircraft, self.scenario.sectors)
        self.landing_queue = landing.build_landing_queue(self.aircraft)
        self._process_exits()
        self._spawn_if_due()

        self.game_over = check_game_over(
            self.score_tracker.state, self.conflicts, self.scenario.total_aircraft_target
        )

    def _process_emergencies(self) -> None:
        if not self.scenario.emergencies_enabled:
            return

        for ac in self.aircraft.values():
            status = emergencies.maybe_trigger_aircraft_emergency(
                ac, self.sim_time_s, self.tick_count, self._last_emergency_time
            )
            if status is not None:
                ac.emergency = status
                self.comms_log.append(
                    CommsMessage(
                        id=str(uuid.uuid4()),
                        from_=ac.callsign,
                        text=status.message,
                        kind="pilot_report",
                        created_at_tick=self.tick_count,
                    )
                )

        result = emergencies.maybe_trigger_runway_unavailable(
            self.scenario.runways,
            self.sim_time_s,
            self.tick_count,
            self._last_runway_emergency_time,
            self.runway_state.unavailable_until,
        )
        if result is not None:
            runway, status = result
            self.comms_log.append(
                CommsMessage(
                    id=str(uuid.uuid4()),
                    from_=runway.name,
                    text=status.message,
                    kind="pilot_report",
                    created_at_tick=self.tick_count,
                )
            )

    def _apply_conflict_status(self) -> None:
        levels: dict[str, ConflictStatus] = {}
        for w in self.conflicts:
            level = ConflictStatus.WARNING if w.risk_level in ("warning", "violation") else ConflictStatus.CAUTION
            for aid in (w.aircraft_a, w.aircraft_b):
                if levels.get(aid) != ConflictStatus.WARNING:
                    levels[aid] = level
        for ac in self.aircraft.values():
            ac.conflict_status = levels.get(ac.id, ConflictStatus.NONE)

    def _generate_requests(self) -> None:
        for ac in self.aircraft.values():
            req = pilot_requests.maybe_generate_request(
                ac, self.waypoints, self.sim_time_s, self.tick_count, self._last_request_time
            )
            if req is not None:
                self.pending_requests[req.id] = req
                self.comms_log.append(
                    CommsMessage(
                        id=str(uuid.uuid4()),
                        from_=ac.callsign,
                        text=req.message,
                        kind="pilot_request",
                        created_at_tick=self.tick_count,
                    )
                )

    def _process_exits(self) -> None:
        for ac in list(self.aircraft.values()):
            if ac.phase not in (FlightPhase.EXITING, FlightPhase.LANDING):
                continue
            if ac.id not in self._exit_countdown:
                delay_s = self._estimate_delay(ac)
                if ac.phase == FlightPhase.LANDING or self._is_clean_exit(ac):
                    self.score_tracker.record_clean_exit(ac, delay_s)
                else:
                    self.score_tracker.record_excursion(ac, delay_s)
                grace = LANDING_GRACE_TICKS if ac.phase == FlightPhase.LANDING else EXIT_GRACE_TICKS
                self._exit_countdown[ac.id] = grace
            else:
                self._exit_countdown[ac.id] -= 1
                if self._exit_countdown[ac.id] <= 0:
                    ac.phase = FlightPhase.LANDED if ac.phase == FlightPhase.LANDING else FlightPhase.EXITED
                    del self.aircraft[ac.id]
                    del self._exit_countdown[ac.id]
                    self._spawn_sim_time.pop(ac.id, None)
                    self._expected_duration_s.pop(ac.id, None)
                    self._last_request_time.pop(ac.id, None)
                    self._last_emergency_time.pop(ac.id, None)

    def _is_clean_exit(self, ac: Aircraft) -> bool:
        dest_wp = self.waypoints.get(ac.destination)
        if dest_wp is None:
            return False
        return distance_xy(ac.x, ac.y, dest_wp.x, dest_wp.y) <= DESTINATION_EXIT_RADIUS_NM

    def _estimate_delay(self, ac: Aircraft) -> float:
        spawn_time = self._spawn_sim_time.get(ac.id, self.sim_time_s)
        expected = self._expected_duration_s.get(ac.id, 0.0)
        elapsed = self.sim_time_s - spawn_time
        return max(0.0, elapsed - expected)

    def _spawn_if_due(self) -> None:
        if self._spawned_count >= self.scenario.total_aircraft_target:
            return
        if len(self.aircraft) >= self.scenario.max_concurrent_aircraft:
            return
        if self.sim_time_s < self._next_spawn_time:
            return
        self._spawn_aircraft()
        self._next_spawn_time = self.sim_time_s + self.scenario.spawn_interval_s

    def _spawn_aircraft(self) -> None:
        route_id = self._route_cycle[self._route_cycle_index % len(self._route_cycle)]
        self._route_cycle_index += 1
        route = self.routes[route_id]

        first_wp = self.waypoints[route.waypoint_ids[0]]
        second_wp_id = route.waypoint_ids[1] if len(route.waypoint_ids) > 1 else route.waypoint_ids[0]
        second_wp = self.waypoints[second_wp_id]
        dest_wp = self.waypoints[route.waypoint_ids[-1]]

        heading = bearing_to(first_wp.x, first_wp.y, second_wp.x, second_wp.y)
        altitude = random.choice(CRUISE_ALTITUDES)
        distance_to_dest = distance_xy(first_wp.x, first_wp.y, dest_wp.x, dest_wp.y)

        ac = Aircraft(
            id=str(uuid.uuid4()),
            callsign=generate_callsign(),
            aircraft_type=generate_aircraft_type(),
            x=first_wp.x,
            y=first_wp.y,
            altitude_ft=altitude,
            heading_deg=heading,
            speed_kt=CRUISE_SPEED_KT,
            vertical_speed_fpm=0.0,
            target_heading_deg=heading,
            target_altitude_ft=altitude,
            target_speed_kt=CRUISE_SPEED_KT,
            origin=first_wp.id,
            destination=dest_wp.id,
            route=list(route.waypoint_ids),
            route_index=0,
            phase=FlightPhase.CRUISE,
            conflict_status=ConflictStatus.NONE,
            distance_to_destination_nm=distance_to_dest,
            eta_minutes=(distance_to_dest / CRUISE_SPEED_KT) * 60.0,
            spawned_at_tick=self.tick_count,
        )
        self.aircraft[ac.id] = ac
        self._spawned_count += 1
        self._spawn_sim_time[ac.id] = self.sim_time_s
        self._expected_duration_s[ac.id] = (distance_to_dest / CRUISE_SPEED_KT) * 3600.0

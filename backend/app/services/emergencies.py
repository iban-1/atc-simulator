"""Simulated emergency events — entirely fictional game mechanics, not real
aviation emergency procedures. Only active when a scenario opts in via
ScenarioConfig.emergencies_enabled."""

import random

from app.models.aircraft import Aircraft, FlightPhase
from app.models.emergency import EmergencyStatus, EmergencyType
from app.models.runway import Runway

AIRCRAFT_EMERGENCY_PROBABILITY_PER_TICK = 0.003
AIRCRAFT_EMERGENCY_COOLDOWN_S = 120.0
RUNWAY_EMERGENCY_PROBABILITY_PER_TICK = 0.0008
RUNWAY_EMERGENCY_COOLDOWN_S = 240.0
RUNWAY_UNAVAILABLE_DURATION_S = 60.0

AIRCRAFT_EMERGENCY_TYPES = [
    EmergencyType.ALTITUDE_CONTROL_LOSS,
    EmergencyType.PRIORITY_LANDING,
    EmergencyType.ABNORMAL_SPEED,
    EmergencyType.ROUTE_DEVIATION,
]

_NON_TRACKABLE_PHASES = (FlightPhase.EXITING, FlightPhase.EXITED, FlightPhase.LANDING, FlightPhase.LANDED)


def maybe_trigger_aircraft_emergency(
    ac: Aircraft,
    sim_time_s: float,
    tick: int,
    last_emergency_time: dict[str, float],
) -> EmergencyStatus | None:
    if ac.emergency is not None or ac.phase in _NON_TRACKABLE_PHASES:
        return None
    last = last_emergency_time.get(ac.id, -AIRCRAFT_EMERGENCY_COOLDOWN_S)
    if sim_time_s - last < AIRCRAFT_EMERGENCY_COOLDOWN_S:
        return None
    if random.random() >= AIRCRAFT_EMERGENCY_PROBABILITY_PER_TICK:
        return None

    last_emergency_time[ac.id] = sim_time_s
    emergency_type = random.choice(AIRCRAFT_EMERGENCY_TYPES)
    return EmergencyStatus(type=emergency_type, message=_describe(ac, emergency_type), started_at_tick=tick)


def _describe(ac: Aircraft, emergency_type: EmergencyType) -> str:
    descriptions = {
        EmergencyType.ALTITUDE_CONTROL_LOSS: f"{ac.callsign} reports altitude control issues (simulated emergency).",
        EmergencyType.PRIORITY_LANDING: f"{ac.callsign} requests priority landing (simulated emergency).",
        EmergencyType.ABNORMAL_SPEED: f"{ac.callsign} reports an abnormal speed reading (simulated emergency).",
        EmergencyType.ROUTE_DEVIATION: f"{ac.callsign} has deviated from its assigned route (simulated emergency).",
    }
    return descriptions.get(emergency_type, f"{ac.callsign} reports an emergency (simulated).")


def apply_emergency_effects(ac: Aircraft, dt: float) -> None:
    """Per-tick drift while an emergency is active and uncorrected. Cleared
    by the engine once the player issues the matching corrective command."""
    if ac.emergency is None:
        return
    if ac.emergency.type == EmergencyType.ALTITUDE_CONTROL_LOSS:
        drift = random.uniform(-300.0, 300.0) * dt
        ac.target_altitude_ft = max(0.0, min(45000.0, ac.target_altitude_ft + drift))
    elif ac.emergency.type == EmergencyType.ABNORMAL_SPEED:
        drift = random.uniform(-10.0, 10.0) * dt
        ac.target_speed_kt = max(100.0, min(600.0, ac.target_speed_kt + drift))
    elif ac.emergency.type == EmergencyType.ROUTE_DEVIATION:
        drift = random.uniform(-5.0, 5.0) * dt
        ac.target_heading_deg = (ac.target_heading_deg + drift) % 360.0
    # PRIORITY_LANDING has no per-tick physical effect; it's a queue-priority flag
    # cleared once the aircraft is granted a landing clearance.


def maybe_trigger_runway_unavailable(
    runways: list[Runway],
    sim_time_s: float,
    tick: int,
    last_runway_emergency_time: dict[str, float],
    unavailable_until: dict[str, float],
) -> tuple[Runway, EmergencyStatus] | None:
    if not runways:
        return None
    last = last_runway_emergency_time.get("_global", -RUNWAY_EMERGENCY_COOLDOWN_S)
    if sim_time_s - last < RUNWAY_EMERGENCY_COOLDOWN_S:
        return None
    if random.random() >= RUNWAY_EMERGENCY_PROBABILITY_PER_TICK:
        return None

    last_runway_emergency_time["_global"] = sim_time_s
    runway = random.choice(runways)
    unavailable_until[runway.id] = sim_time_s + RUNWAY_UNAVAILABLE_DURATION_S
    status = EmergencyStatus(
        type=EmergencyType.RUNWAY_UNAVAILABLE,
        message=f"Runway {runway.name} is temporarily unavailable (simulated emergency).",
        started_at_tick=tick,
    )
    return runway, status

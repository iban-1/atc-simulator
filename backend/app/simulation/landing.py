"""Simplified arrivals/landing sequencing — a fictional game mechanic
(single runway per airport, basic minimum-spacing rule), not a real
approach/ATC separation standard."""

from dataclasses import dataclass, field

from app.models.aircraft import Aircraft, FlightPhase
from app.models.emergency import EmergencyType
from app.models.messages import LandingQueueEntry
from app.models.runway import Runway
from app.simulation import constants


@dataclass
class RunwayState:
    last_landed_at: dict[str, float] = field(default_factory=dict)
    unavailable_until: dict[str, float] = field(default_factory=dict)


def runways_by_id(runways: list[Runway]) -> dict[str, Runway]:
    return {rw.id: rw for rw in runways}


def airports_with_runways(runways: list[Runway]) -> set[str]:
    return {rw.airport_id for rw in runways}


def promote_to_approach(ac: Aircraft, airport_ids_with_runways: set[str]) -> None:
    if ac.phase != FlightPhase.EXITING:
        return
    if ac.assigned_runway is not None:
        return
    if ac.destination not in airport_ids_with_runways:
        return
    if ac.distance_to_destination_nm <= constants.APPROACH_RADIUS_NM:
        ac.phase = FlightPhase.APPROACH


def land_aircraft(
    ac: Aircraft,
    runway_id: str,
    runways: dict[str, Runway],
    runway_state: RunwayState,
    sim_time_s: float,
) -> None:
    if ac.phase != FlightPhase.APPROACH:
        raise ValueError(f"{ac.callsign} is not established on approach")

    runway = runways.get(runway_id)
    if runway is None:
        raise ValueError(f"Unknown runway: {runway_id}")
    if runway.airport_id != ac.destination:
        raise ValueError(f"Runway {runway.name} does not serve {ac.destination}")

    unavailable_until = runway_state.unavailable_until.get(runway_id)
    if unavailable_until is not None and sim_time_s < unavailable_until:
        raise ValueError(f"Runway {runway.name} is currently unavailable (simulated emergency)")

    last_landed = runway_state.last_landed_at.get(runway_id)
    if last_landed is not None and sim_time_s - last_landed < constants.MIN_LANDING_SPACING_S:
        raise ValueError(f"Runway {runway.name} needs more spacing before another landing")

    ac.assigned_runway = runway_id
    ac.phase = FlightPhase.LANDING
    runway_state.last_landed_at[runway_id] = sim_time_s
    if ac.emergency is not None and ac.emergency.type == EmergencyType.PRIORITY_LANDING:
        ac.emergency = None


def build_landing_queue(aircraft: dict[str, Aircraft]) -> list[LandingQueueEntry]:
    relevant = [ac for ac in aircraft.values() if ac.phase in (FlightPhase.APPROACH, FlightPhase.LANDING)]
    relevant.sort(key=lambda ac: (ac.phase != FlightPhase.LANDING, ac.distance_to_destination_nm))

    entries: list[LandingQueueEntry] = []
    per_runway_position: dict[str, int] = {}
    for ac in relevant:
        runway_key = ac.assigned_runway or f"unassigned:{ac.destination}"
        position = per_runway_position.get(runway_key, 0) + 1
        per_runway_position[runway_key] = position
        entries.append(
            LandingQueueEntry(
                runway_id=ac.assigned_runway or "",
                aircraft_id=ac.id,
                callsign=ac.callsign,
                position=position,
                phase="landing" if ac.phase == FlightPhase.LANDING else "approach",
            )
        )
    return entries

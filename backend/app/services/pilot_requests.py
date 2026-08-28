"""Simulated pilot request generation — entirely fictional flavor text tied
to real aircraft state. Each request carries a suggested_command so the
comms panel's Approve button can execute it directly via the sim engine.
"""

import random
import uuid

from app.models.aircraft import Aircraft, AltitudeCommand, RouteCommand, SpeedCommand
from app.models.messages import PilotRequest
from app.models.waypoint import Waypoint

REQUEST_PROBABILITY_PER_TICK = 0.01
COOLDOWN_S = 90.0


def maybe_generate_request(
    ac: Aircraft,
    waypoints: dict[str, Waypoint],
    sim_time_s: float,
    tick: int,
    last_request_time: dict[str, float],
) -> PilotRequest | None:
    if ac.phase.value in ("exiting", "exited"):
        return None

    last = last_request_time.get(ac.id, -COOLDOWN_S)
    if sim_time_s - last < COOLDOWN_S:
        return None

    if random.random() >= REQUEST_PROBABILITY_PER_TICK:
        return None

    candidates = []

    if ac.altitude_ft > 12000.0:
        candidates.append("descend")
    if ac.route_index + 1 < len(ac.route):
        candidates.append("direct")
    if ac.speed_kt < 500.0:
        candidates.append("speed")

    if not candidates:
        return None

    kind = random.choice(candidates)
    last_request_time[ac.id] = sim_time_s

    if kind == "descend":
        target_alt = max(4000.0, ac.altitude_ft - 4000.0)
        return PilotRequest(
            id=str(uuid.uuid4()),
            aircraft_id=ac.id,
            callsign=ac.callsign,
            message=f"{ac.callsign} requesting descent to FL{int(target_alt / 100)}.",
            suggested_command=AltitudeCommand(value=target_alt),
            created_at_tick=tick,
        )

    if kind == "direct":
        final_wp_id = ac.route[-1]
        final_wp = waypoints.get(final_wp_id)
        wp_name = final_wp.name if final_wp else final_wp_id
        return PilotRequest(
            id=str(uuid.uuid4()),
            aircraft_id=ac.id,
            callsign=ac.callsign,
            message=f"{ac.callsign} requesting direct to {wp_name}.",
            suggested_command=RouteCommand(waypoint_id=final_wp_id),
            created_at_tick=tick,
        )

    target_speed = min(560.0, ac.speed_kt + 40.0)
    return PilotRequest(
        id=str(uuid.uuid4()),
        aircraft_id=ac.id,
        callsign=ac.callsign,
        message=f"{ac.callsign} requesting speed increase to {int(target_speed)} knots.",
        suggested_command=SpeedCommand(value=target_speed),
        created_at_tick=tick,
    )

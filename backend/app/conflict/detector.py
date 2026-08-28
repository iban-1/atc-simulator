"""Conflict prediction between aircraft pairs.

Separation minimums and lookahead windows here are simplified, fictional
game mechanics — not real aviation separation standards. This module only
detects and reports; it never mutates aircraft state or auto-resolves a
conflict. The player must always decide what command to issue.
"""

import itertools

import numpy as np

from app.models.aircraft import Aircraft, FlightPhase
from app.models.messages import ConflictWarning
from app.simulation import constants
from app.simulation.geometry import distance, velocity_vector


def closest_point_of_approach(a: Aircraft, b: Aircraft) -> tuple[float, float]:
    """Returns (time_to_cpa_seconds, horizontal_separation_at_cpa_nm)."""
    rel_pos = np.array([b.x - a.x, b.y - a.y])
    rel_vel = velocity_vector(b.heading_deg, b.speed_kt) - velocity_vector(a.heading_deg, a.speed_kt)

    speed_sq = float(np.dot(rel_vel, rel_vel))
    if speed_sq < 1e-9:
        t_cpa = 0.0
    else:
        t_cpa = max(0.0, -float(np.dot(rel_pos, rel_vel)) / speed_sq)

    future_rel = rel_pos + rel_vel * t_cpa
    sep_at_cpa = float(np.hypot(*future_rel))
    return t_cpa, sep_at_cpa


def _is_trackable(ac: Aircraft) -> bool:
    return ac.phase not in (FlightPhase.EXITING, FlightPhase.EXITED)


def detect_conflicts(aircraft: dict[str, Aircraft]) -> list[ConflictWarning]:
    warnings: list[ConflictWarning] = []
    trackable = [ac for ac in aircraft.values() if _is_trackable(ac)]

    for a, b in itertools.combinations(trackable, 2):
        vert_sep = abs(a.altitude_ft - b.altitude_ft)
        if vert_sep >= constants.VERTICAL_SEP_MIN_FT:
            continue

        t_cpa, predicted_sep = closest_point_of_approach(a, b)
        current_sep = distance(a, b)

        is_violation = current_sep < constants.HORIZONTAL_SEP_MIN_NM
        will_conflict = t_cpa <= constants.LOOKAHEAD_SECONDS and predicted_sep < constants.HORIZONTAL_SEP_MIN_NM

        if not (is_violation or will_conflict):
            continue

        if is_violation:
            risk_level = "violation"
        elif t_cpa <= constants.WARNING_LEAD_SECONDS:
            risk_level = "warning"
        else:
            risk_level = "caution"

        warnings.append(
            ConflictWarning(
                aircraft_a=a.id,
                aircraft_b=b.id,
                time_to_conflict_s=t_cpa,
                predicted_separation_nm=predicted_sep,
                vertical_separation_ft=vert_sep,
                risk_level=risk_level,
                is_active_violation=is_violation,
            )
        )

    return warnings

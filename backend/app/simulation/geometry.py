import math

import numpy as np

from app.models.aircraft import Aircraft


def velocity_vector(heading_deg: float, speed_kt: float) -> np.ndarray:
    """Velocity vector in NM/second, in the sim's flat x/y (E/N) plane."""
    angle_rad = math.radians(90.0 - heading_deg)
    speed_nm_per_s = speed_kt / 3600.0
    return np.array([speed_nm_per_s * math.cos(angle_rad), speed_nm_per_s * math.sin(angle_rad)])


def distance(a: Aircraft, b: Aircraft) -> float:
    return float(math.hypot(a.x - b.x, a.y - b.y))


def distance_xy(x1: float, y1: float, x2: float, y2: float) -> float:
    return float(math.hypot(x2 - x1, y2 - y1))


def bearing_to(x1: float, y1: float, x2: float, y2: float) -> float:
    """Heading in degrees (0=N, 90=E) from point 1 to point 2."""
    angle_rad = math.atan2(x2 - x1, y2 - y1)
    heading = math.degrees(angle_rad)
    return heading % 360.0


def shortest_angle_delta(current_deg: float, target_deg: float) -> float:
    """Signed shortest turn (degrees) from current to target heading, in (-180, 180]."""
    return ((target_deg - current_deg + 540.0) % 360.0) - 180.0

"""Airspace sector occupancy — a simplified, fictional traffic-density
display, not a real ATC sectorization system."""

from app.models.aircraft import Aircraft
from app.models.messages import SectorStatus
from app.models.sector import Sector

LOW_DENSITY_MAX = 2
MEDIUM_DENSITY_MAX = 5


def _point_in_polygon(x: float, y: float, boundary: list[tuple[float, float]]) -> bool:
    inside = False
    n = len(boundary)
    for i in range(n):
        x1, y1 = boundary[i]
        x2, y2 = boundary[(i + 1) % n]
        crosses = (y1 > y) != (y2 > y)
        if crosses:
            x_at_y = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < x_at_y:
                inside = not inside
    return inside


def _density_label(count: int) -> str:
    if count <= LOW_DENSITY_MAX:
        return "low"
    if count <= MEDIUM_DENSITY_MAX:
        return "medium"
    return "high"


def compute_sector_stats(aircraft: dict[str, Aircraft], sectors: list[Sector]) -> list[SectorStatus]:
    stats = []
    for sector in sectors:
        count = sum(1 for ac in aircraft.values() if _point_in_polygon(ac.x, ac.y, sector.boundary))
        stats.append(
            SectorStatus(id=sector.id, name=sector.name, aircraft_count=count, density=_density_label(count))
        )
    return stats

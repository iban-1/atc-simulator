from pydantic import BaseModel

from app.models.route import Route
from app.models.runway import Runway
from app.models.sector import Sector
from app.models.waypoint import Waypoint


class ScenarioConfig(BaseModel):
    id: str
    name: str
    description: str
    difficulty: int

    # (min_x, min_y, max_x, max_y) in NM
    airspace_bounds: tuple[float, float, float, float]

    waypoints: list[Waypoint]
    routes: list[Route]
    sectors: list[Sector] = []
    runways: list[Runway] = []

    max_concurrent_aircraft: int
    spawn_interval_s: float
    total_aircraft_target: int
    objective_description: str

    emergencies_enabled: bool = False

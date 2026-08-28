from app.models.route import Route
from app.models.scenario import ScenarioConfig
from app.models.waypoint import Waypoint

QUIET_AIRSPACE = ScenarioConfig(
    id="quiet-airspace",
    name="Quiet Airspace",
    description="Light traffic, generous separation — ideal for learning the controls. All aircraft, airports and waypoints are fictional.",
    difficulty=1,
    airspace_bounds=(-60.0, -60.0, 60.0, 60.0),
    waypoints=[
        Waypoint(id="wpt-alpha", name="ALPHA", x=-40.0, y=30.0, kind="waypoint"),
        Waypoint(id="wpt-bravo", name="BRAVO", x=40.0, y=-30.0, kind="waypoint"),
        Waypoint(id="apt-nova", name="NOVA", x=0.0, y=0.0, kind="airport"),
    ],
    routes=[
        Route(id="rt-alpha-nova", waypoint_ids=["wpt-alpha", "apt-nova"]),
        Route(id="rt-bravo-nova", waypoint_ids=["wpt-bravo", "apt-nova"]),
    ],
    max_concurrent_aircraft=5,
    spawn_interval_s=45.0,
    total_aircraft_target=8,
    objective_description="Safely guide 8 aircraft through the sector with zero collisions.",
)

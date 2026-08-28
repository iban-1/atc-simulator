from app.models.route import Route
from app.models.scenario import ScenarioConfig
from app.models.waypoint import Waypoint

CONFLICT_CHALLENGE = ScenarioConfig(
    id="conflict-challenge",
    name="Conflict Challenge",
    description="Four through-traffic routes deliberately crossing at the center of the sector. All aircraft and waypoints are fictional.",
    difficulty=3,
    airspace_bounds=(-60.0, -60.0, 60.0, 60.0),
    waypoints=[
        Waypoint(id="wpt-north", name="NORTH", x=0.0, y=50.0, kind="waypoint"),
        Waypoint(id="wpt-south", name="SOUTH", x=0.0, y=-50.0, kind="waypoint"),
        Waypoint(id="wpt-east", name="EAST", x=50.0, y=0.0, kind="waypoint"),
        Waypoint(id="wpt-west", name="WEST", x=-50.0, y=0.0, kind="waypoint"),
    ],
    routes=[
        Route(id="rt-north-south", waypoint_ids=["wpt-north", "wpt-south"]),
        Route(id="rt-south-north", waypoint_ids=["wpt-south", "wpt-north"]),
        Route(id="rt-east-west", waypoint_ids=["wpt-east", "wpt-west"]),
        Route(id="rt-west-east", waypoint_ids=["wpt-west", "wpt-east"]),
    ],
    max_concurrent_aircraft=8,
    spawn_interval_s=30.0,
    total_aircraft_target=12,
    objective_description="Guide 12 crossing aircraft through the sector with zero conflicts.",
)

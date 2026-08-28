from app.models.route import Route
from app.models.runway import Runway
from app.models.scenario import ScenarioConfig
from app.models.sector import Sector
from app.models.waypoint import Waypoint

BUSY_AIRSPACE = ScenarioConfig(
    id="busy-airspace",
    name="Busy Airspace",
    description="Crossing through-traffic plus arrivals into one airport, divided into four sectors. All aircraft, airports and waypoints are fictional.",
    difficulty=3,
    airspace_bounds=(-70.0, -70.0, 70.0, 70.0),
    waypoints=[
        Waypoint(id="wpt-north", name="NORTH", x=0.0, y=55.0, kind="waypoint"),
        Waypoint(id="wpt-south", name="SOUTH", x=0.0, y=-55.0, kind="waypoint"),
        Waypoint(id="wpt-east", name="EAST", x=55.0, y=0.0, kind="waypoint"),
        Waypoint(id="wpt-west", name="WEST", x=-55.0, y=0.0, kind="waypoint"),
        Waypoint(id="apt-nova", name="NOVA", x=0.0, y=0.0, kind="airport"),
    ],
    routes=[
        Route(id="rt-north-south", waypoint_ids=["wpt-north", "wpt-south"]),
        Route(id="rt-south-north", waypoint_ids=["wpt-south", "wpt-north"]),
        Route(id="rt-east-west", waypoint_ids=["wpt-east", "wpt-west"]),
        Route(id="rt-west-east", waypoint_ids=["wpt-west", "wpt-east"]),
        Route(id="rt-north-nova", waypoint_ids=["wpt-north", "apt-nova"]),
        Route(id="rt-south-nova", waypoint_ids=["wpt-south", "apt-nova"]),
        Route(id="rt-east-nova", waypoint_ids=["wpt-east", "apt-nova"]),
        Route(id="rt-west-nova", waypoint_ids=["wpt-west", "apt-nova"]),
        Route(id="rt-nova-south", waypoint_ids=["apt-nova", "wpt-south"]),
    ],
    sectors=[
        Sector(id="sector-ne", name="SECTOR NE", boundary=[(0.0, 0.0), (70.0, 0.0), (70.0, 70.0), (0.0, 70.0)]),
        Sector(id="sector-nw", name="SECTOR NW", boundary=[(-70.0, 0.0), (0.0, 0.0), (0.0, 70.0), (-70.0, 70.0)]),
        Sector(id="sector-se", name="SECTOR SE", boundary=[(0.0, -70.0), (70.0, -70.0), (70.0, 0.0), (0.0, 0.0)]),
        Sector(id="sector-sw", name="SECTOR SW", boundary=[(-70.0, -70.0), (0.0, -70.0), (0.0, 0.0), (-70.0, 0.0)]),
    ],
    runways=[Runway(id="rwy-nova-09", name="RWY 09", airport_id="apt-nova", heading_deg=90.0)],
    max_concurrent_aircraft=10,
    spawn_interval_s=25.0,
    total_aircraft_target=20,
    objective_description="Manage 20 aircraft across four sectors with crossing routes and zero collisions.",
)

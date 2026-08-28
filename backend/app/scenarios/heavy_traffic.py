from app.models.route import Route
from app.models.runway import Runway
from app.models.scenario import ScenarioConfig
from app.models.sector import Sector
from app.models.waypoint import Waypoint

HEAVY_TRAFFIC = ScenarioConfig(
    id="heavy-traffic",
    name="Heavy Traffic",
    description="High-density traffic across eight entry points with frequent crossing routes. All aircraft, airports and waypoints are fictional.",
    difficulty=4,
    airspace_bounds=(-80.0, -80.0, 80.0, 80.0),
    waypoints=[
        Waypoint(id="wpt-north", name="NORTH", x=0.0, y=65.0, kind="waypoint"),
        Waypoint(id="wpt-south", name="SOUTH", x=0.0, y=-65.0, kind="waypoint"),
        Waypoint(id="wpt-east", name="EAST", x=65.0, y=0.0, kind="waypoint"),
        Waypoint(id="wpt-west", name="WEST", x=-65.0, y=0.0, kind="waypoint"),
        Waypoint(id="wpt-ne", name="NORTHEAST", x=45.0, y=45.0, kind="waypoint"),
        Waypoint(id="wpt-sw", name="SOUTHWEST", x=-45.0, y=-45.0, kind="waypoint"),
        Waypoint(id="apt-nova", name="NOVA", x=0.0, y=0.0, kind="airport"),
    ],
    routes=[
        Route(id="rt-north-south", waypoint_ids=["wpt-north", "wpt-south"]),
        Route(id="rt-south-north", waypoint_ids=["wpt-south", "wpt-north"]),
        Route(id="rt-east-west", waypoint_ids=["wpt-east", "wpt-west"]),
        Route(id="rt-west-east", waypoint_ids=["wpt-west", "wpt-east"]),
        Route(id="rt-ne-sw", waypoint_ids=["wpt-ne", "wpt-sw"]),
        Route(id="rt-sw-ne", waypoint_ids=["wpt-sw", "wpt-ne"]),
        Route(id="rt-north-nova", waypoint_ids=["wpt-north", "apt-nova"]),
        Route(id="rt-south-nova", waypoint_ids=["wpt-south", "apt-nova"]),
        Route(id="rt-east-nova", waypoint_ids=["wpt-east", "apt-nova"]),
        Route(id="rt-west-nova", waypoint_ids=["wpt-west", "apt-nova"]),
    ],
    sectors=[
        Sector(id="sector-ne", name="SECTOR NE", boundary=[(0.0, 0.0), (80.0, 0.0), (80.0, 80.0), (0.0, 80.0)]),
        Sector(id="sector-nw", name="SECTOR NW", boundary=[(-80.0, 0.0), (0.0, 0.0), (0.0, 80.0), (-80.0, 80.0)]),
        Sector(id="sector-se", name="SECTOR SE", boundary=[(0.0, -80.0), (80.0, -80.0), (80.0, 0.0), (0.0, 0.0)]),
        Sector(id="sector-sw", name="SECTOR SW", boundary=[(-80.0, -80.0), (0.0, -80.0), (0.0, 0.0), (-80.0, 0.0)]),
    ],
    runways=[Runway(id="rwy-nova-09", name="RWY 09", airport_id="apt-nova", heading_deg=90.0)],
    max_concurrent_aircraft=15,
    spawn_interval_s=15.0,
    total_aircraft_target=32,
    objective_description="Handle 32+ aircraft through dense crossing traffic with zero collisions.",
)

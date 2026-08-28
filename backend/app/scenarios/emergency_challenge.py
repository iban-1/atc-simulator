from app.models.route import Route
from app.models.runway import Runway
from app.models.scenario import ScenarioConfig
from app.models.sector import Sector
from app.models.waypoint import Waypoint

EMERGENCY_CHALLENGE = ScenarioConfig(
    id="emergency-challenge",
    name="Emergency Challenge",
    description="Frequent requests and simulated in-flight emergencies with limited reaction time. All aircraft, airports and waypoints are fictional; emergencies here are simplified game mechanics, not real aviation procedures.",
    difficulty=5,
    airspace_bounds=(-60.0, -60.0, 60.0, 60.0),
    waypoints=[
        Waypoint(id="wpt-alpha", name="ALPHA", x=-40.0, y=30.0, kind="waypoint"),
        Waypoint(id="wpt-bravo", name="BRAVO", x=40.0, y=-30.0, kind="waypoint"),
        Waypoint(id="wpt-charlie", name="CHARLIE", x=-40.0, y=-30.0, kind="waypoint"),
        Waypoint(id="wpt-delta", name="DELTA", x=40.0, y=30.0, kind="waypoint"),
        Waypoint(id="apt-nova", name="NOVA", x=0.0, y=0.0, kind="airport"),
    ],
    routes=[
        Route(id="rt-alpha-nova", waypoint_ids=["wpt-alpha", "apt-nova"]),
        Route(id="rt-bravo-nova", waypoint_ids=["wpt-bravo", "apt-nova"]),
        Route(id="rt-charlie-nova", waypoint_ids=["wpt-charlie", "apt-nova"]),
        Route(id="rt-delta-nova", waypoint_ids=["wpt-delta", "apt-nova"]),
        Route(id="rt-nova-charlie", waypoint_ids=["apt-nova", "wpt-charlie"]),
    ],
    sectors=[
        Sector(id="sector-north", name="SECTOR NORTH", boundary=[(-60.0, 0.0), (60.0, 0.0), (60.0, 60.0), (-60.0, 60.0)]),
        Sector(id="sector-south", name="SECTOR SOUTH", boundary=[(-60.0, -60.0), (60.0, -60.0), (60.0, 0.0), (-60.0, 0.0)]),
    ],
    runways=[Runway(id="rwy-nova-09", name="RWY 09", airport_id="apt-nova", heading_deg=90.0)],
    max_concurrent_aircraft=10,
    spawn_interval_s=20.0,
    total_aircraft_target=15,
    objective_description="Handle 15 aircraft while responding to simulated emergencies, with zero collisions.",
    emergencies_enabled=True,
)

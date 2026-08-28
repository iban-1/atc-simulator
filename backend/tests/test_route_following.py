from app.models.aircraft import Aircraft, ConflictStatus, FlightPhase
from app.models.waypoint import Waypoint
from app.simulation import movement


def make_aircraft(**overrides) -> Aircraft:
    defaults = dict(
        id="ac-1",
        callsign="SIM100",
        aircraft_type="GX2",
        x=0.0,
        y=0.0,
        altitude_ft=20000.0,
        heading_deg=90.0,
        speed_kt=1800.0,  # fast, so a single tick can cross each waypoint's arrival radius
        vertical_speed_fpm=0.0,
        target_heading_deg=90.0,
        target_altitude_ft=20000.0,
        target_speed_kt=1800.0,
        origin="wpt-a",
        destination="wpt-c",
        route=["wpt-a", "wpt-b", "wpt-c"],
        route_index=0,
        phase=FlightPhase.CRUISE,
        conflict_status=ConflictStatus.NONE,
        distance_to_destination_nm=100.0,
        eta_minutes=None,
        spawned_at_tick=0,
    )
    defaults.update(overrides)
    return Aircraft(**defaults)


def test_advances_route_index_on_reaching_first_waypoint():
    ac = make_aircraft(x=0.0, y=0.0, route_index=0)
    waypoints = {
        "wpt-a": Waypoint(id="wpt-a", name="A", x=0.0, y=0.0, kind="waypoint"),
        "wpt-b": Waypoint(id="wpt-b", name="B", x=50.0, y=0.0, kind="waypoint"),
        "wpt-c": Waypoint(id="wpt-c", name="C", x=50.0, y=50.0, kind="waypoint"),
    }
    bounds = (-200.0, -200.0, 200.0, 200.0)

    # Aircraft starts exactly at wpt-a, which is within arrival radius immediately.
    movement.step_aircraft(ac, dt=1.0, waypoints=waypoints, bounds=bounds)

    assert ac.route_index == 1
    # Heading should now point toward wpt-b (due east).
    assert 89.0 <= ac.target_heading_deg <= 91.0


def test_advances_through_multiple_waypoints_in_order():
    ac = make_aircraft(x=0.0, y=0.0, heading_deg=90.0, target_heading_deg=90.0, route_index=0)
    waypoints = {
        "wpt-a": Waypoint(id="wpt-a", name="A", x=0.0, y=0.0, kind="waypoint"),
        "wpt-b": Waypoint(id="wpt-b", name="B", x=10.0, y=0.0, kind="waypoint"),
        "wpt-c": Waypoint(id="wpt-c", name="C", x=10.0, y=10.0, kind="waypoint"),
    }
    bounds = (-200.0, -200.0, 200.0, 200.0)

    # Step several times; at 1800kt (0.5 NM/s) the aircraft should reach B then turn toward C.
    for _ in range(40):
        movement.step_aircraft(ac, dt=1.0, waypoints=waypoints, bounds=bounds)
        if ac.route_index >= 2:
            break

    assert ac.route_index >= 2


def test_does_not_advance_before_reaching_waypoint():
    ac = make_aircraft(x=0.0, y=0.0, route_index=0, speed_kt=1.0, target_speed_kt=1.0)
    waypoints = {
        "wpt-a": Waypoint(id="wpt-a", name="A", x=50.0, y=0.0, kind="waypoint"),
        "wpt-b": Waypoint(id="wpt-b", name="B", x=100.0, y=0.0, kind="waypoint"),
        "wpt-c": Waypoint(id="wpt-c", name="C", x=150.0, y=0.0, kind="waypoint"),
    }
    bounds = (-200.0, -200.0, 200.0, 200.0)

    movement.step_aircraft(ac, dt=1.0, waypoints=waypoints, bounds=bounds)

    assert ac.route_index == 0

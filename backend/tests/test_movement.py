from app.models.aircraft import Aircraft, FlightPhase, ConflictStatus
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
        speed_kt=360.0,
        vertical_speed_fpm=0.0,
        target_heading_deg=90.0,
        target_altitude_ft=20000.0,
        target_speed_kt=360.0,
        origin="wpt-a",
        destination="wpt-b",
        route=["wpt-b"],
        route_index=0,
        phase=FlightPhase.CRUISE,
        conflict_status=ConflictStatus.NONE,
        distance_to_destination_nm=100.0,
        eta_minutes=None,
        spawned_at_tick=0,
    )
    defaults.update(overrides)
    return Aircraft(**defaults)


def test_moves_east_at_given_heading_and_speed():
    ac = make_aircraft(heading_deg=90.0, target_heading_deg=90.0, speed_kt=360.0, target_speed_kt=360.0)
    waypoints = {"wpt-b": Waypoint(id="wpt-b", name="B", x=100.0, y=0.0, kind="waypoint")}
    bounds = (-60.0, -60.0, 60.0, 60.0)

    movement.step_aircraft(ac, dt=10.0, waypoints=waypoints, bounds=bounds)

    # 360 kt = 0.1 NM/s -> 10s = 1 NM east
    assert ac.x > 0.9
    assert abs(ac.y) < 1e-6


def test_heading_change_is_bounded_by_turn_rate():
    ac = make_aircraft(heading_deg=0.0, target_heading_deg=90.0)
    waypoints: dict[str, Waypoint] = {}
    bounds = (-60.0, -60.0, 60.0, 60.0)

    movement.step_aircraft(ac, dt=1.0, waypoints=waypoints, bounds=bounds)

    # turn rate is 3 deg/sec, so heading should not jump straight to 90
    assert 0.0 < ac.heading_deg <= 3.0 + 1e-6


def test_altitude_change_is_bounded_by_climb_rate():
    ac = make_aircraft(altitude_ft=20000.0, target_altitude_ft=24000.0)
    waypoints: dict[str, Waypoint] = {}
    bounds = (-60.0, -60.0, 60.0, 60.0)

    movement.step_aircraft(ac, dt=1.0, waypoints=waypoints, bounds=bounds)

    # climb rate is 1500 fpm = 25 ft/sec
    assert 20000.0 < ac.altitude_ft <= 20025.0 + 1e-6


def test_marks_exited_when_out_of_bounds():
    ac = make_aircraft(x=59.5, y=0.0, heading_deg=90.0, target_heading_deg=90.0, speed_kt=360.0, target_speed_kt=360.0)
    waypoints = {"wpt-b": Waypoint(id="wpt-b", name="B", x=200.0, y=0.0, kind="waypoint")}
    bounds = (-60.0, -60.0, 60.0, 60.0)

    movement.step_aircraft(ac, dt=10.0, waypoints=waypoints, bounds=bounds)

    assert ac.phase == FlightPhase.EXITING

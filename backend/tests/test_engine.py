import pytest

from app.scenarios.quiet_airspace import QUIET_AIRSPACE
from app.simulation.engine import SimulationEngine
from app.models.aircraft import AltitudeCommand, HeadingCommand, RouteCommand, SpeedCommand


def make_engine() -> SimulationEngine:
    return SimulationEngine(QUIET_AIRSPACE)


def spawn_one(engine: SimulationEngine):
    engine.start()
    engine._spawn_aircraft()
    return next(iter(engine.aircraft.values()))


def test_start_transitions_status_to_running():
    engine = make_engine()
    assert engine.status == "stopped"
    engine.start()
    assert engine.status == "running"


def test_pause_and_resume_toggle_status():
    engine = make_engine()
    engine.start()
    engine.pause()
    assert engine.status == "paused"
    engine.resume()
    assert engine.status == "running"


def test_pause_is_noop_when_not_running():
    engine = make_engine()
    engine.pause()
    assert engine.status == "stopped"


def test_restart_zeroes_score_and_clears_aircraft():
    engine = make_engine()
    ac = spawn_one(engine)
    engine.score_tracker.record_request_approved()
    assert engine.score_tracker.state.score != 0

    engine.restart()

    assert engine.score_tracker.state.score == 0
    assert engine.aircraft == {}
    assert engine.status == "running"


def test_apply_command_unknown_aircraft_raises():
    engine = make_engine()
    with pytest.raises(ValueError):
        engine.apply_command("does-not-exist", HeadingCommand(value=90.0))


def test_apply_heading_command_sets_target_not_position():
    engine = make_engine()
    ac = spawn_one(engine)
    original_x, original_y, original_heading = ac.x, ac.y, ac.heading_deg

    engine.apply_command(ac.id, HeadingCommand(value=200.0))

    assert ac.target_heading_deg == 200.0
    # position and current heading must not jump instantly
    assert ac.x == original_x
    assert ac.y == original_y
    assert ac.heading_deg == original_heading


def test_apply_altitude_command_sets_target_only():
    engine = make_engine()
    ac = spawn_one(engine)
    original_altitude = ac.altitude_ft

    engine.apply_command(ac.id, AltitudeCommand(value=30000.0))

    assert ac.target_altitude_ft == 30000.0
    assert ac.altitude_ft == original_altitude


def test_apply_speed_command_sets_target_only():
    engine = make_engine()
    ac = spawn_one(engine)
    original_speed = ac.speed_kt

    engine.apply_command(ac.id, SpeedCommand(value=500.0))

    assert ac.target_speed_kt == 500.0
    assert ac.speed_kt == original_speed


def test_apply_route_command_to_unlisted_waypoint_inserts_ahead():
    engine = make_engine()
    ac = spawn_one(engine)
    other_waypoint_id = next(wp_id for wp_id in engine.waypoints if wp_id not in ac.route)

    engine.apply_command(ac.id, RouteCommand(waypoint_id=other_waypoint_id))

    assert ac.route[ac.route_index] == other_waypoint_id


def test_apply_route_command_to_existing_waypoint_jumps_index():
    engine = make_engine()
    ac = spawn_one(engine)
    last_waypoint_id = ac.route[-1]

    engine.apply_command(ac.id, RouteCommand(waypoint_id=last_waypoint_id))

    assert ac.route_index == ac.route.index(last_waypoint_id)


def test_tick_is_noop_when_not_running():
    engine = make_engine()
    ac = spawn_one(engine)
    engine.pause()
    tick_before = engine.tick_count

    engine.tick()

    assert engine.tick_count == tick_before

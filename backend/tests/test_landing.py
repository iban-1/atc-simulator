import pytest

from app.models.aircraft import Aircraft, ConflictStatus, FlightPhase
from app.models.runway import Runway
from app.simulation import constants
from app.simulation.landing import RunwayState, build_landing_queue, land_aircraft, promote_to_approach


def make_aircraft(**overrides) -> Aircraft:
    defaults = dict(
        id="ac-1",
        callsign="SIM100",
        aircraft_type="GX2",
        x=0.0,
        y=0.0,
        altitude_ft=5000.0,
        heading_deg=90.0,
        speed_kt=250.0,
        vertical_speed_fpm=0.0,
        target_heading_deg=90.0,
        target_altitude_ft=5000.0,
        target_speed_kt=250.0,
        origin="wpt-a",
        destination="apt-nova",
        route=["apt-nova"],
        route_index=1,
        phase=FlightPhase.EXITING,
        conflict_status=ConflictStatus.NONE,
        distance_to_destination_nm=5.0,
        eta_minutes=None,
        spawned_at_tick=0,
    )
    defaults.update(overrides)
    return Aircraft(**defaults)


def test_promote_to_approach_when_near_destination_airport():
    ac = make_aircraft(distance_to_destination_nm=5.0)
    promote_to_approach(ac, {"apt-nova"})
    assert ac.phase == FlightPhase.APPROACH


def test_does_not_promote_when_destination_has_no_runway():
    ac = make_aircraft(distance_to_destination_nm=5.0)
    promote_to_approach(ac, set())
    assert ac.phase == FlightPhase.EXITING


def test_does_not_promote_when_too_far_out():
    ac = make_aircraft(distance_to_destination_nm=50.0)
    promote_to_approach(ac, {"apt-nova"})
    assert ac.phase == FlightPhase.EXITING


def test_land_aircraft_success():
    ac = make_aircraft(phase=FlightPhase.APPROACH)
    runway = Runway(id="rwy-1", name="RWY 09", airport_id="apt-nova", heading_deg=90.0)
    state = RunwayState()

    land_aircraft(ac, "rwy-1", {"rwy-1": runway}, state, sim_time_s=100.0)

    assert ac.phase == FlightPhase.LANDING
    assert ac.assigned_runway == "rwy-1"
    assert state.last_landed_at["rwy-1"] == 100.0


def test_land_aircraft_rejects_when_not_on_approach():
    ac = make_aircraft(phase=FlightPhase.CRUISE)
    runway = Runway(id="rwy-1", name="RWY 09", airport_id="apt-nova", heading_deg=90.0)
    state = RunwayState()

    with pytest.raises(ValueError):
        land_aircraft(ac, "rwy-1", {"rwy-1": runway}, state, sim_time_s=100.0)


def test_land_aircraft_rejects_insufficient_spacing():
    runway = Runway(id="rwy-1", name="RWY 09", airport_id="apt-nova", heading_deg=90.0)
    state = RunwayState()
    state.last_landed_at["rwy-1"] = 100.0

    ac = make_aircraft(phase=FlightPhase.APPROACH)

    with pytest.raises(ValueError):
        land_aircraft(ac, "rwy-1", {"rwy-1": runway}, state, sim_time_s=100.0 + constants.MIN_LANDING_SPACING_S - 1)


def test_land_aircraft_rejects_unavailable_runway():
    runway = Runway(id="rwy-1", name="RWY 09", airport_id="apt-nova", heading_deg=90.0)
    state = RunwayState()
    state.unavailable_until["rwy-1"] = 200.0

    ac = make_aircraft(phase=FlightPhase.APPROACH)

    with pytest.raises(ValueError):
        land_aircraft(ac, "rwy-1", {"rwy-1": runway}, state, sim_time_s=100.0)


def test_build_landing_queue_orders_landing_before_approach():
    ac1 = make_aircraft(id="a1", phase=FlightPhase.APPROACH, distance_to_destination_nm=10.0)
    ac2 = make_aircraft(id="a2", phase=FlightPhase.LANDING, assigned_runway="rwy-1", distance_to_destination_nm=1.0)

    queue = build_landing_queue({"a1": ac1, "a2": ac2})

    assert queue[0].aircraft_id == "a2"
    assert queue[0].phase == "landing"
    assert queue[1].aircraft_id == "a1"
    assert queue[1].phase == "approach"

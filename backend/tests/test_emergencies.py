from app.models.aircraft import Aircraft, ConflictStatus, FlightPhase
from app.models.emergency import EmergencyStatus, EmergencyType
from app.models.runway import Runway
from app.services import emergencies


def make_aircraft(**overrides) -> Aircraft:
    defaults = dict(
        id="ac-1",
        callsign="SIM100",
        aircraft_type="GX2",
        x=0.0,
        y=0.0,
        altitude_ft=20000.0,
        heading_deg=90.0,
        speed_kt=400.0,
        vertical_speed_fpm=0.0,
        target_heading_deg=90.0,
        target_altitude_ft=20000.0,
        target_speed_kt=400.0,
        origin="a",
        destination="b",
        route=["b"],
        route_index=0,
        phase=FlightPhase.CRUISE,
        conflict_status=ConflictStatus.NONE,
        distance_to_destination_nm=10.0,
        eta_minutes=None,
        spawned_at_tick=0,
    )
    defaults.update(overrides)
    return Aircraft(**defaults)


def test_maybe_trigger_respects_probability(monkeypatch):
    ac = make_aircraft()
    monkeypatch.setattr(emergencies.random, "random", lambda: 0.999)
    status = emergencies.maybe_trigger_aircraft_emergency(ac, sim_time_s=1000.0, tick=1, last_emergency_time={})
    assert status is None


def test_maybe_trigger_fires_and_sets_cooldown(monkeypatch):
    ac = make_aircraft()
    monkeypatch.setattr(emergencies.random, "random", lambda: 0.0)
    monkeypatch.setattr(emergencies.random, "choice", lambda seq: EmergencyType.ABNORMAL_SPEED)

    last_emergency_time: dict[str, float] = {}
    status = emergencies.maybe_trigger_aircraft_emergency(ac, sim_time_s=1000.0, tick=1, last_emergency_time=last_emergency_time)

    assert status is not None
    assert status.type == EmergencyType.ABNORMAL_SPEED
    assert last_emergency_time["ac-1"] == 1000.0


def test_maybe_trigger_respects_cooldown(monkeypatch):
    ac = make_aircraft()
    monkeypatch.setattr(emergencies.random, "random", lambda: 0.0)
    last_emergency_time = {"ac-1": 990.0}

    status = emergencies.maybe_trigger_aircraft_emergency(ac, sim_time_s=1000.0, tick=1, last_emergency_time=last_emergency_time)

    assert status is None


def test_apply_altitude_control_loss_drifts_target_altitude(monkeypatch):
    ac = make_aircraft(emergency=EmergencyStatus(type=EmergencyType.ALTITUDE_CONTROL_LOSS, message="x", started_at_tick=0))
    monkeypatch.setattr(emergencies.random, "uniform", lambda a, b: 300.0)

    emergencies.apply_emergency_effects(ac, dt=1.0)

    assert ac.target_altitude_ft == 20300.0


def test_apply_effects_noop_without_emergency():
    ac = make_aircraft()
    emergencies.apply_emergency_effects(ac, dt=1.0)
    assert ac.target_altitude_ft == 20000.0
    assert ac.target_speed_kt == 400.0
    assert ac.target_heading_deg == 90.0


def test_maybe_trigger_runway_unavailable(monkeypatch):
    runway = Runway(id="rwy-1", name="RWY 09", airport_id="apt-nova", heading_deg=90.0)
    monkeypatch.setattr(emergencies.random, "random", lambda: 0.0)
    monkeypatch.setattr(emergencies.random, "choice", lambda seq: runway)

    unavailable_until: dict[str, float] = {}
    result = emergencies.maybe_trigger_runway_unavailable([runway], sim_time_s=500.0, tick=1, last_runway_emergency_time={}, unavailable_until=unavailable_until)

    assert result is not None
    returned_runway, status = result
    assert returned_runway is runway
    assert status.type.value == "runway_unavailable"
    assert unavailable_until["rwy-1"] == 500.0 + emergencies.RUNWAY_UNAVAILABLE_DURATION_S

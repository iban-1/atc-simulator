from app.conflict.detector import detect_conflicts
from app.models.aircraft import Aircraft, FlightPhase, ConflictStatus


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


def test_detects_head_on_pair_within_lookahead():
    # Same altitude, flying directly at each other, close enough to collide soon.
    a = make_aircraft(id="a", x=-5.0, y=0.0, heading_deg=90.0, target_heading_deg=90.0, speed_kt=360.0, target_speed_kt=360.0)
    b = make_aircraft(id="b", x=5.0, y=0.0, heading_deg=270.0, target_heading_deg=270.0, speed_kt=360.0, target_speed_kt=360.0)

    warnings = detect_conflicts({"a": a, "b": b})

    assert len(warnings) == 1
    w = warnings[0]
    assert {w.aircraft_a, w.aircraft_b} == {"a", "b"}
    assert w.risk_level in ("caution", "warning", "violation")


def test_ignores_well_separated_pair():
    a = make_aircraft(id="a", x=0.0, y=0.0, heading_deg=90.0, target_heading_deg=90.0)
    b = make_aircraft(id="b", x=0.0, y=50.0, heading_deg=90.0, target_heading_deg=90.0)

    warnings = detect_conflicts({"a": a, "b": b})

    assert warnings == []


def test_ignores_pair_with_safe_vertical_separation():
    a = make_aircraft(id="a", x=0.0, y=0.0, altitude_ft=20000.0, heading_deg=90.0, target_heading_deg=90.0)
    b = make_aircraft(id="b", x=1.0, y=0.0, altitude_ft=25000.0, heading_deg=270.0, target_heading_deg=270.0)

    warnings = detect_conflicts({"a": a, "b": b})

    assert warnings == []


def test_flags_active_violation_when_already_too_close():
    a = make_aircraft(id="a", x=0.0, y=0.0, heading_deg=0.0, target_heading_deg=0.0, speed_kt=300.0, target_speed_kt=300.0)
    b = make_aircraft(id="b", x=1.0, y=0.0, heading_deg=180.0, target_heading_deg=180.0, speed_kt=300.0, target_speed_kt=300.0)

    warnings = detect_conflicts({"a": a, "b": b})

    assert len(warnings) == 1
    assert warnings[0].is_active_violation is True
    assert warnings[0].risk_level == "violation"

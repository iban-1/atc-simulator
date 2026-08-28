from app.game.scoring import CLEAN_EXIT_POINTS, CORRECT_REQUEST_POINTS, EXCURSION_PENALTY, VIOLATION_PENALTY, ScoreTracker
from app.models.aircraft import Aircraft, ConflictStatus, FlightPhase
from app.models.messages import ConflictWarning


def make_aircraft(id_) -> Aircraft:
    return Aircraft(
        id=id_,
        callsign=f"SIM{id_}",
        aircraft_type="GX2",
        x=0.0,
        y=0.0,
        altitude_ft=20000.0,
        heading_deg=0.0,
        speed_kt=400.0,
        vertical_speed_fpm=0.0,
        target_heading_deg=0.0,
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


def make_warning(a, b, is_violation, risk="violation") -> ConflictWarning:
    return ConflictWarning(
        aircraft_a=a,
        aircraft_b=b,
        time_to_conflict_s=0.0,
        predicted_separation_nm=0.5,
        vertical_separation_ft=0.0,
        risk_level=risk,
        is_active_violation=is_violation,
    )


def test_clean_exit_awards_points_and_marks_safe():
    tracker = ScoreTracker()
    ac = make_aircraft("1")

    tracker.record_clean_exit(ac, delay_s=5.0)

    assert tracker.state.score == CLEAN_EXIT_POINTS
    assert tracker.state.aircraft_handled == 1
    assert tracker.state.aircraft_safe == 1


def test_clean_exit_after_violation_does_not_count_as_safe():
    tracker = ScoreTracker()
    ac = make_aircraft("1")
    tracker.update_conflicts([make_warning("1", "2", is_violation=True)])

    tracker.record_clean_exit(ac, delay_s=0.0)

    # violation penalty applied, but no clean-exit bonus since aircraft "1" violated
    assert tracker.state.score == VIOLATION_PENALTY
    assert tracker.state.aircraft_handled == 1
    assert tracker.state.aircraft_safe == 0


def test_excursion_applies_penalty_and_still_counts_as_handled():
    tracker = ScoreTracker()
    ac = make_aircraft("1")

    tracker.record_excursion(ac, delay_s=0.0)

    assert tracker.state.score == EXCURSION_PENALTY
    assert tracker.state.aircraft_handled == 1
    assert tracker.state.aircraft_safe == 0


def test_request_approved_awards_points():
    tracker = ScoreTracker()
    tracker.record_request_approved()
    assert tracker.state.score == CORRECT_REQUEST_POINTS


def test_violation_penalized_once_per_episode_not_every_tick():
    tracker = ScoreTracker()
    warning = make_warning("1", "2", is_violation=True)

    tracker.update_conflicts([warning])
    tracker.update_conflicts([warning])
    tracker.update_conflicts([warning])

    assert tracker.state.separation_violations == 1
    assert tracker.state.score == VIOLATION_PENALTY


def test_violation_penalized_again_after_resolving_and_recurring():
    tracker = ScoreTracker()
    warning = make_warning("1", "2", is_violation=True)

    tracker.update_conflicts([warning])
    tracker.update_conflicts([])  # separation resolved
    tracker.update_conflicts([warning])  # violates again -> new episode

    assert tracker.state.separation_violations == 2
    assert tracker.state.score == VIOLATION_PENALTY * 2


def test_conflicts_detected_counts_distinct_pairs_once_while_ongoing():
    tracker = ScoreTracker()
    caution = make_warning("1", "2", is_violation=False, risk="caution")

    tracker.update_conflicts([caution])
    tracker.update_conflicts([caution])

    assert tracker.state.conflicts_detected == 1


def test_average_delay_accumulates_across_multiple_records():
    tracker = ScoreTracker()
    tracker.record_clean_exit(make_aircraft("1"), delay_s=10.0)
    tracker.record_clean_exit(make_aircraft("2"), delay_s=20.0)

    assert tracker.state.average_delay_s == 15.0

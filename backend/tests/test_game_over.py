from app.game.game_over import MAX_SEPARATION_VIOLATIONS, check_collision, check_game_over
from app.models.messages import ConflictWarning, ScoreState


def make_warning(is_violation, sep_nm=0.5, vert_ft=0.0) -> ConflictWarning:
    return ConflictWarning(
        aircraft_a="a",
        aircraft_b="b",
        time_to_conflict_s=0.0,
        predicted_separation_nm=sep_nm,
        vertical_separation_ft=vert_ft,
        risk_level="violation" if is_violation else "caution",
        is_active_violation=is_violation,
    )


def test_check_collision_true_when_very_close_and_active_violation():
    warning = make_warning(is_violation=True, sep_nm=0.3, vert_ft=50.0)
    assert check_collision([warning]) is True


def test_check_collision_false_when_not_active_violation():
    warning = make_warning(is_violation=False, sep_nm=0.1, vert_ft=10.0)
    assert check_collision([warning]) is False


def test_check_collision_false_when_far_enough_apart():
    warning = make_warning(is_violation=True, sep_nm=5.0, vert_ft=0.0)
    assert check_collision([warning]) is False


def test_check_collision_false_when_vertically_separated():
    warning = make_warning(is_violation=True, sep_nm=0.2, vert_ft=1000.0)
    assert check_collision([warning]) is False


def test_game_over_none_when_nothing_triggered():
    state = ScoreState(aircraft_handled=2, aircraft_safe=2, separation_violations=0)
    result = check_game_over(state, [], aircraft_handled_target=10)
    assert result is None


def test_game_over_collision_takes_priority():
    state = ScoreState(aircraft_handled=1, separation_violations=1)
    warning = make_warning(is_violation=True, sep_nm=0.1, vert_ft=0.0)
    result = check_game_over(state, [warning], aircraft_handled_target=10)
    assert result.reason == "collision"


def test_game_over_too_many_violations():
    state = ScoreState(separation_violations=MAX_SEPARATION_VIOLATIONS)
    result = check_game_over(state, [], aircraft_handled_target=10)
    assert result.reason == "too_many_violations"


def test_game_over_objective_complete_when_all_handled_safely():
    state = ScoreState(aircraft_handled=8, aircraft_safe=8)
    result = check_game_over(state, [], aircraft_handled_target=8)
    assert result.reason == "objective_complete"


def test_game_over_objective_failed_when_handled_but_not_all_safe():
    state = ScoreState(aircraft_handled=8, aircraft_safe=6)
    result = check_game_over(state, [], aircraft_handled_target=8)
    assert result.reason == "objective_failed"

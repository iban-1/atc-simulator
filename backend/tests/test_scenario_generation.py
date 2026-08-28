from app.scenarios.registry import SCENARIOS, get_scenario, list_scenarios

EXPECTED_SCENARIO_IDS = {
    "quiet-airspace",
    "normal-traffic",
    "busy-airspace",
    "heavy-traffic",
    "conflict-challenge",
    "emergency-challenge",
}


def test_registry_contains_all_six_scenarios():
    ids = {s.id for s in list_scenarios()}
    assert ids == EXPECTED_SCENARIO_IDS


def test_get_scenario_returns_none_for_unknown_id():
    assert get_scenario("does-not-exist") is None


def test_get_scenario_matches_registry_key():
    for scenario_id, scenario in SCENARIOS.items():
        assert get_scenario(scenario_id) is scenario


def test_every_scenario_has_valid_shape():
    for scenario in list_scenarios():
        assert 1 <= scenario.difficulty <= 5
        assert len(scenario.waypoints) > 0
        assert len(scenario.routes) > 0
        assert scenario.max_concurrent_aircraft > 0
        assert scenario.spawn_interval_s > 0
        assert scenario.total_aircraft_target > 0
        assert scenario.objective_description

        min_x, min_y, max_x, max_y = scenario.airspace_bounds
        assert min_x < max_x
        assert min_y < max_y


def test_every_route_waypoint_id_resolves_to_a_real_waypoint():
    for scenario in list_scenarios():
        waypoint_ids = {wp.id for wp in scenario.waypoints}
        for route in scenario.routes:
            assert len(route.waypoint_ids) >= 1, f"{scenario.id}/{route.id} has no waypoints"
            for wp_id in route.waypoint_ids:
                assert wp_id in waypoint_ids, f"{scenario.id}/{route.id} references unknown waypoint {wp_id}"


def test_every_runway_references_a_real_airport_waypoint():
    for scenario in list_scenarios():
        airport_ids = {wp.id for wp in scenario.waypoints if wp.kind == "airport"}
        for runway in scenario.runways:
            assert runway.airport_id in airport_ids, f"{scenario.id}/{runway.id} references unknown airport {runway.airport_id}"


def test_emergencies_only_enabled_where_expected():
    for scenario in list_scenarios():
        if scenario.id == "emergency-challenge":
            assert scenario.emergencies_enabled is True
        else:
            assert scenario.emergencies_enabled is False

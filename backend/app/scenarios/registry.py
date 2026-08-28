from app.models.scenario import ScenarioConfig
from app.scenarios.busy_airspace import BUSY_AIRSPACE
from app.scenarios.conflict_challenge import CONFLICT_CHALLENGE
from app.scenarios.emergency_challenge import EMERGENCY_CHALLENGE
from app.scenarios.heavy_traffic import HEAVY_TRAFFIC
from app.scenarios.normal_traffic import NORMAL_TRAFFIC
from app.scenarios.quiet_airspace import QUIET_AIRSPACE

SCENARIOS: dict[str, ScenarioConfig] = {
    scenario.id: scenario
    for scenario in [
        QUIET_AIRSPACE,
        NORMAL_TRAFFIC,
        BUSY_AIRSPACE,
        HEAVY_TRAFFIC,
        CONFLICT_CHALLENGE,
        EMERGENCY_CHALLENGE,
    ]
}


def get_scenario(scenario_id: str) -> ScenarioConfig | None:
    return SCENARIOS.get(scenario_id)


def list_scenarios() -> list[ScenarioConfig]:
    return list(SCENARIOS.values())

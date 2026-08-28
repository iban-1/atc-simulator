from fastapi import APIRouter, HTTPException, Request

from app.scenarios.registry import get_scenario, list_scenarios

router = APIRouter()


@router.get("/api/scenarios")
async def get_scenarios(request: Request) -> list[dict]:
    progression = request.app.state.progression
    result = []
    for scenario in list_scenarios():
        data = scenario.model_dump(mode="json")
        data["unlocked"] = scenario.difficulty <= progression.highest_difficulty_completed + 1
        result.append(data)
    return result


@router.post("/api/scenarios/{scenario_id}/start")
async def start_scenario(scenario_id: str, request: Request) -> dict:
    scenario = get_scenario(scenario_id)
    if scenario is None:
        raise HTTPException(status_code=404, detail=f"Unknown scenario: {scenario_id}")

    progression = request.app.state.progression
    if scenario.difficulty > progression.highest_difficulty_completed + 1:
        raise HTTPException(status_code=403, detail=f"Scenario {scenario_id} is not yet unlocked")

    session = request.app.state.session
    session.set_scenario(scenario_id)
    session.engine.start()

    await session.manager.broadcast(session.build_full_snapshot())
    return session.build_full_snapshot()

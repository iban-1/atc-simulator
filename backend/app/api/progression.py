from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/api/progression")
async def get_progression(request: Request) -> dict:
    return request.app.state.progression.model_dump(mode="json")

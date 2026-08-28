from pydantic import BaseModel


class Route(BaseModel):
    id: str
    waypoint_ids: list[str]

from typing import Literal

from pydantic import BaseModel


class Waypoint(BaseModel):
    id: str
    name: str
    x: float
    y: float
    kind: Literal["waypoint", "airport"]

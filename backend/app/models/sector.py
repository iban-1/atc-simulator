# Stub model — sector boundaries/density are Phase 2 scope. Defined now so the
# folder structure and imports are stable across phases.
from pydantic import BaseModel


class Sector(BaseModel):
    id: str
    name: str
    boundary: list[tuple[float, float]]

from pydantic import BaseModel


class Runway(BaseModel):
    id: str
    name: str
    airport_id: str
    heading_deg: float

from enum import Enum
from typing import Literal, Union

from pydantic import BaseModel, Field

from app.models.emergency import EmergencyStatus


class FlightPhase(str, Enum):
    ENTERING = "entering"
    CRUISE = "cruise"
    CLIMBING = "climbing"
    DESCENDING = "descending"
    APPROACH = "approach"
    LANDING = "landing"
    LANDED = "landed"
    EXITING = "exiting"
    EXITED = "exited"


class ConflictStatus(str, Enum):
    NONE = "none"
    CAUTION = "caution"
    WARNING = "warning"


class HeadingCommand(BaseModel):
    kind: Literal["heading"] = "heading"
    value: float = Field(ge=0, lt=360)


class AltitudeCommand(BaseModel):
    kind: Literal["altitude"] = "altitude"
    value: float = Field(ge=0, le=45000)


class SpeedCommand(BaseModel):
    kind: Literal["speed"] = "speed"
    value: float = Field(ge=100, le=600)


class RouteCommand(BaseModel):
    kind: Literal["route"] = "route"
    waypoint_id: str


class LandCommand(BaseModel):
    kind: Literal["land"] = "land"
    runway_id: str


Command = Union[HeadingCommand, AltitudeCommand, SpeedCommand, RouteCommand, LandCommand]


class Aircraft(BaseModel):
    id: str
    callsign: str
    aircraft_type: str

    x: float
    y: float
    altitude_ft: float
    heading_deg: float
    speed_kt: float
    vertical_speed_fpm: float

    target_heading_deg: float
    target_altitude_ft: float
    target_speed_kt: float

    origin: str
    destination: str
    route: list[str]
    route_index: int

    phase: FlightPhase
    conflict_status: ConflictStatus = ConflictStatus.NONE

    distance_to_destination_nm: float
    eta_minutes: float | None

    spawned_at_tick: int

    assigned_runway: str | None = None
    emergency: EmergencyStatus | None = None

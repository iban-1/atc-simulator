# Fictional, simplified emergency game mechanics — not real aviation
# emergency procedures. Only used when a scenario opts in via
# ScenarioConfig.emergencies_enabled.
from enum import Enum

from pydantic import BaseModel


class EmergencyType(str, Enum):
    ALTITUDE_CONTROL_LOSS = "altitude_control_loss"
    PRIORITY_LANDING = "priority_landing"
    ABNORMAL_SPEED = "abnormal_speed"
    RUNWAY_UNAVAILABLE = "runway_unavailable"
    ROUTE_DEVIATION = "route_deviation"


class EmergencyStatus(BaseModel):
    type: EmergencyType
    message: str
    started_at_tick: int

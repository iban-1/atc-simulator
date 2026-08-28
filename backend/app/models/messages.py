from typing import Literal, Union

from pydantic import BaseModel, ConfigDict, Field

from app.models.aircraft import Aircraft, Command
from app.models.route import Route
from app.models.scenario import ScenarioConfig
from app.models.waypoint import Waypoint


class ConflictWarning(BaseModel):
    aircraft_a: str
    aircraft_b: str
    time_to_conflict_s: float
    predicted_separation_nm: float
    vertical_separation_ft: float
    risk_level: Literal["caution", "warning", "violation"]
    is_active_violation: bool


class PilotRequest(BaseModel):
    id: str
    aircraft_id: str
    callsign: str
    message: str
    suggested_command: Command
    created_at_tick: int
    status: Literal["pending", "approved", "denied"] = "pending"


class SectorStatus(BaseModel):
    id: str
    name: str
    aircraft_count: int
    density: Literal["low", "medium", "high"]


class LandingQueueEntry(BaseModel):
    runway_id: str
    aircraft_id: str
    callsign: str
    position: int
    phase: Literal["approach", "landing"]


class ScoreState(BaseModel):
    score: int = 0
    aircraft_handled: int = 0
    aircraft_safe: int = 0
    conflicts_detected: int = 0
    separation_violations: int = 0
    average_delay_s: float = 0.0


class CommsMessage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    from_: str = Field(alias="from")
    text: str
    kind: Literal["pilot_request", "pilot_report", "controller_response"]
    created_at_tick: int


class StateUpdate(BaseModel):
    type: Literal["state_update"] = "state_update"
    tick: int
    sim_time_s: float
    status: Literal["stopped", "running", "paused"]
    speed_multiplier: int
    aircraft: list[Aircraft]
    conflicts: list[ConflictWarning]
    score: ScoreState
    pending_requests: list[PilotRequest]
    sectors: list[SectorStatus] = []
    landing_queue: list[LandingQueueEntry] = []


class FullSnapshot(BaseModel):
    type: Literal["full_snapshot"] = "full_snapshot"
    scenario: ScenarioConfig
    waypoints: list[Waypoint]
    routes: list[Route]
    airspace_bounds: tuple[float, float, float, float]
    state_update: StateUpdate


class CommsMessageEnvelope(BaseModel):
    type: Literal["comms_message"] = "comms_message"
    message: CommsMessage


class GameOverMessage(BaseModel):
    type: Literal["game_over"] = "game_over"
    reason: Literal["objective_failed", "too_many_violations", "collision", "objective_complete"]
    results: ScoreState


class ErrorMessage(BaseModel):
    type: Literal["error"] = "error"
    message: str


# --- Client -> Server ---


class CommandEnvelope(BaseModel):
    type: Literal["command"] = "command"
    aircraft_id: str
    command: Command


class ApproveRequestEnvelope(BaseModel):
    type: Literal["approve_request"] = "approve_request"
    request_id: str


class DenyRequestEnvelope(BaseModel):
    type: Literal["deny_request"] = "deny_request"
    request_id: str


class SimControlEnvelope(BaseModel):
    type: Literal["sim_control"] = "sim_control"
    action: Literal["start", "pause", "resume", "restart"]


class SetSpeedEnvelope(BaseModel):
    type: Literal["set_speed"] = "set_speed"
    multiplier: Literal[1, 2, 5]


ClientMessage = Union[
    CommandEnvelope,
    ApproveRequestEnvelope,
    DenyRequestEnvelope,
    SimControlEnvelope,
    SetSpeedEnvelope,
]

from pydantic import BaseModel


class GameHistoryEntry(BaseModel):
    scenario_id: str
    scenario_name: str
    difficulty: int
    score: int
    aircraft_handled: int
    aircraft_safe: int
    conflicts_detected: int
    separation_violations: int
    average_delay_s: float
    objective_completed: bool
    played_at_s: float


class ProgressionRecord(BaseModel):
    best_score: int = 0
    highest_difficulty_completed: int = 0
    total_aircraft_safely_handled: int = 0
    total_play_time_s: float = 0.0
    total_conflicts_avoided: int = 0
    games_played: int = 0
    average_score: float = 0.0
    history: list[GameHistoryEntry] = []

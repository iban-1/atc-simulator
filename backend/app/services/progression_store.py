import json
import time
from pathlib import Path

from app.models.progression import GameHistoryEntry, ProgressionRecord

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "simulated"
PROGRESSION_FILE = DATA_DIR / "progression.json"

MAX_HISTORY_ENTRIES = 50


def load_progression() -> ProgressionRecord:
    if not PROGRESSION_FILE.exists():
        return ProgressionRecord()
    try:
        data = json.loads(PROGRESSION_FILE.read_text(encoding="utf-8"))
        return ProgressionRecord.model_validate(data)
    except (json.JSONDecodeError, ValueError):
        return ProgressionRecord()


def save_progression(record: ProgressionRecord) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROGRESSION_FILE.write_text(json.dumps(record.model_dump(), indent=2), encoding="utf-8")


def record_game_result(
    record: ProgressionRecord,
    score: int,
    scenario_id: str,
    scenario_name: str,
    difficulty: int,
    aircraft_handled: int,
    aircraft_safe: int,
    conflicts_detected: int,
    separation_violations: int,
    average_delay_s: float,
    conflicts_avoided: int,
    play_time_s: float,
    objective_completed: bool,
) -> ProgressionRecord:
    record.games_played += 1
    record.best_score = max(record.best_score, score)
    if objective_completed:
        record.highest_difficulty_completed = max(record.highest_difficulty_completed, difficulty)
    record.total_aircraft_safely_handled += aircraft_safe
    record.total_play_time_s += play_time_s
    record.total_conflicts_avoided += conflicts_avoided
    total_score = record.average_score * (record.games_played - 1) + score
    record.average_score = total_score / record.games_played

    record.history.append(
        GameHistoryEntry(
            scenario_id=scenario_id,
            scenario_name=scenario_name,
            difficulty=difficulty,
            score=score,
            aircraft_handled=aircraft_handled,
            aircraft_safe=aircraft_safe,
            conflicts_detected=conflicts_detected,
            separation_violations=separation_violations,
            average_delay_s=average_delay_s,
            objective_completed=objective_completed,
            played_at_s=time.time(),
        )
    )
    record.history = record.history[-MAX_HISTORY_ENTRIES:]

    return record

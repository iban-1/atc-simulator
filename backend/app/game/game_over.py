"""Fictional game-over conditions for Phase 1's single scenario."""

from dataclasses import dataclass
from typing import Literal

from app.models.aircraft import Aircraft
from app.models.messages import ConflictWarning, ScoreState

MAX_SEPARATION_VIOLATIONS = 5
COLLISION_HORIZONTAL_NM = 1.0
COLLISION_VERTICAL_FT = 200.0

GameOverReason = Literal["objective_failed", "too_many_violations", "collision", "objective_complete"]


@dataclass
class GameOverResult:
    reason: GameOverReason
    results: ScoreState


def check_collision(conflicts: list[ConflictWarning]) -> bool:
    return any(
        w.is_active_violation
        and w.predicted_separation_nm < COLLISION_HORIZONTAL_NM
        and w.vertical_separation_ft < COLLISION_VERTICAL_FT
        for w in conflicts
    )


def check_game_over(
    score_state: ScoreState,
    conflicts: list[ConflictWarning],
    aircraft_handled_target: int,
) -> GameOverResult | None:
    if check_collision(conflicts):
        return GameOverResult(reason="collision", results=score_state)

    if score_state.separation_violations >= MAX_SEPARATION_VIOLATIONS:
        return GameOverResult(reason="too_many_violations", results=score_state)

    if score_state.aircraft_handled >= aircraft_handled_target:
        if score_state.aircraft_safe >= aircraft_handled_target:
            return GameOverResult(reason="objective_complete", results=score_state)
        return GameOverResult(reason="objective_failed", results=score_state)

    return None

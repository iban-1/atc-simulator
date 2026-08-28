"""Phase 1 scoring rules — simplified, fictional game mechanics.

Points:
  +50  aircraft exits airspace cleanly via its destination, never violated
  +10  pilot request correctly actioned (approved) by the controller
 -100  a new separation-violation episode begins between a pair of aircraft
  -25  aircraft exits the airspace boundary without reaching its destination
       (treated as an airspace excursion)
"""

from dataclasses import dataclass, field

from app.models.aircraft import Aircraft
from app.models.messages import ConflictWarning, ScoreState

CLEAN_EXIT_POINTS = 50
CORRECT_REQUEST_POINTS = 10
VIOLATION_PENALTY = -100
EXCURSION_PENALTY = -25


@dataclass
class ScoreTracker:
    state: ScoreState = field(default_factory=ScoreState)
    _active_violation_pairs: set[frozenset[str]] = field(default_factory=set)
    _active_conflict_pairs: set[frozenset[str]] = field(default_factory=set)
    _violated_aircraft_ids: set[str] = field(default_factory=set)
    _delay_total_s: float = 0.0
    _delay_samples: int = 0

    def update_conflicts(self, conflicts: list[ConflictWarning]) -> None:
        current_conflict_pairs: set[frozenset[str]] = set()
        current_violation_pairs: set[frozenset[str]] = set()

        for w in conflicts:
            pair = frozenset((w.aircraft_a, w.aircraft_b))
            current_conflict_pairs.add(pair)
            if w.is_active_violation:
                current_violation_pairs.add(pair)
                self._violated_aircraft_ids.add(w.aircraft_a)
                self._violated_aircraft_ids.add(w.aircraft_b)

        newly_seen = current_conflict_pairs - self._active_conflict_pairs
        self.state.conflicts_detected += len(newly_seen)
        self._active_conflict_pairs = current_conflict_pairs

        newly_violated = current_violation_pairs - self._active_violation_pairs
        if newly_violated:
            self.state.separation_violations += len(newly_violated)
            self.state.score += VIOLATION_PENALTY * len(newly_violated)
        self._active_violation_pairs = current_violation_pairs

    def record_clean_exit(self, ac: Aircraft, delay_s: float) -> None:
        self.state.aircraft_handled += 1
        self._record_delay(delay_s)
        if ac.id in self._violated_aircraft_ids:
            return
        self.state.aircraft_safe += 1
        self.state.score += CLEAN_EXIT_POINTS

    def record_excursion(self, ac: Aircraft, delay_s: float) -> None:
        self.state.aircraft_handled += 1
        self._record_delay(delay_s)
        self.state.score += EXCURSION_PENALTY

    def record_request_approved(self) -> None:
        self.state.score += CORRECT_REQUEST_POINTS

    def _record_delay(self, delay_s: float) -> None:
        self._delay_total_s += max(0.0, delay_s)
        self._delay_samples += 1
        self.state.average_delay_s = self._delay_total_s / self._delay_samples

    def has_violation_history(self, aircraft_id: str) -> bool:
        return aircraft_id in self._violated_aircraft_ids

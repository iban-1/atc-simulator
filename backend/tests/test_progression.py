from app.models.progression import ProgressionRecord
from app.services import progression_store


def record_result(record, **overrides):
    defaults = dict(
        score=100,
        scenario_id="quiet-airspace",
        scenario_name="Quiet Airspace",
        difficulty=1,
        aircraft_handled=6,
        aircraft_safe=5,
        conflicts_detected=3,
        separation_violations=0,
        average_delay_s=2.5,
        conflicts_avoided=2,
        play_time_s=60.0,
        objective_completed=True,
    )
    defaults.update(overrides)
    return progression_store.record_game_result(record, **defaults)


def test_record_game_result_tracks_best_score_and_average():
    record = ProgressionRecord()

    record_result(record, score=100, difficulty=1, aircraft_safe=5, conflicts_avoided=2, play_time_s=60.0, objective_completed=True)
    assert record.games_played == 1
    assert record.best_score == 100
    assert record.average_score == 100.0
    assert record.highest_difficulty_completed == 1

    record_result(
        record,
        score=50,
        scenario_id="normal-traffic",
        scenario_name="Normal Traffic",
        difficulty=2,
        aircraft_safe=3,
        conflicts_avoided=1,
        play_time_s=30.0,
        objective_completed=False,
    )
    assert record.games_played == 2
    assert record.best_score == 100
    assert record.average_score == 75.0
    # objective not completed on the difficulty-2 attempt, so it should not count
    assert record.highest_difficulty_completed == 1
    assert record.total_aircraft_safely_handled == 8
    assert record.total_conflicts_avoided == 3
    assert record.total_play_time_s == 90.0


def test_record_game_result_appends_history_entry():
    record = ProgressionRecord()
    record_result(record, score=123, scenario_id="busy-airspace", scenario_name="Busy Airspace", difficulty=3)

    assert len(record.history) == 1
    entry = record.history[0]
    assert entry.scenario_id == "busy-airspace"
    assert entry.scenario_name == "Busy Airspace"
    assert entry.difficulty == 3
    assert entry.score == 123
    assert entry.played_at_s > 0


def test_record_game_result_caps_history_length():
    record = ProgressionRecord()
    for i in range(progression_store.MAX_HISTORY_ENTRIES + 10):
        record_result(record, score=i)

    assert len(record.history) == progression_store.MAX_HISTORY_ENTRIES
    # oldest entries should have been dropped, newest kept
    assert record.history[-1].score == progression_store.MAX_HISTORY_ENTRIES + 9


def test_save_and_load_roundtrip(tmp_path, monkeypatch):
    data_dir = tmp_path / "simulated"
    progression_file = data_dir / "progression.json"
    monkeypatch.setattr(progression_store, "DATA_DIR", data_dir)
    monkeypatch.setattr(progression_store, "PROGRESSION_FILE", progression_file)

    record = ProgressionRecord(best_score=42, highest_difficulty_completed=2, games_played=3)
    progression_store.save_progression(record)

    loaded = progression_store.load_progression()
    assert loaded.best_score == 42
    assert loaded.highest_difficulty_completed == 2
    assert loaded.games_played == 3


def test_load_progression_returns_default_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(progression_store, "PROGRESSION_FILE", tmp_path / "does_not_exist.json")
    record = progression_store.load_progression()
    assert record == ProgressionRecord()

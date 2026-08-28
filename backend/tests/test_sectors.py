from app.models.aircraft import Aircraft, ConflictStatus, FlightPhase
from app.models.sector import Sector
from app.simulation.sectors import compute_sector_stats


def make_aircraft(id_, x, y) -> Aircraft:
    return Aircraft(
        id=id_,
        callsign=f"SIM{id_}",
        aircraft_type="GX2",
        x=x,
        y=y,
        altitude_ft=20000.0,
        heading_deg=0.0,
        speed_kt=400.0,
        vertical_speed_fpm=0.0,
        target_heading_deg=0.0,
        target_altitude_ft=20000.0,
        target_speed_kt=400.0,
        origin="a",
        destination="b",
        route=["b"],
        route_index=0,
        phase=FlightPhase.CRUISE,
        conflict_status=ConflictStatus.NONE,
        distance_to_destination_nm=10.0,
        eta_minutes=None,
        spawned_at_tick=0,
    )


def test_counts_aircraft_within_sector_boundary():
    north = Sector(id="north", name="NORTH", boundary=[(-10.0, 0.0), (10.0, 0.0), (10.0, 10.0), (-10.0, 10.0)])
    south = Sector(id="south", name="SOUTH", boundary=[(-10.0, -10.0), (10.0, -10.0), (10.0, 0.0), (-10.0, 0.0)])

    aircraft = {
        "1": make_aircraft("1", 0.0, 5.0),
        "2": make_aircraft("2", 0.0, 5.0),
        "3": make_aircraft("3", 0.0, -5.0),
    }

    stats = compute_sector_stats(aircraft, [north, south])
    by_id = {s.id: s for s in stats}

    assert by_id["north"].aircraft_count == 2
    assert by_id["south"].aircraft_count == 1


def test_density_labels_scale_with_count():
    sector = Sector(id="s", name="S", boundary=[(-100.0, -100.0), (100.0, -100.0), (100.0, 100.0), (-100.0, 100.0)])

    empty_stats = compute_sector_stats({}, [sector])
    assert empty_stats[0].density == "low"

    many_aircraft = {str(i): make_aircraft(str(i), 0.0, 0.0) for i in range(10)}
    busy_stats = compute_sector_stats(many_aircraft, [sector])
    assert busy_stats[0].density == "high"

import math

from app.simulation.geometry import bearing_to, distance_xy, shortest_angle_delta, velocity_vector


def test_distance_xy_pythagorean():
    assert distance_xy(0.0, 0.0, 3.0, 4.0) == 5.0


def test_distance_xy_zero_for_same_point():
    assert distance_xy(10.0, -5.0, 10.0, -5.0) == 0.0


def test_bearing_to_north():
    assert math.isclose(bearing_to(0.0, 0.0, 0.0, 10.0), 0.0, abs_tol=1e-6)


def test_bearing_to_east():
    assert math.isclose(bearing_to(0.0, 0.0, 10.0, 0.0), 90.0, abs_tol=1e-6)


def test_bearing_to_south():
    assert math.isclose(bearing_to(0.0, 0.0, 0.0, -10.0), 180.0, abs_tol=1e-6)


def test_bearing_to_west():
    assert math.isclose(bearing_to(0.0, 0.0, -10.0, 0.0), 270.0, abs_tol=1e-6)


def test_shortest_angle_delta_simple_right_turn():
    assert shortest_angle_delta(0.0, 90.0) == 90.0


def test_shortest_angle_delta_simple_left_turn():
    assert shortest_angle_delta(90.0, 0.0) == -90.0


def test_shortest_angle_delta_wraps_around_0_360_boundary():
    # From 350 to 10 is a 20 degree right turn, not a 340 degree left turn.
    assert math.isclose(shortest_angle_delta(350.0, 10.0), 20.0, abs_tol=1e-6)


def test_shortest_angle_delta_wraps_the_other_direction():
    # From 10 to 350 is a 20 degree left turn.
    assert math.isclose(shortest_angle_delta(10.0, 350.0), -20.0, abs_tol=1e-6)


def test_shortest_angle_delta_zero_when_already_on_heading():
    assert shortest_angle_delta(123.0, 123.0) == 0.0


def test_velocity_vector_magnitude_matches_speed_in_nm_per_second():
    vx, vy = velocity_vector(heading_deg=90.0, speed_kt=3600.0)
    speed_nm_per_s = math.hypot(vx, vy)
    assert math.isclose(speed_nm_per_s, 1.0, abs_tol=1e-6)  # 3600 kt = 1 NM/s


def test_velocity_vector_east_heading_is_positive_x():
    vx, vy = velocity_vector(heading_deg=90.0, speed_kt=360.0)
    assert vx > 0
    assert math.isclose(vy, 0.0, abs_tol=1e-9)


def test_velocity_vector_north_heading_is_positive_y():
    vx, vy = velocity_vector(heading_deg=0.0, speed_kt=360.0)
    assert math.isclose(vx, 0.0, abs_tol=1e-9)
    assert vy > 0

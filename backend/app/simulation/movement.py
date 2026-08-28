from app.models.aircraft import Aircraft, FlightPhase
from app.models.waypoint import Waypoint
from app.simulation import constants
from app.simulation.geometry import bearing_to, distance_xy, shortest_angle_delta, velocity_vector


def step_aircraft(
    ac: Aircraft,
    dt: float,
    waypoints: dict[str, Waypoint],
    bounds: tuple[float, float, float, float],
) -> None:
    if ac.phase == FlightPhase.EXITED:
        return

    _turn_toward_target(ac, dt)
    _adjust_altitude_toward_target(ac, dt)
    _adjust_speed_toward_target(ac, dt)
    _integrate_position(ac, dt)
    _advance_route_if_at_waypoint(ac, waypoints)
    _update_distance_and_eta(ac, waypoints)
    _update_phase(ac)
    _mark_exited_if_out_of_bounds(ac, bounds, waypoints)


def _turn_toward_target(ac: Aircraft, dt: float) -> None:
    delta = shortest_angle_delta(ac.heading_deg, ac.target_heading_deg)
    max_turn = constants.TURN_RATE_DEG_PER_SEC * dt
    step = max(-max_turn, min(max_turn, delta))
    ac.heading_deg = (ac.heading_deg + step) % 360.0


def _adjust_altitude_toward_target(ac: Aircraft, dt: float) -> None:
    delta = ac.target_altitude_ft - ac.altitude_ft
    if abs(delta) < 1e-6:
        ac.vertical_speed_fpm = 0.0
        return
    rate = constants.CLIMB_RATE_FPM if delta > 0 else -constants.DESCEND_RATE_FPM
    max_step_ft = abs(rate) * (dt / 60.0)
    step = max(-max_step_ft, min(max_step_ft, delta))
    ac.altitude_ft += step
    ac.vertical_speed_fpm = rate if abs(step) > 1e-6 else 0.0


def _adjust_speed_toward_target(ac: Aircraft, dt: float) -> None:
    delta = ac.target_speed_kt - ac.speed_kt
    max_step = constants.ACCEL_KT_PER_SEC * dt
    step = max(-max_step, min(max_step, delta))
    ac.speed_kt += step


def _integrate_position(ac: Aircraft, dt: float) -> None:
    vx, vy = velocity_vector(ac.heading_deg, ac.speed_kt)
    ac.x += vx * dt
    ac.y += vy * dt


def _advance_route_if_at_waypoint(ac: Aircraft, waypoints: dict[str, Waypoint]) -> None:
    if ac.route_index >= len(ac.route):
        return
    current_wp_id = ac.route[ac.route_index]
    wp = waypoints.get(current_wp_id)
    if wp is None:
        return
    if distance_xy(ac.x, ac.y, wp.x, wp.y) <= constants.WAYPOINT_ARRIVAL_RADIUS_NM:
        ac.route_index += 1
        if ac.route_index < len(ac.route):
            next_wp = waypoints.get(ac.route[ac.route_index])
            if next_wp is not None:
                ac.target_heading_deg = bearing_to(ac.x, ac.y, next_wp.x, next_wp.y)


def _update_distance_and_eta(ac: Aircraft, waypoints: dict[str, Waypoint]) -> None:
    dest_wp = waypoints.get(ac.destination)
    if dest_wp is None:
        ac.distance_to_destination_nm = 0.0
        ac.eta_minutes = None
        return
    ac.distance_to_destination_nm = distance_xy(ac.x, ac.y, dest_wp.x, dest_wp.y)
    if ac.speed_kt > 1e-3:
        ac.eta_minutes = (ac.distance_to_destination_nm / ac.speed_kt) * 60.0
    else:
        ac.eta_minutes = None


def _update_phase(ac: Aircraft) -> None:
    if ac.phase in (FlightPhase.EXITING, FlightPhase.EXITED):
        return
    if abs(ac.target_altitude_ft - ac.altitude_ft) > 1.0:
        ac.phase = FlightPhase.CLIMBING if ac.target_altitude_ft > ac.altitude_ft else FlightPhase.DESCENDING
    else:
        ac.phase = FlightPhase.CRUISE


def _mark_exited_if_out_of_bounds(
    ac: Aircraft,
    bounds: tuple[float, float, float, float],
    waypoints: dict[str, Waypoint],
) -> None:
    min_x, min_y, max_x, max_y = bounds
    out_of_bounds = not (min_x <= ac.x <= max_x and min_y <= ac.y <= max_y)
    reached_destination = ac.route_index >= len(ac.route)
    if reached_destination:
        dest_wp = waypoints.get(ac.destination)
        if dest_wp is not None and distance_xy(ac.x, ac.y, dest_wp.x, dest_wp.y) <= constants.WAYPOINT_ARRIVAL_RADIUS_NM:
            ac.phase = FlightPhase.EXITING
    if out_of_bounds and ac.phase != FlightPhase.EXITING:
        ac.phase = FlightPhase.EXITING

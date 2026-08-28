# All values below are simplified, fictional game-simulation constants — they
# are not real aviation performance figures or separation standards.

TURN_RATE_DEG_PER_SEC = 3.0
CLIMB_RATE_FPM = 1500.0
DESCEND_RATE_FPM = 1500.0
ACCEL_KT_PER_SEC = 2.0

TICK_SECONDS = 1.0

# Fictional separation minimums (game mechanic, not a real standard).
HORIZONTAL_SEP_MIN_NM = 5.0
VERTICAL_SEP_MIN_FT = 1000.0

# Conflict prediction lookahead / warning lead time.
LOOKAHEAD_SECONDS = 180.0
WARNING_LEAD_SECONDS = 90.0

# Radius around a waypoint at which an aircraft is considered "arrived".
WAYPOINT_ARRIVAL_RADIUS_NM = 3.0

# Radius around the destination waypoint within which an exit counts as a
# clean, on-route completion rather than an airspace excursion.
DESTINATION_EXIT_RADIUS_NM = 8.0

# Radius around an airport within which an arriving aircraft enters the
# APPROACH phase and must be cleared to land by the player (fictional,
# simplified game mechanic — not real approach procedures).
APPROACH_RADIUS_NM = 15.0

# Minimum fictional spacing between two landings on the same runway.
MIN_LANDING_SPACING_S = 90.0

# Ticks an aircraft stays visible in LANDING phase before being removed.
LANDING_GRACE_TICKS = 3

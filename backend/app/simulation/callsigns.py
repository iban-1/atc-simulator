import random

_AIRCRAFT_TYPES = ["GX2", "AV7", "TR4", "SK9", "NX3"]
_USED_NUMBERS: set[int] = set()


def generate_callsign() -> str:
    """Fictional callsign, e.g. SIM482. No relation to any real airline code."""
    number = random.randint(100, 999)
    while number in _USED_NUMBERS:
        number = random.randint(100, 999)
    _USED_NUMBERS.add(number)
    return f"SIM{number}"


def generate_aircraft_type() -> str:
    return random.choice(_AIRCRAFT_TYPES)


def reset_callsign_pool() -> None:
    _USED_NUMBERS.clear()

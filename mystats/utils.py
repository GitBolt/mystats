"""Utility functions"""

def time_converter(time: str) -> int:

    formats: tuple[str, str, str, str] = ("s", "m", "h", "d")
    conversions: dict[str, int] = {"s": 1, "m": 60, "h": 3600, "d": 86400}

    if time[-1] not in formats:
        raise ValueError((
            "Time must have s, m, h or d at the end "
            "representing seconds, minutes, hours or days."
        ))
        
    if not time[:-1].isdigit():
        raise ValueError("The time provided is not an integer")

    return int(time[:-1]) * conversions[time[-1]]

game_mode_to_players: dict[str, int] = {
    "duos": 2,
    "trios": 3,
    "quads": 4
}
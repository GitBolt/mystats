def time_converter(time: str):
    formats = ("s", "m", "h", "d")
    conversions = {"s": 1, "m": 60, "h": 3600, "d": 86400}

    if time[-1] not in formats:
        raise ValueError((
            "Time must have s, m, h or d at the end "
            "representing seconds, minutes, hours or days."
        ))
    if not time[:-1].isdigit():
        raise ValueError("The time provided is not an integer")

    return int(time[:-1]) * conversions[time[-1]]

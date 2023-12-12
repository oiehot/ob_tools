import math


def rad_to_deg(rad: float) -> float:
    return math.degrees(rad)


def deg_to_rad(deg: float) -> float:
    return math.radians(deg)


def rad_to_deg_tuple(rad_tuple: tuple[float]) -> tuple[float]:
    return [math.degrees(rad) for rad in rad_tuple]


def deg_to_rad_tuple(deg_tuple: tuple[float]) -> tuple[float]:
    return [math.radians(deg) for deg in deg_tuple]

import math


def rotations(angle: float) -> float:
    return angle * 2 * math.pi


def arc_minutes(angle: float) -> float:
    return angle * (math.pi / 10800)


def arc_seconds(angle: float) -> float:
    return angle * (math.pi / 648000)


def gradians(angle: float) -> float:
    return angle * math.pi / 200


def degrees(angle: float) -> float:
    return angle * math.pi / 180


def milliradians(angle: float) -> float:
    return angle / 1000


def radians(angle: float) -> float:
    return angle

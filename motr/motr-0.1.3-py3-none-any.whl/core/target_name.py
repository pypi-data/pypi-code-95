import typing

TargetName = typing.NewType("TargetName", str)


def coerce(name: str) -> TargetName:
    return TargetName(name)

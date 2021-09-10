from dataclasses import dataclass


@dataclass
class Worker:
    name: str
    function: callable
    period: int

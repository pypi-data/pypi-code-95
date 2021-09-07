from dataclasses import dataclass


@dataclass
class Select:
    when: callable
    to: callable

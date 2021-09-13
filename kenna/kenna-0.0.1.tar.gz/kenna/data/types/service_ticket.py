from dataclasses import dataclass


@dataclass(frozen=True)
class ServiceTicket:
    id: str
    name: str


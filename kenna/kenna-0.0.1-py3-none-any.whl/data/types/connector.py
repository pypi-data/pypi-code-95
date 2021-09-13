from dataclasses import dataclass


@dataclass(frozen=True)
class Connector:
    id: int
    name: str
    vendor: str
    connector_definition_name: str

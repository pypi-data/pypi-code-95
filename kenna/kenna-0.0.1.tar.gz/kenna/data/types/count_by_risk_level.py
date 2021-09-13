from dataclasses import dataclass


@dataclass(frozen=True)
class CountByRiskLevel:
    high: int
    medium: int
    low: int

    @property
    def total(self):
        return self.high + self.medium + self.low

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskMeterScore:
    date: str
    score: int

    def __int__(self):
        return self.score

from dataclasses import dataclass
from typing import List, Dict
from kenna.data.types.risk_meter_score import RiskMeterScore


@dataclass(frozen=True)
class Application:
    id: int
    name: str
    url: str
    hostname: str
    owner: str
    team: str
    business_units: List[str]
    notes: List[str]
    risk_meter_scores: List[RiskMeterScore]
    asset_count: int                                        #: Number of assets associated with the application.
    vulnerability_count: int                                #: Number of vulnerabilities associated with an application.
    total_vulnerability_count: int                          #: Number of vulnerabilities associated with an application including closed vulnerabilities and vulnerabilities on inactive assets.
    open_vulnerability_count_by_risk_level: Dict[str, int]  #: Number of vulnerabilities open vulnerabilities separated by high risk, medium risk, low risk, and total.
    external_facing: bool
    priority: int                                           #: Priority of application, on a scale of 1 (low) to 10 (high).
    identifiers: List[str]

    @property
    def risk_meter_score(self) -> RiskMeterScore:
        return next(iter(sorted(self.risk_meter_scores, key=lambda score: score.score)), None)

    def is_external_facing(self):
        return self.external_facing is True

    def is_internal_facing(self):
        return self.external_facing is False

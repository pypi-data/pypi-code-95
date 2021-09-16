# coding: utf8

__all__ = ["ProtectionLegDefinition"]

from typing import Optional

from ..instrument._instrument_definition import ObjectDefinition
from ._enums import (
    Direction,
    DocClause,
    Seniority,
)


class ProtectionLegDefinition(ObjectDefinition):
    """
    API endpoint for Financial Contract analytics,
    that returns calculations relevant to each contract type.

    Parameters
    ----------
    direction : Direction, optional
        The direction of the leg. the possible values are:
        - 'Paid' (the cash flows of the leg are paid to the counterparty),
        - 'Received' (the cash flows of the leg are received from the counterparty).
          Optional for a single leg instrument (like a bond), in that case default value
          is Received. It is mandatory for a multi-instrument leg instrument (like Swap
          or CDS leg).
    notional_ccy : str, optional
        The ISO code of the notional currency. Mandatory if instrument code or
        instrument style has not been defined. In case an instrument code/style has been
        defined, value may comes from the reference data.
    notional_amount : float, optional
        The notional amount of the leg at the period start date. Optional. By default
        1,000,000 is used.
    doc_clause : DocClause, optional
        The restructuring clause or credit event for Single Name Cds. The possible
        values are:
        - CumRestruct14,
        - ModifiedRestruct14,
        - ModModRestruct14,
        - ExRestruct14,
        - CumRestruct03,
        - ModifiedRestruct03,
        - ModModRestruct03,
        - ExRestruct03. Optional. By default the doc_clause of the reference_entity's
          Primary Ric is used.
    seniority : Seniority, optional
        The order of repayment in the case of a credit event for Single Name Cds. The
        possible values are:
        - Secured (Secured Debt (Corporate/Financial) or Domestic Currency Sovereign
          Debt (Government)),
        - SeniorUnsecured (Senior Unsecured Debt (Corporate/Financial) or Foreign
          Currency Sovereign Debt (Government)),
        - Subordinated (Subordinated or Lower Tier 2 Debt (Banks)),
        - JuniorSubordinated (Junior Subordinated or Upper Tier 2 Debt (Banks)),
        - Preference (Preference Shares or Tier 1 Capital (Banks)). Optional. By default
          the seniority of the reference_entity's Primary Ric is used.
    index_factor : float, optional
        The factor that is applied to the notional in case a credit event happens in one
        of the constituents of the Cds Index. Optional. By default no factor (1)
        applies.
    index_series : int, optional
        The series of the Cds Index.  Optional. By default the series of the BenchmarkRic
        is used.
    recovery_rate : float, optional
        The percentage of recovery in case of a credit event. Optional. By default the
        recovery_rate of the Cds built from reference_entity, seniority, doc_clause and
        notional_currency is used.
    recovery_rate_percent : float, optional
        The percentage of recovery in case of a credit event. Optional. By default the
        recovery_rate of the Cds built from reference_entity, seniority, doc_clause and
        notional_currency is used.
    reference_entity : str, optional
        The identifier of the reference entity, it can be:
        - for Single Name : a RedCode, an OrgId, a reference entity's RIC,
        - for Index : a RedCode, a ShortName, a CommonName. Mandatory.
    settlement_convention : str, optional
        The cashSettlementRule of the CDS. Optional. By default "3WD" (3 week days) is
        used.
    """

    def __init__(
        self,
        *,
        direction: Optional[Direction] = None,
        notional_ccy: Optional[str] = None,
        notional_amount: Optional[float] = None,
        doc_clause: Optional[DocClause] = None,
        seniority: Optional[Seniority] = None,
        index_factor: Optional[float] = None,
        index_series: Optional[int] = None,
        recovery_rate: Optional[float] = None,
        recovery_rate_percent: Optional[float] = None,
        reference_entity: Optional[str] = None,
        settlement_convention: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.direction = direction
        self.notional_ccy = notional_ccy
        self.notional_amount = notional_amount
        self.doc_clause = doc_clause
        self.seniority = seniority
        self.index_factor = index_factor
        self.index_series = index_series
        self.recovery_rate = recovery_rate
        self.recovery_rate_percent = recovery_rate_percent
        self.reference_entity = reference_entity
        self.settlement_convention = settlement_convention

    @property
    def direction(self):
        """
        The direction of the leg. the possible values are:
        - 'Paid' (the cash flows of the leg are paid to the counterparty),
        - 'Received' (the cash flows of the leg are received from the counterparty).
          Optional for a single leg instrument (like a bond), in that case default value
          is Received. It is mandatory for a multi-instrument leg instrument (like Swap
          or CDS leg).
        :return: enum Direction
        """
        return self._get_enum_parameter(Direction, "direction")

    @direction.setter
    def direction(self, value):
        self._set_enum_parameter(Direction, "direction", value)

    @property
    def doc_clause(self):
        """
        The restructuring clause or credit event for Single Name Cds. The possible
        values are:
        - CumRestruct14,
        - ModifiedRestruct14,
        - ModModRestruct14,
        - ExRestruct14,
        - CumRestruct03,
        - ModifiedRestruct03,
        - ModModRestruct03,
        - ExRestruct03. Optional.
        By default the doc_clause of the reference_entity's Primary Ric is used.
        :return: enum DocClause
        """
        return self._get_enum_parameter(DocClause, "docClause")

    @doc_clause.setter
    def doc_clause(self, value):
        self._set_enum_parameter(DocClause, "docClause", value)

    @property
    def seniority(self):
        """
        The order of repayment in the case of a credit event for Single Name Cds. The
        possible values are:
        - Secured (Secured Debt (Corporate/Financial) or Domestic Currency Sovereign
          Debt (Government)),
        - SeniorUnsecured (Senior Unsecured Debt (Corporate/Financial) or Foreign
          Currency Sovereign Debt (Government)),
        - Subordinated (Subordinated or Lower Tier 2 Debt (Banks)),
        - JuniorSubordinated (Junior Subordinated or Upper Tier 2 Debt (Banks)),
        - Preference (Preference Shares or Tier 1 Capital (Banks)).
        Optional. By default the seniority of the reference_entity's
        Primary Ric is used.
        :return: enum Seniority
        """
        return self._get_enum_parameter(Seniority, "seniority")

    @seniority.setter
    def seniority(self, value):
        self._set_enum_parameter(Seniority, "seniority", value)

    @property
    def index_factor(self):
        """
        The factor that is applied to the notional in case a credit event happens in one
        of the constituents of the Cds Index. Optional. By default no factor (1)
        applies.
        :return: float
        """
        return self._get_parameter("indexFactor")

    @index_factor.setter
    def index_factor(self, value):
        self._set_parameter("indexFactor", value)

    @property
    def index_series(self):
        """
        The series of the Cds Index.  Optional.
        By default the series of the BenchmarkRic is used.
        :return: int
        """
        return self._get_parameter("indexSeries")

    @index_series.setter
    def index_series(self, value):
        self._set_parameter("indexSeries", value)

    @property
    def notional_amount(self):
        """
        The notional amount of the leg at the period start date. Optional. By default
        1,000,000 is used.
        :return: float
        """
        return self._get_parameter("notionalAmount")

    @notional_amount.setter
    def notional_amount(self, value):
        self._set_parameter("notionalAmount", value)

    @property
    def notional_ccy(self):
        """
        The ISO code of the notional currency. Mandatory if instrument code or
        instrument style has not been defined. In case an instrument code/style has been
        defined, value may comes from the reference data.
        :return: str
        """
        return self._get_parameter("notionalCcy")

    @notional_ccy.setter
    def notional_ccy(self, value):
        self._set_parameter("notionalCcy", value)

    @property
    def recovery_rate(self):
        """
        The percentage of recovery in case of a credit event. Optional. By default the
        recovery_rate of the Cds built from reference_entity, seniority, doc_clause and
        notional_currency is used.
        :return: float
        """
        return self._get_parameter("recoveryRate")

    @recovery_rate.setter
    def recovery_rate(self, value):
        self._set_parameter("recoveryRate", value)

    @property
    def recovery_rate_percent(self):
        """
        The percentage of recovery in case of a credit event. Optional. By default the
        recovery_rate of the Cds built from reference_entity, seniority, doc_clause and
        notional_currency is used.
        :return: float
        """
        return self._get_parameter("recoveryRatePercent")

    @recovery_rate_percent.setter
    def recovery_rate_percent(self, value):
        self._set_parameter("recoveryRatePercent", value)

    @property
    def reference_entity(self):
        """
        The identifier of the reference entity, it can be:
        - for Single Name : a RedCode, an OrgId, a reference entity's RIC,
        - for Index : a RedCode, a ShortName, a CommonName. Mandatory.
        :return: str
        """
        return self._get_parameter("referenceEntity")

    @reference_entity.setter
    def reference_entity(self, value):
        self._set_parameter("referenceEntity", value)

    @property
    def settlement_convention(self):
        """
        The cashSettlementRule of the CDS. Optional. By default "3WD" (3 week days) is
        used.
        :return: str
        """
        return self._get_parameter("settlementConvention")

    @settlement_convention.setter
    def settlement_convention(self, value):
        self._set_parameter("settlementConvention", value)

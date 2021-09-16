# coding: utf8

__all__ = ["CdsInstrumentDefinition"]

from typing import Optional

from ..instrument._instrument_definition import InstrumentDefinition
from ._enums import (
    BusinessDayConvention,
    CdsConvention,
)
from ._models import (
    PremiumLegDefinition,
    ProtectionLegDefinition,
)


class CdsInstrumentDefinition(InstrumentDefinition):
    """
    API endpoint for Financial Contract analytics,
    that returns calculations relevant to each contract type.

    Parameters
    ----------
    instrument_tag : str, optional
        User defined string to identify the instrument.It can be used to link output
        results to the instrument definition. Only alphabetic, numeric and '- _.#=@'
        characters are supported. Optional.
    instrument_code : str, optional
        A cds RIC that is used to retrieve the description of the cds contract.
        Optional. If null, the protection_leg and the premium_leg  must be provided.
    cds_convention : CdsConvention, optional
        Define the cds convention. Possible values are:
        - 'ISDA' (start_date will default to accrued_begin_date, end_date will be
          adjusted to IMM Date),
        - 'UserDefined' (start_date will default to step_in_date, end_date will not be
          adjusted). Optional. Defaults to 'ISDA'.
    trade_date : str, optional
        The date the cds contract was created. Optional. By default the valuation date.
    step_in_date : str, optional
        The effective protection date. Optional. By default the trade_date + 1 calendar.
    start_date : str, optional
        The date the cds starts accruing interest. Its effective date. Optional. By
        default it is the accrued_begin_date (the last IMM date before trade_date) if
        cds_convention is ISDA, else it is the step_in_date.
    end_date : str, optional
        The maturity date of the cds contract. Mandatory if instrument_code is null.
        Either the end_date or the tenor must be provided.
    tenor : str, optional
        The period code that represents the time between the start date and end date the
        contract. Mandatory if instrument_code is null. Either the end_date or the tenor
        must be provided.
    start_date_moving_convention : BusinessDayConvention, optional
        The method to adjust the start_date. The possible values are:
        - ModifiedFollowing (adjusts dates according to the Modified Following
          convention - next business day unless is it goes into the next month,
          preceeding is used in that  case),
        - NextBusinessDay (adjusts dates according to the Following convention - Next
          Business Day),
        - PreviousBusinessDay (adjusts dates  according to the Preceeding convention -
          Previous Business Day),
        - NoMoving (does not adjust dates),
        - BbswModifiedFollowing (adjusts dates  according to the BBSW Modified Following
          convention). Optional. By default 'NoMoving' is used.
    end_date_moving_convention : BusinessDayConvention, optional
        The method to adjust the end_date.. The possible values are:
        - ModifiedFollowing (adjusts dates according to the Modified Following
          convention - next business day unless is it goes into the next month,
          preceeding is used in that  case),
        - NextBusinessDay (adjusts dates according to the Following convention - Next
          Business Day),
        - PreviousBusinessDay (adjusts dates  according to the Preceeding convention -
          Previous Business Day),
        - NoMoving (does not adjust dates),
        - BbswModifiedFollowing (adjusts dates  according to the BBSW Modified Following
          convention). Optional. By default 'NoMoving' is used.
    adjust_to_isda_end_date : bool, optional
        The way the end_date is adjusted if computed from tenor input.    The possible
        values are:
        - true ( the end_date is an IMM date computed from start_date according to ISDA
          rules, ),
        - false ( the end_date is computed from start_date according to
          end_dateMovingConvention), Optional. By default true is used if cds_convention
          is ISDA, else false is used.
    protection_leg : ProtectionLegDefinition, optional
        The Protection Leg of the CDS. It is the default leg. Mandatory if
        instrument_code is null. Optional if instrument_code not null.
    premium_leg : PremiumLegDefinition, optional
        The Premium Leg of the CDS. It is a swap leg paying a fixed coupon. Mandatory if
        instrument_code is null. Optional if instrument_code not null.
    accrued_begin_date : str, optional
        The last cashflow date. Optional. By default it is the last cashflow date.
    """

    def __init__(
        self,
        instrument_tag: Optional[str] = None,
        instrument_code: Optional[str] = None,
        cds_convention: Optional[CdsConvention] = None,
        trade_date: Optional[str] = None,
        step_in_date: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        tenor: Optional[str] = None,
        start_date_moving_convention: Optional[BusinessDayConvention] = None,
        end_date_moving_convention: Optional[BusinessDayConvention] = None,
        adjust_to_isda_end_date: Optional[bool] = None,
        protection_leg: Optional[ProtectionLegDefinition] = None,
        premium_leg: Optional[PremiumLegDefinition] = None,
        accrued_begin_date: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.instrument_tag = instrument_tag
        self.instrument_code = instrument_code
        self.cds_convention = cds_convention
        self.trade_date = trade_date
        self.step_in_date = step_in_date
        self.start_date = start_date
        self.end_date = end_date
        self.tenor = tenor
        self.start_date_moving_convention = start_date_moving_convention
        self.end_date_moving_convention = end_date_moving_convention
        self.adjust_to_isda_end_date = adjust_to_isda_end_date
        self.protection_leg = protection_leg
        self.premium_leg = premium_leg
        self.accrued_begin_date = accrued_begin_date

    @classmethod
    def get_instrument_type(cls):
        return "Cds"

    @property
    def cds_convention(self):
        """
        Define the cds convention. Possible values are:
        - 'ISDA' (start_date will default to accrued_begin_date, end_date will be
          adjusted to IMM Date),
        - 'UserDefined' (start_date will default to step_in_date, end_date will not be
          adjusted). Optional. Defaults to 'ISDA'.
        :return: enum CdsConvention
        """
        return self._get_enum_parameter(CdsConvention, "cdsConvention")

    @cds_convention.setter
    def cds_convention(self, value):
        self._set_enum_parameter(CdsConvention, "cdsConvention", value)

    @property
    def end_date_moving_convention(self):
        """
        The method to adjust the end_date. The possible values are:
        - ModifiedFollowing (adjusts dates according to the Modified Following
          convention - next business day unless is it goes into the next month,
          preceeding is used in that  case),
        - NextBusinessDay (adjusts dates according to the Following convention - Next
          Business Day),
        - PreviousBusinessDay (adjusts dates  according to the Preceeding convention -
          Previous Business Day),
        - NoMoving (does not adjust dates),
        - BbswModifiedFollowing (adjusts dates  according to the BBSW Modified Following
          convention). Optional. By default 'NoMoving' is used.
        :return: enum BusinessDayConvention
        """
        return self._get_enum_parameter(
            BusinessDayConvention, "endDateMovingConvention"
        )

    @end_date_moving_convention.setter
    def end_date_moving_convention(self, value):
        self._set_enum_parameter(
            BusinessDayConvention, "endDateMovingConvention", value
        )

    @property
    def premium_leg(self):
        """
        The Premium Leg of the CDS. It is a swap leg paying a fixed coupon. Mandatory if
        instrument_code is null. Optional if instrument_code not null.
        :return: object PremiumLegDefinition
        """
        return self._get_object_parameter(PremiumLegDefinition, "premiumLeg")

    @premium_leg.setter
    def premium_leg(self, value):
        self._set_object_parameter(PremiumLegDefinition, "premiumLeg", value)

    @property
    def protection_leg(self):
        """
        The Protection Leg of the CDS. It is the default leg. Mandatory if
        instrument_code is null. Optional if instrument_code not null.
        :return: object ProtectionLegDefinition
        """
        return self._get_object_parameter(ProtectionLegDefinition, "protectionLeg")

    @protection_leg.setter
    def protection_leg(self, value):
        self._set_object_parameter(ProtectionLegDefinition, "protectionLeg", value)

    @property
    def start_date_moving_convention(self):
        """
        The method to adjust the start_date. The possible values are:
        - ModifiedFollowing (adjusts dates according to the Modified Following
          convention - next business day unless is it goes into the next month,
          preceeding is used in that  case),
        - NextBusinessDay (adjusts dates according to the Following convention - Next
          Business Day),
        - PreviousBusinessDay (adjusts dates  according to the Preceeding convention -
          Previous Business Day),
        - NoMoving (does not adjust dates),
        - BbswModifiedFollowing (adjusts dates  according to the BBSW Modified Following
          convention). Optional. By default 'NoMoving' is used.
        :return: enum BusinessDayConvention
        """
        return self._get_enum_parameter(
            BusinessDayConvention, "startDateMovingConvention"
        )

    @start_date_moving_convention.setter
    def start_date_moving_convention(self, value):
        self._set_enum_parameter(
            BusinessDayConvention, "startDateMovingConvention", value
        )

    @property
    def accrued_begin_date(self):
        """
        The last cashflow date. Optional. By default it is the last cashflow date.
        :return: str
        """
        return self._get_parameter("accruedBeginDate")

    @accrued_begin_date.setter
    def accrued_begin_date(self, value):
        self._set_parameter("accruedBeginDate", value)

    @property
    def adjust_to_isda_end_date(self):
        """
        The way the end_date is adjusted if computed from tenor input.    The possible
        values are:
        - true ( the end_date is an IMM date computed from start_date according to ISDA
          rules, ),
        - false ( the end_date is computed from start_date according to
          end_dateMovingConvention),
        Optional. By default true is used if cds_convention is ISDA, else false is used.
        :return: bool
        """
        return self._get_parameter("adjustToIsdaEndDate")

    @adjust_to_isda_end_date.setter
    def adjust_to_isda_end_date(self, value):
        self._set_parameter("adjustToIsdaEndDate", value)

    @property
    def end_date(self):
        """
        The maturity date of the cds contract. Mandatory if instrument_code is null.
        Either the end_date or the tenor must be provided.
        :return: str
        """
        return self._get_parameter("endDate")

    @end_date.setter
    def end_date(self, value):
        self._set_parameter("endDate", value)

    @property
    def instrument_code(self):
        """
        A cds RIC that is used to retrieve the description of the cds contract.
        Optional. If null, the protection_leg and the premium_leg  must be provided.
        :return: str
        """
        return self._get_parameter("instrumentCode")

    @instrument_code.setter
    def instrument_code(self, value):
        self._set_parameter("instrumentCode", value)

    @property
    def start_date(self):
        """
        The date the cds starts accruing interest. Its effective date. Optional. By
        default it is the accrued_begin_date (the last IMM date before trade_date) if
        cds_convention is ISDA, else it is the step_in_date.
        :return: str
        """
        return self._get_parameter("startDate")

    @start_date.setter
    def start_date(self, value):
        self._set_parameter("startDate", value)

    @property
    def step_in_date(self):
        """
        The effective protection date. Optional. By default the trade_date + 1 calendar.
        :return: str
        """
        return self._get_parameter("stepInDate")

    @step_in_date.setter
    def step_in_date(self, value):
        self._set_parameter("stepInDate", value)

    @property
    def tenor(self):
        """
        The period code that represents the time between the start date and end date the
        contract. Mandatory if instrument_code is null. Either the end_date or the tenor
        must be provided.
        :return: str
        """
        return self._get_parameter("tenor")

    @tenor.setter
    def tenor(self, value):
        self._set_parameter("tenor", value)

    @property
    def trade_date(self):
        """
        The date the cds contract was created. Optional. By default the valuation date.
        :return: str
        """
        return self._get_parameter("tradeDate")

    @trade_date.setter
    def trade_date(self, value):
        self._set_parameter("tradeDate", value)

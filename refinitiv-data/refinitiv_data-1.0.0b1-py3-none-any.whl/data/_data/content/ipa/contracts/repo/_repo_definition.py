# coding: utf8
from typing import Optional, List

from . import UnderlyingContract
from ._enums import DayCountBasis
from ..instrument._instrument_definition import InstrumentDefinition


class RepoInstrumentDefinition(InstrumentDefinition):
    """
    API endpoint for Financial Contract analytics,
    that returns calculations relevant to each contract type.

    Parameters
    ----------
    instrument_tag : str, optional
        User defined string to identify the instrument.It can be used to link output
        results to the instrument definition. Only alphabetic, numeric and '- _.#=@'
        characters are supported.
    start_date : str, optional
        Start date of the repo, that means when the the underlying security is
        exchanged.
    end_date : str, optional
        End date of the repo, that means when the borrower repurchases the security
        back. Either end_date or tenor field are requested.
    tenor : str, optional
        tenor that defines the duration of the Repo in case no end_date has been
        provided. In that case, end_date is computed from start_date and tenor. Either
        end_date or tenor field are requested.
    day_count_basis : DayCountBasis, optional
        Day Count Basis convention to apply to the custom Repo rate.
        By default "Dcb_Actual_360".
    underlying_instruments : list of UnderlyingContract
        Definition of the underlying instruments. Only Bond Contracts are supported for
        now, and only one Bond can be used.
    is_coupon_exchanged : bool, optional
        Specifies whether or not intermediate coupons are exchanged.
        - CouponExchanged = True to specify that intermediate coupons for the underlying
          bond (between the repo start date and repo end date) are exchanged between the
          repo seller and repo buyer.
        - CouponExchanged = False to specify that no intermediate coupons are exchanged
          between the repo seller and repo buyer. In this case the repo instrument is
          like a standard loan with no intermediate coupons; the bond is only used as a
          warranty in case the money borrower defaults. True by default, which means
          coupon exchanged.
    repo_rate_percent : float, optional
        Custom Repo Rate in percentage. If not provided in the request, it will be
        computed by interpolating/extrapolating a Repo Curve.
    """

    def __init__(
        self,
        instrument_tag: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        tenor: Optional[str] = None,
        day_count_basis: Optional[DayCountBasis] = None,
        underlying_instruments: Optional[List[UnderlyingContract]] = None,
        is_coupon_exchanged: Optional[bool] = None,
        repo_rate_percent: Optional[float] = None,
    ):
        super().__init__()
        self.instrument_tag = instrument_tag
        self.start_date = start_date
        self.end_date = end_date
        self.tenor = tenor
        self.day_count_basis = day_count_basis
        self.underlying_instruments = underlying_instruments
        self.is_coupon_exchanged = is_coupon_exchanged
        self.repo_rate_percent = repo_rate_percent

    @classmethod
    def get_instrument_type(cls):
        return "Repo"

    @property
    def day_count_basis(self):
        """
        Day Count Basis convention to apply to the custom Repo rate.
        Optional, "Dcb_Actual_360" by default.
        :return: enum DayCountBasis
        """
        return self._get_enum_parameter(DayCountBasis, "dayCountBasis")

    @day_count_basis.setter
    def day_count_basis(self, value):
        self._set_enum_parameter(DayCountBasis, "dayCountBasis", value)

    @property
    def underlying_instruments(self):
        """
        Definition of the underlying instruments. Only Bond Contracts are supported for now, and only one Bond can be used.
        Mandatory.
        :return: list RepoUnderlyingContract
        """
        return self._get_list_parameter(UnderlyingContract, "underlyingInstruments")

    @underlying_instruments.setter
    def underlying_instruments(self, value):
        self._set_list_parameter(UnderlyingContract, "underlyingInstruments", value)

    @property
    def end_date(self):
        """
        End date of the repo, that means when the borrower repurchases the security back.
        Either EndDate or Tenor field are requested.
        :return: str
        """
        return self._get_parameter("endDate")

    @end_date.setter
    def end_date(self, value):
        self._set_parameter("endDate", value)

    @property
    def instrument_tag(self):
        """
        User defined string to identify the instrument.It can be used to link output results to the instrument definition.
        Only alphabetic, numeric and '- _.#=@' characters are supported.
        Optional.
        :return: str
        """
        return self._get_parameter("instrumentTag")

    @instrument_tag.setter
    def instrument_tag(self, value):
        self._set_parameter("instrumentTag", value)

    @property
    def is_coupon_exchanged(self):
        """
        Specifies whether or not intermediate coupons are exchanged.
        - CouponExchanged = True to specify that intermediate coupons for the underlying bond (between the repo start date and repo
        end date) are exchanged between the repo seller and repo buyer.
        - CouponExchanged = False to specify that no intermediate coupons are exchanged between the repo seller and repo buyer. In
        this case the repo instrument is like a standard loan with no intermediate coupons; the bond is only used as a warranty in
        case the money borrower defaults.
        Optional. True by default, which means coupon exchanged.
        :return: bool
        """
        return self._get_parameter("isCouponExchanged")

    @is_coupon_exchanged.setter
    def is_coupon_exchanged(self, value):
        self._set_parameter("isCouponExchanged", value)

    @property
    def repo_rate_percent(self):
        """
        Custom Repo Rate in percentage. If not provided in the request, it will be computed by interpolating/extrapolating a Repo
        Curve.
        Optional.
        :return: float
        """
        return self._get_parameter("repoRatePercent")

    @repo_rate_percent.setter
    def repo_rate_percent(self, value):
        self._set_parameter("repoRatePercent", value)

    @property
    def start_date(self):
        """
        Start date of the repo, that means when the the underlying security is exchanged.
        Mandatory.
        :return: str
        """
        return self._get_parameter("startDate")

    @start_date.setter
    def start_date(self, value):
        self._set_parameter("startDate", value)

    @property
    def tenor(self):
        """
        Tenor that defines the duration of the Repo in case no EndDate has been provided. In that case, EndDate is computed from
        StartDate and Tenor.
        Either EndDate or Tenor field are requested.
        :return: str
        """
        return self._get_parameter("tenor")

    @tenor.setter
    def tenor(self, value):
        self._set_parameter("tenor", value)

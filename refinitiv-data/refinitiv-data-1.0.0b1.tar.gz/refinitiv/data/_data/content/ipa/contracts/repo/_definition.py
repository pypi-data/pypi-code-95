# coding: utf8

__all__ = ["Definition"]

from typing import Optional, Union, Iterable, List

from . import UnderlyingContract, PricingParameters
from .._outputs import Outputs
from .._base_definition import BaseDefinition
from ._repo_definition import RepoInstrumentDefinition
from ..._enums import DayCountBasis


class Definition(BaseDefinition):
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
    fields: list of str, optional
        Contains the list of Analytics that the quantitative analytic service will
        compute.
    pricing_parameters : PricingParameters, optional
        The pricing parameters to apply to this instrument. If pricing parameters
        are not provided at this level parameters defined globally at the request
        level are used. If no pricing parameters are provided globally default
        values apply.
    outputs: list of str or Outputs, optional
        Contains the sections that will be returned by the API
    extended_params : dict, optional
        If necessary other parameters

    Methods
    -------
    get_data(session=session, on_response=on_response, async_mode=None)
        Returns a response to the data platform
    get_data_async(session=session, on_response=on_response, async_mode=None)
        Returns a response to the async data platform
    get_stream(session=session, api="")
        Get stream quantitative analytic service subscription

    Examples
    --------
     >>> import refinitiv.data.content.ipa.financial_contracts as rdf
     >>> definition = rdf.repo.Definition(
     ...   underlying_instruments=[
     ...   rdf.repo.UnderlyingContract(
     ...   instrument_type="Bond",
     ...   instrument_definition=rdf.bond.Definition(instrument_code="US191450264="),
     ...   )],
     ...)
     >>> response = definition.get_data()

     Using get_stream
     >>> stream = definition.get_stream()
     >>> stream.open()
    """

    def __init__(
        self,
        *,
        instrument_tag: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        tenor: Optional[str] = None,
        day_count_basis: Optional[DayCountBasis] = None,
        underlying_instruments: Optional[List[UnderlyingContract]] = None,
        is_coupon_exchanged: Optional[bool] = None,
        repo_rate_percent: Optional[float] = None,
        fields: Optional[Iterable[str]] = None,
        pricing_parameters: Optional[PricingParameters] = None,
        outputs: Union[Iterable[str], Iterable[Outputs]] = None,
        extended_params: Optional[dict] = None,
    ) -> None:
        self.underlying_instruments = underlying_instruments
        definition = RepoInstrumentDefinition(
            instrument_tag=instrument_tag,
            underlying_instruments=underlying_instruments,
            start_date=start_date,
            end_date=end_date,
            tenor=tenor,
            is_coupon_exchanged=is_coupon_exchanged,
            repo_rate_percent=repo_rate_percent,
            day_count_basis=day_count_basis,
        )
        super().__init__(
            definition=definition,
            fields=fields,
            pricing_parameters=pricing_parameters,
            outputs=outputs,
            extended_params=extended_params,
        )

    def __repr__(self):
        from refinitiv.data._data import create_str_definition

        return create_str_definition(
            self,
            middle_path="content",
            end_path="ipa.financial_contracts",
            content=f"{{underlying_instruments='{self.underlying_instruments}'}}",
        )

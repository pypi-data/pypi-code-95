# coding: utf8

__all__ = ["Definition"]

from typing import Optional, Iterable, Union

from .._base_definition import BaseDefinition
from .._contracts_data_provider import universe_contracts_arg_parser
from ..bond import PricingParameters, Definition as BondDefinition


class Definition(BaseDefinition):
    """
    This class describes the properties
    that you can use in request to price a Bond contracts.

    Parameters
    ----------
    universe : str, list of str, bond.Definition, list of bond.Definition
        Contains the list of Bond Futures you want to price.
    fields : list, optional
        Contains the list of Analytics that the quantitative analytic service
        will compute.
    pricing_parameters : object, optional
        Contains the properties that may be used to control the calculation.
    outputs : list, optional
        Contains the sections that will be returned by the API
    extended_params : dict, optional
        If necessary other parameters

    Methods
    -------
    get_data(session=session, on_response=on_response)
        Returns a response to the data platform
    get_stream(session=session, api="")
        Get stream object of this definition

    Examples
    --------
    >>> import refinitiv.data.content.ipa.financial_contracts as rdf
    >>> definition = rdf.bonds.Definition(
    ...    universe=[
    ...        "US1YT=RR",
    ...        ("US5YT=RR", rdf.bond.PricingParameters(valuation_date="2019-07-05")),
    ...        rdf.bond.Definition("US10YT=RR")
    ...    ],
    ...    fields=[
    ...        "InstrumentCode",
    ...        "MarketDataDate",
    ...        "YieldPercent",
    ...        "GovernmentSpreadBp",
    ...        "GovCountrySpreadBp",
    ...        "RatingSpreadBp",
    ...        "SectorRatingSpreadBp",
    ...        "EdsfSpreadBp",
    ...        "IssuerSpreadBp"
    ...    ],
    ...    pricing_parameters=rdf.bond.PricingParameters(
    ...        valuation_date="2019-07-05",
    ...        price_side=rdf.bond.PriceSide.BID
    ...    )
    ...)
    >>> response = definition.get_data()

    Using get_stream
    >>> response = definition.get_stream()
    """

    def __init__(
        self,
        universe: Union[str, Iterable[str], BondDefinition, Iterable[BondDefinition]],
        fields: Optional[Iterable[str]] = None,
        pricing_parameters: Optional[PricingParameters] = None,
        outputs: Optional[Iterable[str]] = None,
        extended_params: Optional[dict] = None,
    ) -> None:
        universe = universe_contracts_arg_parser.get_list(
            universe, BondDefinition, PricingParameters
        )
        super().__init__(
            universe=universe,
            fields=fields,
            pricing_parameters=pricing_parameters,
            outputs=outputs,
            extended_params=extended_params,
        )

    def __eq__(self, other):
        definition = self._kwargs.get("universe")
        return definition == other

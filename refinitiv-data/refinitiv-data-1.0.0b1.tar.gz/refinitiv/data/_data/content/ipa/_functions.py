# coding: utf8
from .contracts._contracts_data_provider import process_universe
from .._content_provider import get_valid_session
from .._content_provider_factory import get_url
from .._content_type import ContentType

__all__ = [
    "get_bond_analytics",
    "get_option_analytics",
    "get_swap_analytics",
    "get_cds_analytics",
    "get_cross_analytics",
    "get_repo_analytics",
    "get_cap_floor_analytics",
    "get_swaption_analytics",
    "get_term_deposit_analytics",
    "get_surface",
    "get_forward_curve",
    "get_zc_curve",
    "get_zc_curve_definition",
]


def _get_content_data(content_type, **kwargs):
    from refinitiv.data._data.content._content_provider_factory import make_provider
    from ...factory.content_factory import ContentFactory

    provider = make_provider(content_type)
    session = get_valid_session(kwargs.get("session"))
    result = provider.get_data(session, get_url(content_type), **kwargs)

    if result.is_success and result.data and result.data.df is not None:
        retval = result.data.df
    else:
        ContentFactory._last_error_status = result.status
        retval = None

    ContentFactory._last_result = result

    return retval


def get_instrument_analytics(
    universe,
    fields=None,
    pricing_parameters=None,
    outputs=None,
    on_response=None,
    closure=None,
    session=None,
):
    return _get_content_data(ContentType.CONTRACTS, **locals())


def get_bond_analytics(
    universe,
    fields=None,
    pricing_parameters=None,
    outputs=None,
):
    """
    This function describes the properties that you can use a request to price a Bond contract.

    Parameters
    ----------
    universe: str, list, object
        contains the list of Bond Futures you want to price.
    fields: list, optional
        contains the list of Analytics that the quantitative analytic service will compute.
    pricing_parameters: object, optional
        contains the properties that may be used to control the calculation.
    outputs: list, optional
        contains the sections that will be returned by the API

    Returns
    -------
    Dataframe or None
        Dataframe if successful, None otherwise.

    Examples
    --------
    >>> import refinitiv.data as rd
    >>> from refinitiv.data.content import ipa
    >>> df = rd.function.get_bond_analytics(
    ...    universe=[
    ...        "US1YT=RR",
    ...        "US5YT=RR",
    ...        "US10YT=RR"
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
    ...    pricing_parameters=ipa.financial_contracts.bond.PricingParameters(
    ...        valuation_date="2019-07-05",
    ...        price_side=ipa.financial_contracts.bond.PriceSide.BID
    ...    )
    ...)
    """
    from .contracts.bond import Definition, PricingParameters

    universe = process_universe(universe, Definition, PricingParameters)
    return _get_content_data(ContentType.CONTRACTS, **locals())


def get_option_analytics(
    universe,
    fields=None,
    pricing_parameters=None,
    outputs=None,
):
    """
    This function describes the properties that you can use a request
    to get the results for an Option contract.

    Parameters
    ----------
    universe: str, list, object
        contains the list of Option you want to price.
    fields: list, optional
        contains the list of Analytics that the quantitative analytic service will compute.
    pricing_parameters: object, optional
        contains the properties that may be used to control the calculation.
    outputs: list, optional
        contains the sections that will be returned by the API

    Returns
    -------
    Dataframe or None
        Dataframe if successful, None otherwise.

    Examples
    --------
    >>> import refinitiv.data as rd
    >>> from refinitiv.data.content import ipa
    >>> df = rd.function.get_option_analytics(
    ...     universe=ipa.financial_contracts.option.Definition(
    ...         instrument_code="FCHI560000L1.p",
    ...         underlying_type=ipa.financial_contracts.option.UnderlyingType.ETI
    ...     ),
    ...     outputs=[
    ...         "Data",
    ...         "Headers"
    ...     ],
    ...     fields=[
    ...         "MarketValueInDealCcy",
    ...         "DeltaPercent",
    ...         "GammaPercent",
    ...         "RhoPercent",
    ...         "ThetaPercent",
    ...         "VegaPercent"
    ...     ]
    ... )
    """
    from .contracts.option import Definition

    universe = process_universe(universe, Definition)
    return _get_content_data(ContentType.CONTRACTS, **locals())


def get_swap_analytics(
    universe,
    fields=None,
    pricing_parameters=None,
    outputs=None,
):
    """
    This function describes the properties that you can use a request
    to price an Interest Rate Swap contract.

    Parameters
    ----------
    universe: str, list, object
        contains the list of IR Swap you want to price.
    fields: list, optional
        contains the list of Analytics that the quantitative analytic service will compute.
    pricing_parameters: object, optional
        contains the properties that may be used to control the calculation.
    outputs: list, optional
        contains the sections that will be returned by the API

    Returns
    -------
    Dataframe or None
        Dataframe if successful, None otherwise.

    Examples
    --------
    >>> import refinitiv.data as rd
    >>> from refinitiv.data.content import ipa
    >>> df = rd.function.get_swap_analytics(
    ...     universe=ipa.financial_contracts.swap.Definition(
    ...         instrument_tag="user-defined GBP IRS",
    ...         start_date="2019-05-21T00:00:00Z",
    ...         tenor="10Y",
    ...         legs=[
    ...             ipa.financial_contracts.swap.LegDefinition(
    ...                 direction=ipa.financial_contracts.swap.Direction.PAID,
    ...                 notional_amount="10000000",
    ...                 notional_ccy="GBP",
    ...                 interest_type=ipa.financial_contracts.swap.InterestType.FIXED,
    ...                 interest_payment_frequency=ipa.financial_contracts.swap.Frequency.ANNUAL,
    ...                 interest_calculation_method=ipa.financial_contracts.swap.DayCountBasis.DCB_30_360,
    ...                 payment_business_day_convention=ipa.financial_contracts.swap.BusinessDayConvention.MODIFIED_FOLLOWING,
    ...                 payment_roll_convention=ipa.financial_contracts.swap.DateRollingConvention.SAME,
    ...                 payment_business_days="UKG",
    ...                 amortization_schedule=[
    ...                     ipa.financial_contracts.swap.AmortizationItem(
    ...                         remaining_notional=200000,
    ...                         amortization_frequency=ipa.financial_contracts.swap.AmortizationFrequency.EVERY_COUPON,
    ...                         amortization_type=ipa.financial_contracts.swap.AmortizationType.LINEAR
    ...                     )
    ...                 ]
    ...             ),
    ...             ipa.financial_contracts.swap.LegDefinition(
    ...                 direction=ipa.financial_contracts.swap.Direction.RECEIVED,
    ...                 notional_amount="10000000",
    ...                 notional_ccy="GBP",
    ...                 interest_type=ipa.financial_contracts.swap.InterestType.FLOAT,
    ...                 interest_payment_frequency=ipa.financial_contracts.swap.Frequency.SEMI_ANNUAL,
    ...                 index_reset_frequency=ipa.financial_contracts.swap.Frequency.SEMI_ANNUAL,
    ...                 interest_calculation_method=ipa.financial_contracts.swap.DayCountBasis.DCB_ACTUAL_360,
    ...                 payment_business_day_convention=ipa.financial_contracts.swap.BusinessDayConvention.MODIFIED_FOLLOWING,
    ...                 payment_roll_convention=ipa.financial_contracts.swap.DateRollingConvention.SAME,
    ...                 payment_business_days="UKG",
    ...                 spread_bp=20,
    ...                 index_name="LIBOR",
    ...                 index_tenor="6M",
    ...                 index_reset_type=ipa.financial_contracts.swap.IndexResetType.IN_ADVANCE,
    ...                 amortization_schedule=[
    ...                     ipa.financial_contracts.swap.AmortizationItem(
    ...                         remaining_notional=200000,
    ...                         amortization_frequency=ipa.financial_contracts.swap.AmortizationFrequency.EVERY2ND_COUPON,
    ...                         amortization_type=ipa.financial_contracts.swap.AmortizationType.LINEAR
    ...                     )
    ...                 ]
    ...             )
    ...         ]
    ...     ),
    ...     pricing_parameters=ipa.financial_contracts.swap.PricingParameters(discounting_tenor="ON"),
    ...     fields=[
    ...         "InstrumentTag",
    ...         "InstrumentDescription",
    ...         "FixedRate",
    ...         "MarketValueInDealCcy",
    ...         "PV01Bp",
    ...         "DiscountCurveName",
    ...         "ForwardCurveName",
    ...         "CashFlowDatesArray",
    ...         "CashFlowTotalAmountsInDealCcyArray",
    ...         "CashFlowDiscountFactorsArray",
    ...         "CashFlowResidualAmountsInDealCcyArray",
    ...         "ErrorMessage"
    ...     ],
    ...     outputs=[
    ...         "Data",
    ...         "Headers"
    ...     ]
    ... )
    """
    from .contracts.swap import Definition

    universe = process_universe(universe, Definition)
    return _get_content_data(ContentType.CONTRACTS, **locals())


def get_cds_analytics(
    universe,
    fields=None,
    pricing_parameters=None,
    outputs=None,
):
    """
    This function describes the properties that you can use a request
    to price a Credit Default Swap (CDS) contract.

    Parameters
    ----------
    universe: str, list, object
        contains the list of CDS you want to price.
    fields: list, optional
        contains the list of Analytics that the quantitative analytic service will compute.
    pricing_parameters: object, optional
        contains the properties that may be used to control the calculation.
    outputs: list, optional
        contains the sections that will be returned by the API

    Returns
    -------
    Dataframe or None
        Dataframe if successful, None otherwise.

    Examples
    --------
    >>> import refinitiv.data as rd
    >>> from refinitiv.data.content import ipa
    >>> df = rd.function.get_cds_analytics(
    ...    universe=ipa.financial_contracts.cds.Definition(
    ...        instrument_tag="Cds1_InstrumentCode",
    ...        instrument_code="BNPP5YEUAM=R",
    ...        cds_convention=ipa.financial_contracts.cds.CdsConvention.ISDA,
    ...        trade_date="2019-05-21T00:00:00Z",
    ...        step_in_date="2019-05-22T00:00:00Z",
    ...        start_date="2019-05-20T00:00:00Z",
    ...        end_date_moving_convention=ipa.financial_contracts.cds.BusinessDayConvention.NO_MOVING,
    ...        adjust_to_isda_end_date=True,
    ...    ),
    ...    pricing_parameters=ipa.financial_contracts.cds.PricingParameters(
    ...        market_data_date="2020-01-01"
    ...    ),
    ...    outputs=[
    ...        "Data",
    ...        "Headers"
    ...    ],
    ...    fields=[
    ...        "InstrumentTag",
    ...        "ValuationDate",
    ...        "InstrumentDescription",
    ...        "StartDate",
    ...        "EndDate",
    ...        "SettlementDate",
    ...        "UpfrontAmountInDealCcy",
    ...        "CashAmountInDealCcy",
    ...        "AccruedAmountInDealCcy",
    ...        "AccruedBeginDate",
    ...        "NextCouponDate",
    ...        "UpfrontPercent",
    ...        "ConventionalSpreadBp",
    ...        "ParSpreadBp",
    ...        "AccruedDays",
    ...        "ErrorCode",
    ...        "ErrorMessage"
    ...    ]
    ...)
    """
    from .contracts.cds import Definition

    universe = process_universe(universe, Definition)
    return _get_content_data(ContentType.CONTRACTS, **locals())


def get_cross_analytics(
    universe,
    fields=None,
    pricing_parameters=None,
    outputs=None,
):
    """
    This function describes the properties that you can use a request
    to price a FX Cross contract.

    Parameters
    ----------
    universe: str, list, object
        contains the list of FX Cross contract you want to price.
    fields: list, optional
        contains the list of Analytics that the quantitative analytic service will compute.
    pricing_parameters: object, optional
        contains the properties that may be used to control the calculation.
    outputs: list, optional
        contains the sections that will be returned by the API

    Returns
    -------
    Dataframe or None
        Dataframe if successful, None otherwise.

    Examples
    --------
    >>> import refinitiv.data as rd
    >>> from refinitiv.data.content import ipa
    >>> df = rd.function.get_cross_analytics(
    ...    universe=[
    ...        ipa.financial_contracts.cross.Definition(
    ...            fx_cross_type=ipa.financial_contracts.cross.FxCrossType.FX_NON_DELIVERABLE_FORWARD,
    ...            fx_cross_code="USDINR",
    ...            legs=[
    ...                ipa.financial_contracts.cross.LegDefinition(
    ...                    deal_amount=1000000,
    ...                    contra_amount=65762500,
    ...                    deal_ccy_buy_sell=ipa.financial_contracts.cross.BuySell.BUY,
    ...                    tenor="4Y"
    ...                )
    ...            ],
    ...        ),
    ...    ],
    ...    pricing_parameters=ipa.financial_contracts.cross.PricingParameters(
    ...        valuation_date="2017-11-15T00:00:00Z"
    ...    ),
    ...    fields=[
    ...        "ValuationDate",
    ...        "InstrumentDescription",
    ...        "EndDate",
    ...        "FxSwapsCcy1Ccy2",
    ...        "MarketValueInReportCcy",
    ...        "DeltaAmountInReportCcy",
    ...        "RhoContraCcyAmountInReportCcy",
    ...        "RhoDealCcyAmountInReportCcy"
    ...    ],
    ...    outputs=[
    ...        "Data",
    ...        "Headers"
    ...    ]
    ...)
    """
    return _get_content_data(ContentType.CONTRACTS, **locals())


def get_repo_analytics(
    universe,
    fields=None,
    pricing_parameters=None,
    outputs=None,
):
    """
    This function describes the properties that you can use a request
    to get the results for a Repo contract.

    Parameters
    ----------
    universe: str, list, object
        contains the list of Repo definitions.
    fields: list, optional
        contains the list of Analytics that the quantitative analytic service will compute.
    pricing_parameters: object, optional
        contains the properties that may be used to control the calculation.
    outputs: list, optional
        contains the sections that will be returned by the API

    Returns
    -------
    Dataframe or None
        Dataframe if successful, None otherwise.

    Examples
    --------
    >>> import refinitiv.data as rd
    >>> from refinitiv.data.content import ipa
    >>> df = rd.function.get_repo_analytics(
    ...     universe=ipa.financial_contracts.repo.Definition(
    ...         start_date="2019-11-27",
    ...         tenor="1M",
    ...         underlying_instruments=[
    ...             ipa.financial_contracts.repo.UnderlyingContract(
    ...                 instrument_type="Bond",
    ...                 instrument_definition=ipa.financial_contracts.bond.Definition(
    ...                     instrument_code="US191450264="
    ...                 )
    ...             )
    ...         ]
    ...     ),
    ...     pricing_parameters=ipa.financial_contracts.repo.PricingParameters(
    ...         market_data_date="2019-11-25"
    ...     )
    ... )
    """
    return _get_content_data(ContentType.CONTRACTS, **locals())


def get_cap_floor_analytics(
    universe,
    fields=None,
    pricing_parameters=None,
    outputs=None,
):
    """
    This function describes the properties that you can use a request
    to get the results for a Cap Floor contract.

    Parameters
    ----------
    universe: str, list, object
        contains the list of Cap Floor definitions.
    fields: list, optional
        contains the list of Analytics that the quantitative analytic service will compute.
    pricing_parameters: object, optional
        contains the properties that may be used to control the calculation.
    outputs: list, optional
        contains the sections that will be returned by the API

    Returns
    -------
    Dataframe or None
        Dataframe if successful, None otherwise.

    Examples
    --------
    >>> import refinitiv.data as rd
    >>> from refinitiv.data.content import ipa
    >>> df = rd.function.get_cap_floor_analytics(
     ...   universe=ipa.financial_contracts.cap_floor.Definition(
     ...       notional_ccy="EUR",
     ...       start_date="2019-02-11",
     ...       amortization_schedule=[
     ...           ipa.financial_contracts.cap_floor.AmortizationItem(
     ...               start_date="2021-02-11",
     ...               end_date="2022-02-11",
     ...               amount=100000,
     ...               amortization_type="Schedule"
     ...           ),
     ...           ipa.financial_contracts.cap_floor.AmortizationItem(
     ...               start_date="2022-02-11",
     ...               end_date="2023-02-11",
     ...               amount=-100000,
     ...               amortization_type="Schedule"
     ...           ),
     ...       ],
     ...       tenor="5Y",
     ...       buy_sell="Sell",
     ...       notional_amount=10000000,
     ...       interest_payment_frequency="Monthly",
     ...       cap_strike_percent=1
     ...   ),
     ...   pricing_parameters=ipa.financial_contracts.cap_floor.PricingParameters(
     ...       skip_first_cap_floorlet=True,
     ...       valuation_date="2020-02-07"
     ...   ),
     ...   fields=[
     ...       "InstrumentTag",
     ...       "InstrumentDescription",
     ...       "FixedRate",
     ...       "MarketValueInDealCcy",
     ...       "MarketValueInReportCcy",
     ...       "ErrorMessage"
     ...   ],
     ...   outputs=[
     ...       "Data",
     ...       "Headers"
     ...   ]
     ...)
    """
    return _get_content_data(ContentType.CONTRACTS, **locals())


def get_swaption_analytics(
    universe,
    fields=None,
    pricing_parameters=None,
    outputs=None,
):
    """
    This function describes the properties that you can use a request
    to get the results for a Swaption contract.

    Parameters
    ----------
    universe: str, list, object
        contains the list of Swaption definitions.
    fields: list, optional
        contains the list of Analytics that the quantitative analytic service will compute.
    pricing_parameters: object, optional
        contains the properties that may be used to control the calculation.
    outputs: list, optional
        contains the sections that will be returned by the API

    Returns
    -------
    Dataframe or None
        Dataframe if successful, None otherwise.

    Examples
    --------
    >>> import refinitiv.data as rd
    >>> from refinitiv.data.content import ipa
    >>> df = rd.function.get_swaption_analytics(
    ...    universe=ipa.financial_contracts.swaption.Definition(
    ...        instrument_tag="BermudanEURswaption",
    ...        settlement_type=ipa.financial_contracts.swaption.SwaptionSettlementType.CASH,
    ...        tenor="7Y",
    ...        strike_percent=2.75,
    ...        buy_sell=ipa.financial_contracts.swaption.BuySell.BUY,
    ...        call_put=ipa.financial_contracts.swaption.CallPut.CALL,
    ...        exercise_style=ipa.financial_contracts.swaption.ExerciseStyle.BERM,
    ...        bermudan_swaption_definition=ipa.financial_contracts.swaption.BermudanSwaptionDefinition(
    ...            exercise_schedule_type=ipa.financial_contracts.swaption.ExerciseScheduleType.FLOAT_LEG,
    ...            notification_days=0
    ...        ),
    ...        underlying_definition=ipa.financial_contracts.swap.Definition(
    ...            tenor="3Y",
    ...            template="EUR_AB6E"
    ...        )
    ...    ),
    ...    pricing_parameters=ipa.financial_contracts.swaption.PricingParameters(valuation_date="2020-04-24", nb_iterations=80),
    ...    outputs=[
    ...        "Data",
    ...        "Headers",
    ...        "MarketData"
    ...    ]
    ...)
    """
    return _get_content_data(ContentType.CONTRACTS, **locals())


def get_term_deposit_analytics(
    universe,
    fields=None,
    pricing_parameters=None,
    outputs=None,
):
    """
    This function describes the properties that you can use a request
    to get the results for a Term Deposits contract.

    Parameters
    ----------
    universe: str, list, object
        contains the list of Term Deposits definitions.
    fields: list, optional
        contains the list of Analytics that the quantitative analytic service will compute.
    pricing_parameters: object, optional
        contains the properties that may be used to control the calculation.
    outputs: list, optional
        contains the sections that will be returned by the API

    Returns
    -------
    Dataframe or None
        Dataframe if successful, None otherwise.

    Examples
    --------
    >>> import refinitiv.data as rd
    >>> from refinitiv.data.content import ipa
    >>> df = rd.function.get_term_deposit_analytics(
    ...     universe=ipa.financial_contracts.term_deposit.Definition(
    ...         instrument_tag="AED_AM1A",
    ...         tenor="5Y",
    ...         notional_ccy="GBP"
    ...     ),
    ...     pricing_parameters=ipa.financial_contracts.term_deposit.PricingParameters(valuation_date="2018-01-10T00:00:00Z"),
    ...     fields=[
    ...         "InstrumentTag",
    ...         "InstrumentDescription",
    ...         "FixedRate",
    ...         "MarketValueInDealCcy",
    ...         "MarketValueInReportCcy",
    ...         "ErrorMessage"
    ...     ],
    ...     outputs=[
    ...         "Data",
    ...         "Headers"
    ...     ]
    ... )
    """
    from .contracts.term_deposit import Definition

    universe = process_universe(universe, Definition)
    return _get_content_data(ContentType.CONTRACTS, **locals())


def get_surface(
    universe,
    outputs=None,
):
    """
    The Volatility Surfaces API provides you with an easy way to:

    - Compute the volatility level for a specific expiry and strike.
    - Derive volatility slices based on specific strikes or expiries.
    - Analyze the volatility surface of an asset.

    To compute a volatility surface, all you need to do is define the underlying instrument.
    For more advanced usage, you can easily apply different calculation parameters or
    adjust the surface layout to match your needs.

    Parameters
    ----------
    universe: list, object
        contains the list of Surface definitions.
    outputs: list, optional
        these values will be distributed depending on the available input data and the type of volatility.

    Returns
    -------
    Dataframe or None
        Dataframe if successful, None otherwise.

    Examples
    --------
    >>> import refinitiv.data as rd
    >>> from refinitiv.data.content import ipa
    >>> df = rd.function.get_surface(
    ...    universe=[
    ...        ipa.surfaces.surface_eti.Definition(
    ...            tag="1",
    ...            instrument_code="BNPP.PA@RIC",
    ...            pricing_parameters=ipa.surfaces.surface_eti.EtiCalculationParams(
    ...                price_side=ipa.surfaces.surface_eti.PriceSide.MID,
    ...                volatility_model=ipa.surfaces.surface_eti.VolatilityModel.SVI,
    ...                x_axis=ipa.surfaces.surface_eti.Axis.DATE,
    ...                y_axis=ipa.surfaces.surface_eti.Axis.STRIKE,
    ...            ),
    ...            layout=ipa.surfaces.surface_eti.SurfaceLayout(
    ...                format=ipa.surfaces.surface_eti.Format.MATRIX,
    ...                y_point_count=10
    ...            ),
    ...        ),
    ...        ipa.surfaces.surface_eti.Definition(
    ...            tag="222",
    ...            instrument_code="BNPP.PA@RIC",
    ...            pricing_parameters=ipa.surfaces.surface_eti.EtiCalculationParams(
    ...                price_side=ipa.surfaces.surface_eti.PriceSide.MID,
    ...                volatility_model=ipa.surfaces.surface_eti.VolatilityModel.SVI,
    ...                x_axis=ipa.surfaces.surface_eti.Axis.DATE,
    ...                y_axis=ipa.surfaces.surface_eti.Axis.STRIKE,
    ...            ),
    ...            layout=ipa.surfaces.surface_eti.SurfaceLayout(
    ...                format=ipa.surfaces.surface_eti.Format.MATRIX,
    ...                y_point_count=10
    ...            ),
    ...        )
    ...    ]
    ...)
    """

    return _get_content_data(ContentType.SURFACES, **locals())


def get_forward_curve(
    universe,
    outputs=None,
):
    """
    Parameters
    ----------
    universe: str, list, object
        contains the list of Curve definitions.
    outputs: str, list, optional
        contains the sections that will be returned by the API

    Returns
    -------
    Dataframe or None
        Dataframe if successful, None otherwise.

    Examples
    --------
    >>> import refinitiv.data as rd
    >>> from refinitiv.data.content import ipa
    >>> response = rd.function.get_forward_curve(
    ...    universe=[
    ...        ipa.curves.forward_curve.Definition(
    ...            curve_definition=ipa.curves.forward_curve.SwapZcCurveDefinition(
    ...                currency="EUR",
    ...                index_name="EURIBOR",
    ...                discounting_tenor="OIS"
    ...            ),
    ...            forward_curve_definitions=[
    ...                ipa.curves.forward_curve.ForwardCurveDefinition(
    ...                    index_tenor="3M",
    ...                    forward_curve_tag="ForwardTag",
    ...                    forward_start_date="2021-02-01",
    ...                    forward_curve_tenors=[
    ...                        "0D",
    ...                        "1D",
    ...                        "2D",
    ...                        "3M",
    ...                        "6M",
    ...                        "9M",
    ...                        "1Y",
    ...                        "2Y",
    ...                        "3Y",
    ...                        "4Y",
    ...                        "5Y",
    ...                        "6Y",
    ...                        "7Y",
    ...                        "8Y",
    ...                        "9Y",
    ...                        "10Y",
    ...                        "15Y",
    ...                        "20Y",
    ...                        "25Y"
    ...                    ]
    ...                )
    ...            ]
    ...        )
    ...    ],
    ...    outputs=[
    ...        "Constituents"
    ...    ]
    ...)
    """

    return _get_content_data(ContentType.FORWARD_CURVE, **locals())


def get_zc_curve(
    universe,
    outputs=None,
):
    """
    Parameters
    ----------
    universe: str, list, object
        contains the list of Curve definitions.
    outputs: list, optional
        contains the sections that will be returned by the API

    Returns
    -------
    Dataframe or None
        Dataframe if successful, None otherwise.

    Examples
    --------
    >>> import refinitiv.data as rd
    >>> from refinitiv.data.content import ipa
    >>> response = rd.function.get_zc_curve(
    ...    universe=[
    ...         ipa.curves.zc_curve.Definition(
    ...             constituents={},
    ...             curve_parameters=ipa.curves.zc_curve.ZcCurveParameters(
    ...                 valuation_date="2019-08-21",
    ...                 price_side="Mid",
    ...                 interpolation_mode=ipa.curves.zc_curve.ZcInterpolationMode.CUBIC_DISCOUNT,
    ...             ),
    ...             curve_definition=ipa.curves.zc_curve.ZcCurveDefinitions(
    ...                 currency="EUR",
    ...                 index_name="EURIBOR",
    ...                 source="Refinitiv",
    ...                 discounting_tenor="OIS",
    ...             ),
    ...             curve_tag="TAG",
    ...         )
    ...    ],
    ...    outputs=[
    ...        ipa.curves.zc_curves.Outputs.CONSTITUENTS
    ...    ]
    ...)
    """

    return _get_content_data(ContentType.ZC_CURVES, **locals())


def get_zc_curve_definition(universe):
    """
    Parameters
    ----------
    universe: str, list, object
        contains the list of Curve definitions.

    Returns
    -------
    Dataframe or None
        Dataframe if successful, None otherwise.

    Examples
    --------
    >>> import refinitiv.data as rd
    >>> from refinitiv.data.content import ipa
    >>> response = rd.function.get_zc_curve_definition(
    ...    universe=[
    ...        ipa.curves.zc_curve_definition.Definition(source="Refinitiv")
    ...    ],
    ...)
    """

    return _get_content_data(ContentType.ZC_CURVE_DEFINITIONS, **locals())

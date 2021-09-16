# coding: utf8

__all__ = ["PricingParameters"]

from typing import Optional, Union

from ..instrument._instrument_pricing_parameters import InstrumentPricingParameters
from ._enums import (
    DividendType,
    ProjectedIndexCalculationMethod,
    CreditSpreadType,
    PriceSide,
    RedemptionDateType,
    VolatilityType,
    VolatilityTermStructureType,
    BenchmarkYieldSelectionMode,
    YieldType,
    QuoteFallbackLogic,
)
from ._models import BondRoundingParameters


class PricingParameters(InstrumentPricingParameters):
    """
    API endpoint for Financial Contract analytics,
    that returns calculations relevant to each contract type.

    Parameters
    ----------
    trade_date : str, optional
        Trade date of the bond. The trade_date is used to compute the default
        valuation_date : By default the rule is that valuation_date = trade_date +
        settlement_convention. Optional. By default, it is equal to market_data_date.
    benchmark_yield_selection_mode : BenchmarkYieldSelectionMode, optional
        The benchmark yield.
        Default value is "Interpolate".
    credit_spread_type : CreditSpreadType, optional
        Credit curve spread type to use during pricing. Applicable for Convertible
        Bonds.
    dividend_type : DividendType, optional
        Underlying stock dividend type used during pricing convertible bond. Applicable
        for Convertible Bonds.
    fx_price_side : PriceSide, optional
        FX price side to consider when retrieving FX rates (Mid, Bid, Ask, Last, Close)
    price_side : PriceSide, optional
        Quoted price side of the bond to use for pricing Analysis: Bid(Bid value),
        Ask(Ask value), Mid(Mid value) Optional. By default the "Mid" price of the bond
        is used.
    projected_index_calculation_method : ProjectedIndexCalculationMethod, optional
        Flag used to define how projected index is computed.
        Default value is "ConstantIndex". It is defaulted to "ForwardIndex"
        for Preferreds and Brazilian Debenture bonds.
    quote_fallback_logic : QuoteFallbackLogic, optional
        Enumeration used to define the fallback logic for the quotation of the
        instrument. Available values are:
        - "None": it means that there's no fallback logic. For example, if the user asks
          for a "Ask" price and instrument is only quoted with a "Bid" price, it is an
          error case.
        - "BestField" : it means that there's a fallback logic to use another market
          data field as quoted price. For example, if the user asks for a "Ask" price
          and instrument is only quoted with a "Bid" price, "Bid" price can be used.
    redemption_date_type : RedemptionDateType, optional
        Redemption type of the bond. It is used to compute the default redemption date:
        - RedemptionAtMaturityDate : yield and price are computed at maturity date.
        - RedemptionAtCallDate : yield and price are computed at call date (next call
          date by default).
        - RedemptionAtPutDate : yield and price are computed at put date (next put date
          by default)..
        - RedemptionAtWorstDate : yield and price are computed at the lowest yield date.
        - RedemptionAtSinkDate : yield and price are computed at sinking fund date.
        - RedemptionAtParDate : yield and price are computed at next par.
        - RedemptionAtPremiumDate : yield and price are computed at next premium.
        - RedemptionAtMakeWholeCallDate : yield and price are computed at Make Whole
          Call date.
        - RedemptionAtAverageLife : yield and price are computed at average life (case
          of sinkable bonds)
        - RedemptionAtNextDate : yield and price are computed at next redemption date
          available.

          Default value is "RedemptionAtWorstDate" for callable
          bond, "RedemptionAtBestDate" for puttable bond or "RedemptionAtMaturityDate".
    rounding_parameters : BondRoundingParameters, optional
        Definition of rounding parameters to be applied on accrued, price or yield.
        By default, rounding parameters are the ones defined in the bond structure.
    volatility_term_structure_type : VolatilityTermStructureType, optional
        Stock volatility trem structure type to use during pricing. Applicable for
        Convertible Bonds.
    volatility_type : VolatilityType, optional
        Volatility type to use during pricing. Applicable for Convertible Bonds.
    yield_type : YieldType, optional
        yield_type that specifies the rate structure.
        The default value is Native.
    adjusted_clean_price : float, optional
        Inflation Adjusted Clean price to override and that will be used as pricing
        analysis input. The currency of the clean price is the cash flow currency (that
        can be different to deal currency especially if "ComputeCashFlowWithReportCcy"
        flag has been set to true). No override is applied by default. Note that only
        one pricing analysis input should be defined.
    adjusted_dirty_price : float, optional
        Inflation Adjusted Dirty price to override and that will be used as pricing
        analysis input. The currency of the dirty price is the cash flow currency (that
        can be different to deal currency especially if "ComputeCashFlowWithReportCcy"
        flag has been set to true). No override is applied by default. Note that only
        one pricing analysis input should be defined.
    adjusted_yield_percent : float, optional
        Inflation Adjusted Yield (expressed in percent) to override and that will be
        used as pricing analysis input. No override is applied by default.
        Note that only one pricing analysis input should be defined.
    apply_tax_to_full_pricing : bool, optional
        Tax Parameters Flag to set these tax parameters for all
        pricing/schedule/risk/spread.
        By default Tax Params are applied only to Muni.
    asset_swap_spread_bp : float, optional
        AssetSwapSpread to override and that will be used as pricing analysis input to
        compute the bond price. No override is applied by default. Note that
        only one pricing anlysis input should be defined.
    benchmark_at_issue_price : float, optional
        Price of benchmark at issue to override and that will be used to compute
        benchmark at redemption spread. No override is applied by default and
        price is computed or retrieved from market data.
    benchmark_at_issue_ric : str, optional
        Ric of benchmark at issue to override and that will be used as pricing analysis
        input to compute the bond price. Optional. No override is applied by default.
        Note that only one pricing analysis input should be defined.
    benchmark_at_issue_spread_bp : float, optional
        Spread of benchmark at issue to override and that will be used as pricing
        analysis input to compute the bond price. No override is applied by
        default. Note that only one pricing analysis input should be defined.
    benchmark_at_issue_yield_percent : float, optional
        Yield of benchmark at issue to override and that will be used to compute
        benchmark at redemption spread. No override is applied by default and
        yield is computed or retrieved from market data.
    benchmark_at_redemption_price : float, optional
        Price of benchmark at redemption to override and that will be used to compute
        benchmark at redemption spread. No override is applied by default and
        price is computed or retrieved from market data.
    benchmark_at_redemption_spread_bp : float, optional
        Spread of benchmark at redemption to override and that will be used as pricing
        analysis input to compute the bond price. No override is applied by
        default. Note that only one pricing analysis input should be defined.
    benchmark_at_redemption_yield_percent : float, optional
        Yield of benchmark at redemption to override and that will be used to compute
        benchmark at redemption spread. No override is applied by default and
        yield is computed or retrieved from market data.
    bond_recovery_rate_percent : float, optional
        Bond Recovery Rate Percent set for convertible bond. Applicable for Convertible
        Bonds.
    cash_amount : float, optional
        Cash amount to override and that will be used as pricing analysis input.
        No override is applied by default. Note that only one pricing analysis
        input should be defined.
    cds_recovery_rate_percent : float, optional
        Recovery rate percent used in credit curve related to convertible. Applicable
        for Convertible Bonds.
    clean_price : float, optional
        Clean price to override and that will be used as pricing analysis input. The
        currency of the clean price is the cash flow currency (that can be different to
        deal currency especially if "ComputeCashFlowWithReportCcy" flag has been set to
        true). No override is applied by default. Note that only one pricing analysis
        input should be defined.
    concession_fee : float, optional
        Fee to apply to the bond price; It is expressed in the same unit that the bond
        price (percent or cash).
    current_yield_percent : float, optional
        Current Yield (expressed in percent) to override and that will be used as
        pricing analysis input. No override is applied by default. Note that
        only one pricing anlysis input should be defined.
    dirty_price : float, optional
        Dirty price to override and that will be used as pricing analysis input. The
        currency of the dirty price is the cash flow currency (that can be different to
        deal currency especially if "ComputeCashFlowWithReportCcy" flag has been set to
        true). No override is applied by default. Note that only one pricing analysis
        input should be defined.
    discount_margin_bp : float, optional
        Discount Margin basis points to override and that will be used as pricing
        analysis input. Available only for Floating Rate Notes. No override is
        applied by default. Note that only one pricing anlysis input should be defined.
    discount_percent : float, optional
        Discount (expressed in percent) to override and that will be used as pricing
        analysis input. Should be used only for bond quoted in discount. Optional. No
        override is applied by default. Note that only one pricing anlysis input should
        be defined.
    dividend_yield_percent : float, optional
        Underlying Stock dividend yield percent. Applicable for Convertible Bonds.
    edsf_benchmark_curve_yield_percent : float, optional
        Yield of Euro-Dollar future benchmark curve (Edsf) to override and that will be
        used to compute Euro-Dollar (Edsf) spread. No override is applied by
        default and yield is computed or retrieved from market data.
    edsf_spread_bp : float, optional
        Spread of Euro-Dollar future benchmark curve (Edsf) to override and that will be
        used as pricing analysis input to compute the bond price. This spread is
        computed for USD Bond whose maturity is under 2 Years. No override is
        applied by default. Note that only one pricing anlysis input should be defined.
    efp_benchmark_price : float, optional
        Price of EFP benchmark to override and that will be used to compute benchmark at
        redemption spread in case the bond is an australian FRN. No override
        is applied by default and price is computed or retrieved from market data.
    efp_benchmark_ric : str, optional
        RIC of EFP benchmark to override and that will be used as pricing analysis input
        to compute the bond price in case the bond is an australian FRN. Ric can be
        only "YTTc1" or "YTCc1".
        Default value is "YTTc1".
    efp_benchmark_yield_percent : float, optional
        Yield of EFP benchmark to override and that will be used to compute benchmark at
        redemption spread in case the bond is an australian FRN. No override
        is applied by default and yield is computed or retrieved from market data.
    efp_spread_bp : float, optional
        Spread of EFP benchmark to override and that will be used as pricing analysis
        input to compute the bond price in case the bond is an australian FRN.
        No override is applied by default. Note that only one pricing analysis input
        should be defined.
    flat_credit_spread_bp : float, optional
        Flat credit spread applied during pricing in basis points. Applicable when
        SpreadType = FlatSpread. Applicable for Convertible Bonds.
    flat_credit_spread_tenor : str, optional
        Flat credit spread tenor on credit curve used during pricing to source credit
        spread value. Applicable for Convertible Bonds.
    fx_stock_correlation : float, optional
        Correlation rate between underlying stock price and FX rate. Applicable for
        cross-currency Convertible Bonds.
    fx_volatility_percent : float, optional
        FX volatility rate percent. Applicable for cross-currency Convertible Bonds.
    fx_volatility_tenor : str, optional
        Tenor on FX volatility to source FX volatility Rate Percent. Applicable for
        cross-currency Convertible Bonds.
    gov_country_benchmark_curve_price : float, optional
        Price of government country benchmark to override and that will be used to
        compute user defined spread. No override is applied by default and price is
        computed or retrieved from market data.
    gov_country_benchmark_curve_yield_percent : float, optional
        Yield of government country benchmark to override and that will be used to
        compute government country spread. No override is applied by default
        and yield is computed or retrieved from market data.
    gov_country_spread_bp : float, optional
        Spread of government country benchmark to override and that will be used as
        pricing analysis input to compute the bond price. Optional. No override is
        applied by default. Note that only one pricing analysis input should be defined.
    government_benchmark_curve_price : float, optional
        Price of government benchmark to override and that will be used to compute user
        defined spread. No override is applied by default and price is
        computed or retrieved from market data.
    government_benchmark_curve_yield_percent : float, optional
        Yield of government benchmark to override and that will be used to compute
        government spread. No override is applied by default and yield is
        computed or retrieved from market data.
    government_spread_bp : float, optional
        Spread of government benchmark to override and that will be used as pricing
        analysis input to compute the bond price. No override is applied by
        default. Note that only one pricing analysis input should be defined.
    issuer_benchmark_curve_yield_percent : float, optional
        Yield of issuer benchmark to override and that will be used to compute issuer
        spread. No override is applied by default and yield is computed or retrieved
        from market data.
    issuer_spread_bp : float, optional
        Spread of issuer benchmark to override and that will be used as pricing analysis
        input to compute the bond price. This spread is computed is for coprorate bonds.
        Optional. No override is applied by default. Note that only one pricing anlysis
        input should be defined.
    market_data_date : str, optional
        The market data date for pricing.
        By default, the market_data_date date is the valuation_date or Today
    market_value_in_deal_ccy : float, optional
        Market value in deal currency. This field can be used to compute notionalAmount
        to apply to get this market value. Optional. By default the value is computed
        from notional amount. NotionalAmount field, market_value_in_deal_ccy field and
        market_value_in_report_ccy field cannot be set at defined at the same time.
    market_value_in_report_ccy : float, optional
        Market value in report currency. This field can be used to compute
        notionalAmount to apply to get this market value. By default the value
        is computed from notional amount. NotionalAmount field, market_value_in_deal_ccy
        field and market_value_in_report_ccy field cannot be set at defined at the same
        time.
    net_price : float, optional
        Net price to override and that will be used as pricing analysis input.
        No override is applied by default. Note that only one pricing anlysis input
        should be defined.
    neutral_yield_percent : float, optional
        Neutral Yield (expressed in percent) to override and that will be used as
        pricing analysis input. This is available only for floating rate notes.
        No override is applied by default. Note that only one pricing analysis
        input should be defined.
    ois_zc_benchmark_curve_yield_percent : float, optional
        Yield of OIS benchmark to override and that will be used to compute OIS spread.
        No override is applied by default and yield is computed or retrieved from market
        data.
    ois_zc_spread_bp : float, optional
        Yield of OIS benchmark to override and that will be used as pricing analysis
        input to compute the bond price. No override is applied by default.
        Note that only one pricing analysis input should be defined.
    option_adjusted_spread_bp : float, optional
        Option Adjusted Spread to override and that will be used as pricing analysis
        input to compute the bond price. No override is applied by default.
        Note that only one pricing analysis input should be defined.
    price : float, optional
        Price to override and that will be used as pricing analysis input. This price
        can be the clean price or dirty price depending on price type defined in bond
        structure. The currency of the price is the cash flow currency (that can be
        different to deal currency especially if "ComputeCashFlowWithReportCcy" flag has
        been set to true). Optional. No override is applied by default. Note that only
        one pricing analysis input should be defined.
    quoted_price : float, optional
        Quoted price to override and that will be used as pricing analysis input. Note
        that a quoted price can be a price, a yield, a discount margin, a spread,...
        depending on quotation type. The currency of the quoted price in case the bonnd
        is price-quoted or cash-quoted is the deal currency (that can be different to
        cash flow currency especially if "ComputeCashFlowWithReportCcy" flag has been
        set to true). No override is applied by default. Note that only one pricing
        analysis input should be defined.
    rating_benchmark_curve_yield_percent : float, optional
        Yield of rating benchmark to override and that will be used to compute rating
        spread. No override is applied by default and yield is computed or retrieved
        from market data.
    rating_spread_bp : float, optional
        Spread of rating benchmark to override and that will be used as pricing analysis
        input to compute the bond price. No override is applied by default.
        Note that only one pricing anlysis input should be defined.
    redemption_date : str, optional
        Redemption date that defines the end date for yield and price computation. Used
        only if redemption date type is set to "RedemptionAtCustomDate"
    sector_rating_benchmark_curve_yield_percent : float, optional
        Yield of sector rating benchmark to override and that will be used to compute
        sector rating spread. No override is applied by default and yield is computed
        or retrieved from market data.
    sector_rating_spread_bp : float, optional
        Spread of sector rating benchmark to override and that will be used as pricing
        analysis input to compute the bond price. No override is applied by default.
        Note that only one pricing anlysis input should be defined.
    settlement_convention : str, optional
        Settlement convention for the bond. By default the rule is that valuation_date =
        trade_date + settlement_convention. By default use the settlement tenor defined
        in the bond structure. Only two parameters among "settlement_convention",
        "market_data_date" and "valuation_date" can be overriden at the same time.
    simple_margin_bp : float, optional
        Simple Margin basis points  to override and that will be used as pricing
        analysis input. Available only for Floating Rate Notes. No override is
        applied by default. Note that only one pricing anlysis input should be defined.
    stock_borrow_rate_percent : float, optional
        Underlying stock borrow rate percent. Applicable for Convertible Bonds.
    stock_flat_volatility_percent : float, optional
        Underlying stock volatility percent used for convertible pricing. Applicable
        when volatility_type = Flat Applicable for Convertible Bonds.
    stock_flat_volatility_tenor : str, optional
        Underlying Stock volatility tenor used during pricing to source volatility
        percent value. Applicable when volatility_type = Flat Applicable for Convertible
        Bonds.
    stock_price_on_default : float, optional
        Assumed stock price agreed in event of default. Applicable for Convertible
        Bonds.
    strip_yield_percent : float, optional
        Strip Yield (expressed in percent) to override and that will be used as pricing
        analysis input. No override is applied by default. Note that only one pricing
        anlysis input should be defined.
    swap_benchmark_curve_yield_percent : float, optional
        Yield of swap benchmark to override and that will be used to compute swap
        spread. No override is applied by default and yield is computed or
        retrieved from market data.
    swap_spread_bp : float, optional
        Spread of swap benchmark to override and that will be used as pricing analysis
        input to compute the bond price. No override is applied by default.
        Note that only one pricing analysis input should be defined.
    tax_on_capital_gain_percent : float, optional
        Tax Rate on capital gain expressed in percent.
        By default no tax is applied that means value is equal to 0.
    tax_on_coupon_percent : float, optional
        Tax Rate on Coupon  expressed in percent.
        By default no tax is applied that means value is equal to 0.
    tax_on_price_percent : float, optional
        Tax Rate on price expressed in percent.
        By default no tax is applied that means value is equal to 0.
    tax_on_yield_percent : float, optional
        Tax Rate on Yield expressed in percent. Also named Tax on Yield Optional.
        By default no tax is applied that means value is equal to 0.
    use_settlement_date_from_quote : bool, optional
        Specify whether to use the settlment date of the quote or the one computed from
        the MarketData Date.
    user_defined_benchmark_price : float, optional
        price of user defined instrument to override and that will be used to compute
        user defined spread. No override is applied by default and price is computed
        or retrieved from market data.
    user_defined_benchmark_yield_percent : float, optional
        Yield of user defined instrument to override and that will be used to compute
        user defined spread. No override is applied by default and yield is computed
        or retrieved from market data.
    user_defined_spread_bp : float, optional
        Spread of user defined instrument to override and that will be used as pricing
        analysis input to compute the bond price. No override is applied by default.
        Note that only one pricing analysis input should be defined.
    valuation_date : str, optional
        The valuation date for pricing. If not set the valuation date is equal
        to market_data_date or Today. For assets that contains a settlement_convention,
        the default valuation date is equal to the settlementdate of the Asset that
        is usually the trade_date+settlement_convention.
    yield_percent : float, optional
        Yield (expressed in percent) to override and that will be used as pricing
        analysis input. No override is applied by default. Note that only one pricing
        analysis input should be defined.
    z_spread_bp : float, optional
        ZSpread to override and that will be used as pricing analysis input to compute
        the bond price. No override is applied by default. Note that only one pricing
        analysis input should be defined.

    Examples
    --------
    >>> import refinitiv.data.content.ipa.financial_contracts as rdf
    >>> definition = rdf.bond.Definition(
    ...    instrument_code="US5YT=RR",
    ...    payment_business_day_convention=rdf.bond.BusinessDayConvention.PREVIOUS_BUSINESS_DAY,
    ...    pricing_parameters=rdf.bond.PricingParameters(
    ...        benchmark_yield_selection_mode=rdf.bond.BenchmarkYieldSelectionMode.INTERPOLATE
    ...    ),
    ...    outputs=[rdf.Outputs.DATA, rdf.Outputs.HEADERS],
    ...    fields=["InstrumentDescription", "MarketDataDate", "Price", "YieldPercent", "ZSpreadBp"]
    ...)
    >>> response = definition.get_data()
    """

    def __init__(
        self,
        trade_date: Optional[str] = None,
        benchmark_yield_selection_mode: Optional[BenchmarkYieldSelectionMode] = None,
        credit_spread_type: Optional[CreditSpreadType] = None,
        dividend_type: Optional[DividendType] = None,
        fx_price_side: Optional[PriceSide] = None,
        price_side: Optional[PriceSide] = None,
        projected_index_calculation_method: Optional[
            ProjectedIndexCalculationMethod
        ] = None,
        quote_fallback_logic: Optional[QuoteFallbackLogic] = None,
        redemption_date_type: Optional[RedemptionDateType] = None,
        rounding_parameters: Union[BondRoundingParameters, dict] = None,
        volatility_term_structure_type: Optional[VolatilityTermStructureType] = None,
        volatility_type: Optional[VolatilityType] = None,
        yield_type: Optional[YieldType] = None,
        adjusted_clean_price: Optional[float] = None,
        adjusted_dirty_price: Optional[float] = None,
        adjusted_yield_percent: Optional[float] = None,
        apply_tax_to_full_pricing: Optional[bool] = None,
        asset_swap_spread_bp: Optional[float] = None,
        benchmark_at_issue_price: Optional[float] = None,
        benchmark_at_issue_ric: Optional[str] = None,
        benchmark_at_issue_spread_bp: Optional[float] = None,
        benchmark_at_issue_yield_percent: Optional[float] = None,
        benchmark_at_redemption_price: Optional[float] = None,
        benchmark_at_redemption_spread_bp: Optional[float] = None,
        benchmark_at_redemption_yield_percent: Optional[float] = None,
        bond_recovery_rate_percent: Optional[float] = None,
        cash_amount: Optional[float] = None,
        cds_recovery_rate_percent: Optional[float] = None,
        clean_price: Optional[float] = None,
        concession_fee: Optional[float] = None,
        current_yield_percent: Optional[float] = None,
        dirty_price: Optional[float] = None,
        discount_margin_bp: Optional[float] = None,
        discount_percent: Optional[float] = None,
        dividend_yield_percent: Optional[float] = None,
        edsf_benchmark_curve_yield_percent: Optional[float] = None,
        edsf_spread_bp: Optional[float] = None,
        efp_benchmark_price: Optional[float] = None,
        efp_benchmark_ric: Optional[str] = None,
        efp_benchmark_yield_percent: Optional[float] = None,
        efp_spread_bp: Optional[float] = None,
        flat_credit_spread_bp: Optional[float] = None,
        flat_credit_spread_tenor: Optional[str] = None,
        fx_stock_correlation: Optional[float] = None,
        fx_volatility_percent: Optional[float] = None,
        fx_volatility_tenor: Optional[str] = None,
        gov_country_benchmark_curve_price: Optional[float] = None,
        gov_country_benchmark_curve_yield_percent: Optional[float] = None,
        gov_country_spread_bp: Optional[float] = None,
        government_benchmark_curve_price: Optional[float] = None,
        government_benchmark_curve_yield_percent: Optional[float] = None,
        government_spread_bp: Optional[float] = None,
        issuer_benchmark_curve_yield_percent: Optional[float] = None,
        issuer_spread_bp: Optional[float] = None,
        market_data_date: Optional[str] = None,
        market_value_in_deal_ccy: Optional[float] = None,
        market_value_in_report_ccy: Optional[float] = None,
        net_price: Optional[float] = None,
        neutral_yield_percent: Optional[float] = None,
        ois_zc_benchmark_curve_yield_percent: Optional[float] = None,
        ois_zc_spread_bp: Optional[float] = None,
        option_adjusted_spread_bp: Optional[float] = None,
        price: Optional[float] = None,
        quoted_price: Optional[float] = None,
        rating_benchmark_curve_yield_percent: Optional[float] = None,
        rating_spread_bp: Optional[float] = None,
        redemption_date: Optional[str] = None,
        sector_rating_benchmark_curve_yield_percent: Optional[float] = None,
        sector_rating_spread_bp: Optional[float] = None,
        settlement_convention: Optional[str] = None,
        simple_margin_bp: Optional[float] = None,
        stock_borrow_rate_percent: Optional[float] = None,
        stock_flat_volatility_percent: Optional[float] = None,
        stock_flat_volatility_tenor: Optional[str] = None,
        stock_price_on_default: Optional[float] = None,
        strip_yield_percent: Optional[float] = None,
        swap_benchmark_curve_yield_percent: Optional[float] = None,
        swap_spread_bp: Optional[float] = None,
        tax_on_capital_gain_percent: Optional[float] = None,
        tax_on_coupon_percent: Optional[float] = None,
        tax_on_price_percent: Optional[float] = None,
        tax_on_yield_percent: Optional[float] = None,
        use_settlement_date_from_quote: Optional[bool] = None,
        user_defined_benchmark_price: Optional[float] = None,
        user_defined_benchmark_yield_percent: Optional[float] = None,
        user_defined_spread_bp: Optional[float] = None,
        valuation_date: Optional[str] = None,
        yield_percent: Optional[float] = None,
        z_spread_bp: Optional[float] = None,
    ) -> None:
        super().__init__()
        self.trade_date = trade_date
        self.benchmark_yield_selection_mode = benchmark_yield_selection_mode
        self.credit_spread_type = credit_spread_type
        self.dividend_type = dividend_type
        self.fx_price_side = fx_price_side
        self.price_side = price_side
        self.projected_index_calculation_method = projected_index_calculation_method
        self.quote_fallback_logic = quote_fallback_logic
        self.redemption_date_type = redemption_date_type
        self.rounding_parameters = rounding_parameters
        self.volatility_term_structure_type = volatility_term_structure_type
        self.volatility_type = volatility_type
        self.yield_type = yield_type
        self.adjusted_clean_price = adjusted_clean_price
        self.adjusted_dirty_price = adjusted_dirty_price
        self.adjusted_yield_percent = adjusted_yield_percent
        self.apply_tax_to_full_pricing = apply_tax_to_full_pricing
        self.asset_swap_spread_bp = asset_swap_spread_bp
        self.benchmark_at_issue_price = benchmark_at_issue_price
        self.benchmark_at_issue_ric = benchmark_at_issue_ric
        self.benchmark_at_issue_spread_bp = benchmark_at_issue_spread_bp
        self.benchmark_at_issue_yield_percent = benchmark_at_issue_yield_percent
        self.benchmark_at_redemption_price = benchmark_at_redemption_price
        self.benchmark_at_redemption_spread_bp = benchmark_at_redemption_spread_bp
        self.benchmark_at_redemption_yield_percent = (
            benchmark_at_redemption_yield_percent
        )
        self.bond_recovery_rate_percent = bond_recovery_rate_percent
        self.cash_amount = cash_amount
        self.cds_recovery_rate_percent = cds_recovery_rate_percent
        self.clean_price = clean_price
        self.concession_fee = concession_fee
        self.current_yield_percent = current_yield_percent
        self.dirty_price = dirty_price
        self.discount_margin_bp = discount_margin_bp
        self.discount_percent = discount_percent
        self.dividend_yield_percent = dividend_yield_percent
        self.edsf_benchmark_curve_yield_percent = edsf_benchmark_curve_yield_percent
        self.edsf_spread_bp = edsf_spread_bp
        self.efp_benchmark_price = efp_benchmark_price
        self.efp_benchmark_ric = efp_benchmark_ric
        self.efp_benchmark_yield_percent = efp_benchmark_yield_percent
        self.efp_spread_bp = efp_spread_bp
        self.flat_credit_spread_bp = flat_credit_spread_bp
        self.flat_credit_spread_tenor = flat_credit_spread_tenor
        self.fx_stock_correlation = fx_stock_correlation
        self.fx_volatility_percent = fx_volatility_percent
        self.fx_volatility_tenor = fx_volatility_tenor
        self.gov_country_benchmark_curve_price = gov_country_benchmark_curve_price
        self.gov_country_benchmark_curve_yield_percent = (
            gov_country_benchmark_curve_yield_percent
        )
        self.gov_country_spread_bp = gov_country_spread_bp
        self.government_benchmark_curve_price = government_benchmark_curve_price
        self.government_benchmark_curve_yield_percent = (
            government_benchmark_curve_yield_percent
        )
        self.government_spread_bp = government_spread_bp
        self.issuer_benchmark_curve_yield_percent = issuer_benchmark_curve_yield_percent
        self.issuer_spread_bp = issuer_spread_bp
        self.market_data_date = market_data_date
        self.market_value_in_deal_ccy = market_value_in_deal_ccy
        self.market_value_in_report_ccy = market_value_in_report_ccy
        self.net_price = net_price
        self.neutral_yield_percent = neutral_yield_percent
        self.ois_zc_benchmark_curve_yield_percent = ois_zc_benchmark_curve_yield_percent
        self.ois_zc_spread_bp = ois_zc_spread_bp
        self.option_adjusted_spread_bp = option_adjusted_spread_bp
        self.price = price
        self.quoted_price = quoted_price
        self.rating_benchmark_curve_yield_percent = rating_benchmark_curve_yield_percent
        self.rating_spread_bp = rating_spread_bp
        self.redemption_date = redemption_date
        self.sector_rating_benchmark_curve_yield_percent = (
            sector_rating_benchmark_curve_yield_percent
        )
        self.sector_rating_spread_bp = sector_rating_spread_bp
        self.settlement_convention = settlement_convention
        self.simple_margin_bp = simple_margin_bp
        self.stock_borrow_rate_percent = stock_borrow_rate_percent
        self.stock_flat_volatility_percent = stock_flat_volatility_percent
        self.stock_flat_volatility_tenor = stock_flat_volatility_tenor
        self.stock_price_on_default = stock_price_on_default
        self.strip_yield_percent = strip_yield_percent
        self.swap_benchmark_curve_yield_percent = swap_benchmark_curve_yield_percent
        self.swap_spread_bp = swap_spread_bp
        self.tax_on_capital_gain_percent = tax_on_capital_gain_percent
        self.tax_on_coupon_percent = tax_on_coupon_percent
        self.tax_on_price_percent = tax_on_price_percent
        self.tax_on_yield_percent = tax_on_yield_percent
        self.use_settlement_date_from_quote = use_settlement_date_from_quote
        self.user_defined_benchmark_price = user_defined_benchmark_price
        self.user_defined_benchmark_yield_percent = user_defined_benchmark_yield_percent
        self.user_defined_spread_bp = user_defined_spread_bp
        self.valuation_date = valuation_date
        self.yield_percent = yield_percent
        self.z_spread_bp = z_spread_bp

    @property
    def benchmark_yield_selection_mode(self):
        """
        The benchmark yield selection mode:
        - Interpolate : do an interpolatation on yield curve to compute the reference
          yield.
        - Nearest : use the nearest point to find the reference yield. Optional. Default
          value is "Interpolate".
        :return: enum BenchmarkYieldSelectionMode
        """
        return self._get_enum_parameter(
            BenchmarkYieldSelectionMode, "benchmarkYieldSelectionMode"
        )

    @benchmark_yield_selection_mode.setter
    def benchmark_yield_selection_mode(self, value):
        self._set_enum_parameter(
            BenchmarkYieldSelectionMode, "benchmarkYieldSelectionMode", value
        )

    @property
    def credit_spread_type(self):
        """
        Credit curve spread type to use during pricing. Applicable for Convertible
        Bonds.
        :return: enum CreditSpreadType
        """
        return self._get_enum_parameter(CreditSpreadType, "creditSpreadType")

    @credit_spread_type.setter
    def credit_spread_type(self, value):
        self._set_enum_parameter(CreditSpreadType, "creditSpreadType", value)

    @property
    def dividend_type(self):
        """
        Underlying stock dividend type used during pricing convertible bond. Applicable
        for Convertible Bonds.
        :return: enum DividendType
        """
        return self._get_enum_parameter(DividendType, "dividendType")

    @dividend_type.setter
    def dividend_type(self, value):
        self._set_enum_parameter(DividendType, "dividendType", value)

    @property
    def fx_price_side(self):
        """
        FX price side to consider when retrieving FX rates (Mid, Bid, Ask, Last, Close)
        :return: enum PriceSide
        """
        return self._get_enum_parameter(PriceSide, "fxPriceSide")

    @fx_price_side.setter
    def fx_price_side(self, value):
        self._set_enum_parameter(PriceSide, "fxPriceSide", value)

    @property
    def price_side(self):
        """
        Quoted price side of the bond to use for pricing Analysis: Bid(Bid value),
        Ask(Ask value), Mid(Mid value) Optional. By default the "Mid" price of the bond
        is used.
        :return: enum PriceSide
        """
        return self._get_enum_parameter(PriceSide, "priceSide")

    @price_side.setter
    def price_side(self, value):
        self._set_enum_parameter(PriceSide, "priceSide", value)

    @property
    def projected_index_calculation_method(self):
        """
        Flag used to define how projected index is computed. Avalaible values are:
        - "ConstantIndex" : future index values are considered as constant and equal to
          projected index value.
        - "ForwardIndex" : future index values are computed using a forward curve.
          Optional. Default value is "ConstantIndex". It is defaulted to "ForwardIndex"
          for Preferreds and Brazilian Debenture bonds.
        :return: enum ProjectedIndexCalculationMethod
        """
        return self._get_enum_parameter(
            ProjectedIndexCalculationMethod, "projectedIndexCalculationMethod"
        )

    @projected_index_calculation_method.setter
    def projected_index_calculation_method(self, value):
        self._set_enum_parameter(
            ProjectedIndexCalculationMethod, "projectedIndexCalculationMethod", value
        )

    @property
    def quote_fallback_logic(self):
        """
        Enumeration used to define the fallback logic for the quotation of the
        instrument. Available values are:
        - "None": it means that there's no fallback logic. For example, if the user asks
          for a "Ask" price and instrument is only quoted with a "Bid" price, it is an
          error case.
        - "BestField" : it means that there's a fallback logic to use another market
          data field as quoted price. For example, if the user asks for a "Ask" price
          and instrument is only quoted with a "Bid" price, "Bid" price can be used.
        :return: enum QuoteFallbackLogic
        """
        return self._get_enum_parameter(QuoteFallbackLogic, "quoteFallbackLogic")

    @quote_fallback_logic.setter
    def quote_fallback_logic(self, value):
        self._set_enum_parameter(QuoteFallbackLogic, "quoteFallbackLogic", value)

    @property
    def redemption_date_type(self):
        """
        Redemption type of the bond. It is used to compute the default redemption date:
        - RedemptionAtMaturityDate : yield and price are computed at maturity date.
        - RedemptionAtCallDate : yield and price are computed at call date (next call
          date by default).
        - RedemptionAtPutDate : yield and price are computed at put date (next put date
          by default)..
        - RedemptionAtWorstDate : yield and price are computed at the lowest yield date.
        - RedemptionAtSinkDate : yield and price are computed at sinking fund date.
        - RedemptionAtParDate : yield and price are computed at next par.
        - RedemptionAtPremiumDate : yield and price are computed at next premium.
        - RedemptionAtMakeWholeCallDate : yield and price are computed at Make Whole
          Call date.
        - RedemptionAtAverageLife : yield and price are computed at average life (case
          of sinkable bonds)
        - RedemptionAtNextDate : yield and price are computed at next redemption date
          available. Optional. Default value is "RedemptionAtWorstDate" for callable
          bond, "RedemptionAtBestDate" for puttable bond or "RedemptionAtMaturityDate".
        :return: enum RedemptionDateType
        """
        return self._get_enum_parameter(RedemptionDateType, "redemptionDateType")

    @redemption_date_type.setter
    def redemption_date_type(self, value):
        self._set_enum_parameter(RedemptionDateType, "redemptionDateType", value)

    @property
    def rounding_parameters(self):
        """
        Definition of rounding parameters to be applied on accrued, price or yield.
        Optional. By default, rounding parameters are the ones defined in the bond
        structure.
        :return: object BondRoundingParameters
        """
        return self._get_object_parameter(BondRoundingParameters, "roundingParameters")

    @rounding_parameters.setter
    def rounding_parameters(self, value):
        self._set_object_parameter(BondRoundingParameters, "roundingParameters", value)

    @property
    def volatility_term_structure_type(self):
        """
        Stock volatility trem structure type to use during pricing. Applicable for
        Convertible Bonds.
        :return: enum VolatilityTermStructureType
        """
        return self._get_enum_parameter(
            VolatilityTermStructureType, "volatilityTermStructureType"
        )

    @volatility_term_structure_type.setter
    def volatility_term_structure_type(self, value):
        self._set_enum_parameter(
            VolatilityTermStructureType, "volatilityTermStructureType", value
        )

    @property
    def volatility_type(self):
        """
        Volatility type to use during pricing. Applicable for Convertible Bonds.
        :return: enum VolatilityType
        """
        return self._get_enum_parameter(VolatilityType, "volatilityType")

    @volatility_type.setter
    def volatility_type(self, value):
        self._set_enum_parameter(VolatilityType, "volatilityType", value)

    @property
    def yield_type(self):
        """
        YieldType that specifies the rate structure.
        - Native : no specific yield type is defined.
        - UsGovt_Actual_Actual_6M : US Govt Act/Act 6M YTA.
        - Isma_30_360_6M : ISMA 30/360 6M YTA.
        - Euroland_Actual_Actual_6M : Euroland Equivalent Act/Act 6M YTA.
        - Money_Market_Actual_360_6M : Money Market Act/360 6M YTA.
        - Money_Market_Actual_365_6M : Money Market Act/365 6M YTA.
        - Money_Market_Actual_Actual_6M : Money Market Act/Act 6M YTA.
        - Bond_Actual_364_6M : Bond Market Act/364 6M YTA.
        - Japanese_Simple_JAP_6M : Japanese Simple JAP 6M YTA.
        - Japanese_Compunded_30_360_6M : Japanese Compounded 30/360 6M YTA.
        - Moosmueller_30_360_6M : Moosmueller 30/360 6M YTA.
        - Braess_Frangmeyer_30_360_6M : Braess-Frangmeyer 30/360 6M YTA.
        - Weekend_30_360 : Week End 30/360 6M YTA Optional. The default value is Native.
        :return: enum YieldType
        """
        return self._get_enum_parameter(YieldType, "yieldType")

    @yield_type.setter
    def yield_type(self, value):
        self._set_enum_parameter(YieldType, "yieldType", value)

    @property
    def adjusted_clean_price(self):
        """
        Inflation Adjusted Clean price to override and that will be used as pricing
        analysis input. The currency of the clean price is the cash flow currency (that
        can be different to deal currency especially if "ComputeCashFlowWithReportCcy"
        flag has been set to true). Optional. No override is applied by default. Note
        that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("adjustedCleanPrice")

    @adjusted_clean_price.setter
    def adjusted_clean_price(self, value):
        self._set_parameter("adjustedCleanPrice", value)

    @property
    def adjusted_dirty_price(self):
        """
        Inflation Adjusted Dirty price to override and that will be used as pricing
        analysis input. The currency of the dirty price is the cash flow currency (that
        can be different to deal currency especially if "ComputeCashFlowWithReportCcy"
        flag has been set to true). Optional. No override is applied by default. Note
        that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("adjustedDirtyPrice")

    @adjusted_dirty_price.setter
    def adjusted_dirty_price(self, value):
        self._set_parameter("adjustedDirtyPrice", value)

    @property
    def adjusted_yield_percent(self):
        """
        Inflation Adjusted Yield (expressed in percent) to override and that will be
        used as pricing analysis input. Optional. No override is applied by default.
        Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("adjustedYieldPercent")

    @adjusted_yield_percent.setter
    def adjusted_yield_percent(self, value):
        self._set_parameter("adjustedYieldPercent", value)

    @property
    def apply_tax_to_full_pricing(self):
        """
        Tax Parameters Flag to set these tax parameters for all
        pricing/schedule/risk/spread. Optional. By default Tax Params are applied only
        to Muni.
        :return: bool
        """
        return self._get_parameter("applyTaxToFullPricing")

    @apply_tax_to_full_pricing.setter
    def apply_tax_to_full_pricing(self, value):
        self._set_parameter("applyTaxToFullPricing", value)

    @property
    def asset_swap_spread_bp(self):
        """
        AssetSwapSpread to override and that will be used as pricing analysis input to
        compute the bond price. Optional. No override is applied by default. Note that
        only one pricing anlysis input should be defined.
        :return: float
        """
        return self._get_parameter("assetSwapSpreadBp")

    @asset_swap_spread_bp.setter
    def asset_swap_spread_bp(self, value):
        self._set_parameter("assetSwapSpreadBp", value)

    @property
    def benchmark_at_issue_price(self):
        """
        Price of benchmark at issue to override and that will be used to compute
        benchmark at redemption spread. Optional. No override is applied by default and
        price is computed or retrieved from market data.
        :return: float
        """
        return self._get_parameter("benchmarkAtIssuePrice")

    @benchmark_at_issue_price.setter
    def benchmark_at_issue_price(self, value):
        self._set_parameter("benchmarkAtIssuePrice", value)

    @property
    def benchmark_at_issue_ric(self):
        """
        Ric of benchmark at issue to override and that will be used as pricing analysis
        input to compute the bond price. Optional. No override is applied by default.
        Note that only one pricing analysis input should be defined.
        :return: str
        """
        return self._get_parameter("benchmarkAtIssueRic")

    @benchmark_at_issue_ric.setter
    def benchmark_at_issue_ric(self, value):
        self._set_parameter("benchmarkAtIssueRic", value)

    @property
    def benchmark_at_issue_spread_bp(self):
        """
        Spread of benchmark at issue to override and that will be used as pricing
        analysis input to compute the bond price. Optional. No override is applied by
        default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("benchmarkAtIssueSpreadBp")

    @benchmark_at_issue_spread_bp.setter
    def benchmark_at_issue_spread_bp(self, value):
        self._set_parameter("benchmarkAtIssueSpreadBp", value)

    @property
    def benchmark_at_issue_yield_percent(self):
        """
        Yield of benchmark at issue to override and that will be used to compute
        benchmark at redemption spread. Optional. No override is applied by default and
        yield is computed or retrieved from market data.
        :return: float
        """
        return self._get_parameter("benchmarkAtIssueYieldPercent")

    @benchmark_at_issue_yield_percent.setter
    def benchmark_at_issue_yield_percent(self, value):
        self._set_parameter("benchmarkAtIssueYieldPercent", value)

    @property
    def benchmark_at_redemption_price(self):
        """
        Price of benchmark at redemption to override and that will be used to compute
        benchmark at redemption spread. Optional. No override is applied by default and
        price is computed or retrieved from market data.
        :return: float
        """
        return self._get_parameter("benchmarkAtRedemptionPrice")

    @benchmark_at_redemption_price.setter
    def benchmark_at_redemption_price(self, value):
        self._set_parameter("benchmarkAtRedemptionPrice", value)

    @property
    def benchmark_at_redemption_spread_bp(self):
        """
        Spread of benchmark at redemption to override and that will be used as pricing
        analysis input to compute the bond price. Optional. No override is applied by
        default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("benchmarkAtRedemptionSpreadBp")

    @benchmark_at_redemption_spread_bp.setter
    def benchmark_at_redemption_spread_bp(self, value):
        self._set_parameter("benchmarkAtRedemptionSpreadBp", value)

    @property
    def benchmark_at_redemption_yield_percent(self):
        """
        Yield of benchmark at redemption to override and that will be used to compute
        benchmark at redemption spread. Optional. No override is applied by default and
        yield is computed or retrieved from market data.
        :return: float
        """
        return self._get_parameter("benchmarkAtRedemptionYieldPercent")

    @benchmark_at_redemption_yield_percent.setter
    def benchmark_at_redemption_yield_percent(self, value):
        self._set_parameter("benchmarkAtRedemptionYieldPercent", value)

    @property
    def bond_recovery_rate_percent(self):
        """
        Bond Recovery Rate Percent set for convertible bond. Applicable for Convertible
        Bonds.
        :return: float
        """
        return self._get_parameter("bondRecoveryRatePercent")

    @bond_recovery_rate_percent.setter
    def bond_recovery_rate_percent(self, value):
        self._set_parameter("bondRecoveryRatePercent", value)

    @property
    def cash_amount(self):
        """
        Cash amount to override and that will be used as pricing analysis input.
        Optional. No override is applied by default. Note that only one pricing analysis
        input should be defined.
        :return: float
        """
        return self._get_parameter("cashAmount")

    @cash_amount.setter
    def cash_amount(self, value):
        self._set_parameter("cashAmount", value)

    @property
    def cds_recovery_rate_percent(self):
        """
        Recovery rate percent used in credit curve related to convertible. Applicable
        for Convertible Bonds.
        :return: float
        """
        return self._get_parameter("cdsRecoveryRatePercent")

    @cds_recovery_rate_percent.setter
    def cds_recovery_rate_percent(self, value):
        self._set_parameter("cdsRecoveryRatePercent", value)

    @property
    def clean_price(self):
        """
        Clean price to override and that will be used as pricing analysis input. The
        currency of the clean price is the cash flow currency (that can be different to
        deal currency especially if "ComputeCashFlowWithReportCcy" flag has been set to
        true). Optional. No override is applied by default. Note that only one pricing
        analysis input should be defined.
        :return: float
        """
        return self._get_parameter("cleanPrice")

    @clean_price.setter
    def clean_price(self, value):
        self._set_parameter("cleanPrice", value)

    @property
    def concession_fee(self):
        """
        Fee to apply to the bond price; It is expressed in the same unit that the bond
        price (percent or cash).
        :return: float
        """
        return self._get_parameter("concessionFee")

    @concession_fee.setter
    def concession_fee(self, value):
        self._set_parameter("concessionFee", value)

    @property
    def current_yield_percent(self):
        """
        Current Yield (expressed in percent) to override and that will be used as
        pricing analysis input. Optional. No override is applied by default. Note that
        only one pricing anlysis input should be defined.
        :return: float
        """
        return self._get_parameter("currentYieldPercent")

    @current_yield_percent.setter
    def current_yield_percent(self, value):
        self._set_parameter("currentYieldPercent", value)

    @property
    def dirty_price(self):
        """
        Dirty price to override and that will be used as pricing analysis input. The
        currency of the dirty price is the cash flow currency (that can be different to
        deal currency especially if "ComputeCashFlowWithReportCcy" flag has been set to
        true). Optional. No override is applied by default. Note that only one pricing
        analysis input should be defined.
        :return: float
        """
        return self._get_parameter("dirtyPrice")

    @dirty_price.setter
    def dirty_price(self, value):
        self._set_parameter("dirtyPrice", value)

    @property
    def discount_margin_bp(self):
        """
        Discount Margin basis points to override and that will be used as pricing
        analysis input. Available only for Floating Rate Notes. Optional.No override is
        applied by default. Note that only one pricing anlysis input should be defined.
        :return: float
        """
        return self._get_parameter("discountMarginBp")

    @discount_margin_bp.setter
    def discount_margin_bp(self, value):
        self._set_parameter("discountMarginBp", value)

    @property
    def discount_percent(self):
        """
        Discount (expressed in percent) to override and that will be used as pricing
        analysis input. Should be used only for bond quoted in discount. Optional. No
        override is applied by default. Note that only one pricing anlysis input should
        be defined.
        :return: float
        """
        return self._get_parameter("discountPercent")

    @discount_percent.setter
    def discount_percent(self, value):
        self._set_parameter("discountPercent", value)

    @property
    def dividend_yield_percent(self):
        """
        Underlying Stock dividend yield percent. Applicable for Convertible Bonds.
        :return: float
        """
        return self._get_parameter("dividendYieldPercent")

    @dividend_yield_percent.setter
    def dividend_yield_percent(self, value):
        self._set_parameter("dividendYieldPercent", value)

    @property
    def edsf_benchmark_curve_yield_percent(self):
        """
        Yield of Euro-Dollar future benchmark curve (Edsf) to override and that will be
        used to compute Euro-Dollar (Edsf) spread. Optional. No override is applied by
        default and yield is computed or retrieved from market data.
        :return: float
        """
        return self._get_parameter("edsfBenchmarkCurveYieldPercent")

    @edsf_benchmark_curve_yield_percent.setter
    def edsf_benchmark_curve_yield_percent(self, value):
        self._set_parameter("edsfBenchmarkCurveYieldPercent", value)

    @property
    def edsf_spread_bp(self):
        """
        Spread of Euro-Dollar future benchmark curve (Edsf) to override and that will be
        used as pricing analysis input to compute the bond price. This spread is
        computed for USD Bond whose maturity is under 2 Years. Optional. No override is
        applied by default. Note that only one pricing anlysis input should be defined.
        :return: float
        """
        return self._get_parameter("edsfSpreadBp")

    @edsf_spread_bp.setter
    def edsf_spread_bp(self, value):
        self._set_parameter("edsfSpreadBp", value)

    @property
    def efp_benchmark_price(self):
        """
        Price of EFP benchmark to override and that will be used to compute benchmark at
        redemption spread in case the bond is an australian FRN. Optional. No override
        is applied by default and price is computed or retrieved from market data.
        :return: float
        """
        return self._get_parameter("efpBenchmarkPrice")

    @efp_benchmark_price.setter
    def efp_benchmark_price(self, value):
        self._set_parameter("efpBenchmarkPrice", value)

    @property
    def efp_benchmark_ric(self):
        """
        RIC of EFP benchmark to override and that will be used as pricing analysis input
        to compute the bond price in case the bond is an australian FRN. Ric can be
        only "YTTc1" or "YTCc1". Optional. Default value is "YTTc1".
        :return: str
        """
        return self._get_parameter("efpBenchmarkRic")

    @efp_benchmark_ric.setter
    def efp_benchmark_ric(self, value):
        self._set_parameter("efpBenchmarkRic", value)

    @property
    def efp_benchmark_yield_percent(self):
        """
        Yield of EFP benchmark to override and that will be used to compute benchmark at
        redemption spread in case the bond is an australian FRN. Optional. No override
        is applied by default and yield is computed or retrieved from market data.
        :return: float
        """
        return self._get_parameter("efpBenchmarkYieldPercent")

    @efp_benchmark_yield_percent.setter
    def efp_benchmark_yield_percent(self, value):
        self._set_parameter("efpBenchmarkYieldPercent", value)

    @property
    def efp_spread_bp(self):
        """
        Spread of EFP benchmark to override and that will be used as pricing analysis
        input to compute the bond price in case the bond is an australian FRN. Optional.
        No override is applied by default. Note that only one pricing analysis input
        should be defined.
        :return: float
        """
        return self._get_parameter("efpSpreadBp")

    @efp_spread_bp.setter
    def efp_spread_bp(self, value):
        self._set_parameter("efpSpreadBp", value)

    @property
    def flat_credit_spread_bp(self):
        """
        Flat credit spread applied during pricing in basis points. Applicable when
        SpreadType = FlatSpread. Applicable for Convertible Bonds.
        :return: float
        """
        return self._get_parameter("flatCreditSpreadBp")

    @flat_credit_spread_bp.setter
    def flat_credit_spread_bp(self, value):
        self._set_parameter("flatCreditSpreadBp", value)

    @property
    def flat_credit_spread_tenor(self):
        """
        Flat credit spread tenor on credit curve used during pricing to source credit
        spread value. Applicable for Convertible Bonds.
        :return: str
        """
        return self._get_parameter("flatCreditSpreadTenor")

    @flat_credit_spread_tenor.setter
    def flat_credit_spread_tenor(self, value):
        self._set_parameter("flatCreditSpreadTenor", value)

    @property
    def fx_stock_correlation(self):
        """
        Correlation rate between underlying stock price and FX rate. Applicable for
        cross-currency Convertible Bonds.
        :return: float
        """
        return self._get_parameter("fxStockCorrelation")

    @fx_stock_correlation.setter
    def fx_stock_correlation(self, value):
        self._set_parameter("fxStockCorrelation", value)

    @property
    def fx_volatility_percent(self):
        """
        FX volatility rate percent. Applicable for cross-currency Convertible Bonds.
        :return: float
        """
        return self._get_parameter("fxVolatilityPercent")

    @fx_volatility_percent.setter
    def fx_volatility_percent(self, value):
        self._set_parameter("fxVolatilityPercent", value)

    @property
    def fx_volatility_tenor(self):
        """
        Tenor on FX volatility to source FX volatility Rate Percent. Applicable for
        cross-currency Convertible Bonds.
        :return: str
        """
        return self._get_parameter("fxVolatilityTenor")

    @fx_volatility_tenor.setter
    def fx_volatility_tenor(self, value):
        self._set_parameter("fxVolatilityTenor", value)

    @property
    def gov_country_benchmark_curve_price(self):
        """
        Price of government country benchmark to override and that will be used to
        compute user defined spread. Optional. No override is applied by default and
        price is computed or retrieved from market data.
        :return: float
        """
        return self._get_parameter("govCountryBenchmarkCurvePrice")

    @gov_country_benchmark_curve_price.setter
    def gov_country_benchmark_curve_price(self, value):
        self._set_parameter("govCountryBenchmarkCurvePrice", value)

    @property
    def gov_country_benchmark_curve_yield_percent(self):
        """
        Yield of government country benchmark to override and that will be used to
        compute government country spread. Optional. No override is applied by default
        and yield is computed or retrieved from market data.
        :return: float
        """
        return self._get_parameter("govCountryBenchmarkCurveYieldPercent")

    @gov_country_benchmark_curve_yield_percent.setter
    def gov_country_benchmark_curve_yield_percent(self, value):
        self._set_parameter("govCountryBenchmarkCurveYieldPercent", value)

    @property
    def gov_country_spread_bp(self):
        """
        Spread of government country benchmark to override and that will be used as
        pricing analysis input to compute the bond price. Optional. No override is
        applied by default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("govCountrySpreadBp")

    @gov_country_spread_bp.setter
    def gov_country_spread_bp(self, value):
        self._set_parameter("govCountrySpreadBp", value)

    @property
    def government_benchmark_curve_price(self):
        """
        price of government benchmark to override and that will be used to compute user
        defined spread. Optional. No override is applied by default and price is
        computed or retrieved from market data.
        :return: float
        """
        return self._get_parameter("governmentBenchmarkCurvePrice")

    @government_benchmark_curve_price.setter
    def government_benchmark_curve_price(self, value):
        self._set_parameter("governmentBenchmarkCurvePrice", value)

    @property
    def government_benchmark_curve_yield_percent(self):
        """
        Yield of government benchmark to override and that will be used to compute
        government spread. Optional. No override is applied by default and yield is
        computed or retrieved from market data.
        :return: float
        """
        return self._get_parameter("governmentBenchmarkCurveYieldPercent")

    @government_benchmark_curve_yield_percent.setter
    def government_benchmark_curve_yield_percent(self, value):
        self._set_parameter("governmentBenchmarkCurveYieldPercent", value)

    @property
    def government_spread_bp(self):
        """
        Spread of government benchmark to override and that will be used as pricing
        analysis input to compute the bond price. Optional. No override is applied by
        default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("governmentSpreadBp")

    @government_spread_bp.setter
    def government_spread_bp(self, value):
        self._set_parameter("governmentSpreadBp", value)

    @property
    def issuer_benchmark_curve_yield_percent(self):
        """
        Yield of issuer benchmark to override and that will be used to compute issuer
        spread. Optional. No override is applied by default and yield is computed or
        retrieved from market data.
        :return: float
        """
        return self._get_parameter("issuerBenchmarkCurveYieldPercent")

    @issuer_benchmark_curve_yield_percent.setter
    def issuer_benchmark_curve_yield_percent(self, value):
        self._set_parameter("issuerBenchmarkCurveYieldPercent", value)

    @property
    def issuer_spread_bp(self):
        """
        Spread of issuer benchmark to override and that will be used as pricing analysis
        input to compute the bond price. This spread is computed is for coprorate bonds.
        Optional. No override is applied by default. Note that only one pricing anlysis
        input should be defined.
        :return: float
        """
        return self._get_parameter("issuerSpreadBp")

    @issuer_spread_bp.setter
    def issuer_spread_bp(self, value):
        self._set_parameter("issuerSpreadBp", value)

    @property
    def market_data_date(self):
        """
        The market data date for pricing. Optional. By default, the market_data_date
        date is the valuation_date or Today
        :return: str
        """
        return self._get_parameter("marketDataDate")

    @market_data_date.setter
    def market_data_date(self, value):
        self._set_parameter("marketDataDate", value)

    @property
    def market_value_in_deal_ccy(self):
        """
        Market value in deal currency. This field can be used to compute notionalAmount
        to apply to get this market value. Optional. By default the value is computed
        from notional amount. NotionalAmount field, market_value_in_deal_ccy field and
        market_value_in_report_ccy field cannot be set at defined at the same time.
        :return: float
        """
        return self._get_parameter("marketValueInDealCcy")

    @market_value_in_deal_ccy.setter
    def market_value_in_deal_ccy(self, value):
        self._set_parameter("marketValueInDealCcy", value)

    @property
    def market_value_in_report_ccy(self):
        """
        Market value in report currency. This field can be used to compute
        notionalAmount to apply to get this market value. Optional. By default the value
        is computed from notional amount. NotionalAmount field, market_value_in_deal_ccy
        field and market_value_in_report_ccy field cannot be set at defined at the same
        time.
        :return: float
        """
        return self._get_parameter("marketValueInReportCcy")

    @market_value_in_report_ccy.setter
    def market_value_in_report_ccy(self, value):
        self._set_parameter("marketValueInReportCcy", value)

    @property
    def net_price(self):
        """
        Net price to override and that will be used as pricing analysis input. Optional.
        No override is applied by default. Note that only one pricing anlysis input
        should be defined.
        :return: float
        """
        return self._get_parameter("netPrice")

    @net_price.setter
    def net_price(self, value):
        self._set_parameter("netPrice", value)

    @property
    def neutral_yield_percent(self):
        """
        Neutral Yield (expressed in percent) to override and that will be used as
        pricing analysis input. This is available only for floating rate notes.
        Optional. No override is applied by default. Note that only one pricing analysis
        input should be defined.
        :return: float
        """
        return self._get_parameter("neutralYieldPercent")

    @neutral_yield_percent.setter
    def neutral_yield_percent(self, value):
        self._set_parameter("neutralYieldPercent", value)

    @property
    def ois_zc_benchmark_curve_yield_percent(self):
        """
        Yield of OIS benchmark to override and that will be used to compute OIS spread.
        Optional. No override is applied by default and yield is computed or retrieved
        from market data.
        :return: float
        """
        return self._get_parameter("oisZcBenchmarkCurveYieldPercent")

    @ois_zc_benchmark_curve_yield_percent.setter
    def ois_zc_benchmark_curve_yield_percent(self, value):
        self._set_parameter("oisZcBenchmarkCurveYieldPercent", value)

    @property
    def ois_zc_spread_bp(self):
        """
        Yield of OIS benchmark to override and that will be used as pricing analysis
        input to compute the bond price. Optional. No override is applied by default.
        Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("oisZcSpreadBp")

    @ois_zc_spread_bp.setter
    def ois_zc_spread_bp(self, value):
        self._set_parameter("oisZcSpreadBp", value)

    @property
    def option_adjusted_spread_bp(self):
        """
        Option Adjusted Spread to override and that will be used as pricing analysis
        input to compute the bond price. Optional. No override is applied by default.
        Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("optionAdjustedSpreadBp")

    @option_adjusted_spread_bp.setter
    def option_adjusted_spread_bp(self, value):
        self._set_parameter("optionAdjustedSpreadBp", value)

    @property
    def price(self):
        """
        Price to override and that will be used as pricing analysis input. This price
        can be the clean price or dirty price depending on price type defined in bond
        structure. The currency of the price is the cash flow currency (that can be
        different to deal currency especially if "ComputeCashFlowWithReportCcy" flag has
        been set to true). Optional. No override is applied by default. Note that only
        one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("price")

    @price.setter
    def price(self, value):
        self._set_parameter("price", value)

    @property
    def quoted_price(self):
        """
        Quoted price to override and that will be used as pricing analysis input. Note
        that a quoted price can be a price, a yield, a discount margin, a spread,...
        depending on quotation type. The currency of the quoted price in case the bonnd
        is price-quoted or cash-quoted is the deal currency (that can be different to
        cash flow currency especially if "ComputeCashFlowWithReportCcy" flag has been
        set to true). Optional. No override is applied by default. Note that only one
        pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("quotedPrice")

    @quoted_price.setter
    def quoted_price(self, value):
        self._set_parameter("quotedPrice", value)

    @property
    def rating_benchmark_curve_yield_percent(self):
        """
        Yield of rating benchmark to override and that will be used to compute rating
        spread. Optional. No override is applied by default and yield is computed or
        retrieved from market data.
        :return: float
        """
        return self._get_parameter("ratingBenchmarkCurveYieldPercent")

    @rating_benchmark_curve_yield_percent.setter
    def rating_benchmark_curve_yield_percent(self, value):
        self._set_parameter("ratingBenchmarkCurveYieldPercent", value)

    @property
    def rating_spread_bp(self):
        """
        Spread of rating benchmark to override and that will be used as pricing analysis
        input to compute the bond price. Optional. No override is applied by default.
        Note that only one pricing anlysis input should be defined.
        :return: float
        """
        return self._get_parameter("ratingSpreadBp")

    @rating_spread_bp.setter
    def rating_spread_bp(self, value):
        self._set_parameter("ratingSpreadBp", value)

    @property
    def redemption_date(self):
        """
        Redemption date that defines the end date for yield and price computation. Used
        only if redemption date type is set to "RedemptionAtCustomDate"
        :return: str
        """
        return self._get_parameter("redemptionDate")

    @redemption_date.setter
    def redemption_date(self, value):
        self._set_parameter("redemptionDate", value)

    @property
    def sector_rating_benchmark_curve_yield_percent(self):
        """
        Yield of sector rating benchmark to override and that will be used to compute
        sector rating spread. Optional. No override is applied by default and yield is
        computed or retrieved from market data.
        :return: float
        """
        return self._get_parameter("sectorRatingBenchmarkCurveYieldPercent")

    @sector_rating_benchmark_curve_yield_percent.setter
    def sector_rating_benchmark_curve_yield_percent(self, value):
        self._set_parameter("sectorRatingBenchmarkCurveYieldPercent", value)

    @property
    def sector_rating_spread_bp(self):
        """
        Spread of sector rating benchmark to override and that will be used as pricing
        analysis input to compute the bond price. Optional. No override is applied by
        default. Note that only one pricing anlysis input should be defined.
        :return: float
        """
        return self._get_parameter("sectorRatingSpreadBp")

    @sector_rating_spread_bp.setter
    def sector_rating_spread_bp(self, value):
        self._set_parameter("sectorRatingSpreadBp", value)

    @property
    def settlement_convention(self):
        """
        Settlement convention for the bond. By default the rule is that valuation_date =
        trade_date + settlement_convention. Optional. By default use the settlement
        tenor defined in the bond structure. Only two parameters among
        "settlement_convention", "market_data_date" and "valuation_date" can be
        overriden at the same time.
        :return: str
        """
        return self._get_parameter("settlementConvention")

    @settlement_convention.setter
    def settlement_convention(self, value):
        self._set_parameter("settlementConvention", value)

    @property
    def simple_margin_bp(self):
        """
        Simple Margin basis points  to override and that will be used as pricing
        analysis input. Available only for Floating Rate Notes. Optional.No override is
        applied by default. Note that only one pricing anlysis input should be defined.
        :return: float
        """
        return self._get_parameter("simpleMarginBp")

    @simple_margin_bp.setter
    def simple_margin_bp(self, value):
        self._set_parameter("simpleMarginBp", value)

    @property
    def stock_borrow_rate_percent(self):
        """
        Underlying stock borrow rate percent. Applicable for Convertible Bonds.
        :return: float
        """
        return self._get_parameter("stockBorrowRatePercent")

    @stock_borrow_rate_percent.setter
    def stock_borrow_rate_percent(self, value):
        self._set_parameter("stockBorrowRatePercent", value)

    @property
    def stock_flat_volatility_percent(self):
        """
        Underlying stock volatility percent used for convertible pricing. Applicable
        when volatility_type = Flat Applicable for Convertible Bonds.
        :return: float
        """
        return self._get_parameter("stockFlatVolatilityPercent")

    @stock_flat_volatility_percent.setter
    def stock_flat_volatility_percent(self, value):
        self._set_parameter("stockFlatVolatilityPercent", value)

    @property
    def stock_flat_volatility_tenor(self):
        """
        Underlying Stock volatility tenor used during pricing to source volatility
        percent value. Applicable when volatility_type = Flat Applicable for Convertible
        Bonds.
        :return: str
        """
        return self._get_parameter("stockFlatVolatilityTenor")

    @stock_flat_volatility_tenor.setter
    def stock_flat_volatility_tenor(self, value):
        self._set_parameter("stockFlatVolatilityTenor", value)

    @property
    def stock_price_on_default(self):
        """
        Assumed stock price agreed in event of default. Applicable for Convertible
        Bonds.
        :return: float
        """
        return self._get_parameter("stockPriceOnDefault")

    @stock_price_on_default.setter
    def stock_price_on_default(self, value):
        self._set_parameter("stockPriceOnDefault", value)

    @property
    def strip_yield_percent(self):
        """
        Strip Yield (expressed in percent) to override and that will be used as pricing
        analysis input. Optional. No override is applied by default. Note that only one
        pricing anlysis input should be defined.
        :return: float
        """
        return self._get_parameter("stripYieldPercent")

    @strip_yield_percent.setter
    def strip_yield_percent(self, value):
        self._set_parameter("stripYieldPercent", value)

    @property
    def swap_benchmark_curve_yield_percent(self):
        """
        Yield of swap benchmark to override and that will be used to compute swap
        spread. Optional. No override is applied by default and yield is computed or
        retrieved from market data.
        :return: float
        """
        return self._get_parameter("swapBenchmarkCurveYieldPercent")

    @swap_benchmark_curve_yield_percent.setter
    def swap_benchmark_curve_yield_percent(self, value):
        self._set_parameter("swapBenchmarkCurveYieldPercent", value)

    @property
    def swap_spread_bp(self):
        """
        Spread of swap benchmark to override and that will be used as pricing analysis
        input to compute the bond price. Optional. No override is applied by default.
        Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("swapSpreadBp")

    @swap_spread_bp.setter
    def swap_spread_bp(self, value):
        self._set_parameter("swapSpreadBp", value)

    @property
    def tax_on_capital_gain_percent(self):
        """
        Tax Rate on capital gain expressed in percent. Optional. By default no tax is
        applied that means value is equal to 0.
        :return: float
        """
        return self._get_parameter("taxOnCapitalGainPercent")

    @tax_on_capital_gain_percent.setter
    def tax_on_capital_gain_percent(self, value):
        self._set_parameter("taxOnCapitalGainPercent", value)

    @property
    def tax_on_coupon_percent(self):
        """
        Tax Rate on Coupon  expressed in percent. Optional. By default no tax is applied
        that means value is equal to 0.
        :return: float
        """
        return self._get_parameter("taxOnCouponPercent")

    @tax_on_coupon_percent.setter
    def tax_on_coupon_percent(self, value):
        self._set_parameter("taxOnCouponPercent", value)

    @property
    def tax_on_price_percent(self):
        """
        Tax Rate on price  expressed in percent. Optional. By default no tax is applied
        that means value is equal to 0.
        :return: float
        """
        return self._get_parameter("taxOnPricePercent")

    @tax_on_price_percent.setter
    def tax_on_price_percent(self, value):
        self._set_parameter("taxOnPricePercent", value)

    @property
    def tax_on_yield_percent(self):
        """
        Tax Rate on Yield expressed in percent. Also named Tax on Yield Optional. By
        default no tax is applied that means value is equal to 0.
        :return: float
        """
        return self._get_parameter("taxOnYieldPercent")

    @tax_on_yield_percent.setter
    def tax_on_yield_percent(self, value):
        self._set_parameter("taxOnYieldPercent", value)

    @property
    def trade_date(self):
        """
        Trade date of the bond. The trade_date is used to compute the default
        valuation_date : By default the rule is that valuation_date = trade_date +
        settlement_convention. Optional. By default, it is equal to market_data_date.
        :return: str
        """
        return self._get_parameter("tradeDate")

    @trade_date.setter
    def trade_date(self, value):
        self._set_parameter("tradeDate", value)

    @property
    def use_settlement_date_from_quote(self):
        """
        Specify whether to use the settlment date of the quote or the one computed from
        the MarketData Date
        :return: bool
        """
        return self._get_parameter("useSettlementDateFromQuote")

    @use_settlement_date_from_quote.setter
    def use_settlement_date_from_quote(self, value):
        self._set_parameter("useSettlementDateFromQuote", value)

    @property
    def user_defined_benchmark_price(self):
        """
        Price of user defined instrument to override and that will be used to compute
        user defined spread. Optional. No override is applied by default and price is
        computed or retrieved from market data.
        :return: float
        """
        return self._get_parameter("userDefinedBenchmarkPrice")

    @user_defined_benchmark_price.setter
    def user_defined_benchmark_price(self, value):
        self._set_parameter("userDefinedBenchmarkPrice", value)

    @property
    def user_defined_benchmark_yield_percent(self):
        """
        Yield of user defined instrument to override and that will be used to compute
        user defined spread. Optional. No override is applied by default and yield is
        computed or retrieved from market data.
        :return: float
        """
        return self._get_parameter("userDefinedBenchmarkYieldPercent")

    @user_defined_benchmark_yield_percent.setter
    def user_defined_benchmark_yield_percent(self, value):
        self._set_parameter("userDefinedBenchmarkYieldPercent", value)

    @property
    def user_defined_spread_bp(self):
        """
        Spread of user defined instrument to override and that will be used as pricing
        analysis input to compute the bond price. Optional. No override is applied by
        default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("userDefinedSpreadBp")

    @user_defined_spread_bp.setter
    def user_defined_spread_bp(self, value):
        self._set_parameter("userDefinedSpreadBp", value)

    @property
    def valuation_date(self):
        """
        The valuation date for pricing.  Optional. If not set the valuation date is
        equal to market_data_date or Today. For assets that contains a
        settlement_convention, the default valuation date  is equal to the
        settlementdate of the Asset that is usually the
        trade_date+settlement_convention.
        :return: str
        """
        return self._get_parameter("valuationDate")

    @valuation_date.setter
    def valuation_date(self, value):
        self._set_parameter("valuationDate", value)

    @property
    def yield_percent(self):
        """
        Yield (expressed in percent) to override and that will be used as pricing
        analysis input. Optional. No override is applied by default. Note that only one
        pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("yieldPercent")

    @yield_percent.setter
    def yield_percent(self, value):
        self._set_parameter("yieldPercent", value)

    @property
    def z_spread_bp(self):
        """
        ZSpread to override and that will be used as pricing analysis input to compute
        the bond price. Optional. No override is applied by default. Note that only one
        pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("zSpreadBp")

    @z_spread_bp.setter
    def z_spread_bp(self, value):
        self._set_parameter("zSpreadBp", value)

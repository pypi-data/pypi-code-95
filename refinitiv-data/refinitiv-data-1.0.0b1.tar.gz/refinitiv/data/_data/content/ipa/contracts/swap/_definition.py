# coding: utf8

__all__ = ["Definition"]

from .._base_definition import BaseDefinition
from ._swap_definition import SwapInstrumentDefinition


class Definition(BaseDefinition):
    def __init__(
        self,
        instrument_code=None,
        instrument_tag=None,
        trade_date=None,
        start_date=None,
        end_date=None,
        tenor=None,
        settlement_ccy=None,
        is_non_deliverable=None,
        template=None,
        legs=None,
        fields=None,
        pricing_parameters=None,
        outputs=None,
        extended_params=None,
    ):
        definition = SwapInstrumentDefinition(
            instrument_tag=instrument_tag,
            trade_date=trade_date,
            start_date=start_date,
            end_date=end_date,
            tenor=tenor,
            settlement_ccy=settlement_ccy,
            is_non_deliverable=is_non_deliverable,
            instrument_code=instrument_code,
            template=template,
            legs=legs,
        )
        super().__init__(
            definition=definition,
            fields=fields,
            pricing_parameters=pricing_parameters,
            outputs=outputs,
            extended_params=extended_params,
        )

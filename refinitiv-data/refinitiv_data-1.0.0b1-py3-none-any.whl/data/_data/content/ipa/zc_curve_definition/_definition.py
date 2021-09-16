__all__ = ["Definition"]

from .._curves._interest_rate_curve_get_definition import InterestRateCurveGetDefinition
from ..._content_provider import ContentProviderLayer
from ..._content_type import ContentType


class Definition(ContentProviderLayer):
    def __init__(
        self,
        index_name=None,
        main_constituent_asset_class=None,
        risk_type=None,
        currency=None,
        curve_tag=None,
        id=None,
        name=None,
        source=None,
        valuation_date=None,
        extended_params=None,
    ) -> None:
        request_item = InterestRateCurveGetDefinition(
            index_name=index_name,
            main_constituent_asset_class=main_constituent_asset_class,
            risk_type=risk_type,
            currency=currency,
            curve_tag=curve_tag,
            id=id,
            name=name,
            source=source,
            valuation_date=valuation_date,
        )
        super().__init__(
            content_type=ContentType.ZC_CURVE_DEFINITIONS,
            universe=request_item,
            extended_params=extended_params,
        )

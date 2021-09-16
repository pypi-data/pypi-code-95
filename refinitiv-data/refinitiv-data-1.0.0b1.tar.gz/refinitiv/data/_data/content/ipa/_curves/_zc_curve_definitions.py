# coding: utf8

__all__ = ["ZcCurveDefinitions"]

from typing import Optional
from .._object_definition import ObjectDefinition
from ....tools import create_str_definition


from ._enums import RiskType, AssetClass
from ._zc_curve_definition import ZcCurveDefinition
from ..._types import OptStr, Strings


class ZcCurveDefinitions(ObjectDefinition):
    """
    Parameters
    ----------
    index_name : str, optional

    index_tenors : string, optional
        Defines expected rate surface tenor/slices Defaults to the tenors available,
        based on provided market data
    main_constituent_asset_class : AssetClass, optional

    pivot_curve_definition : ZcCurveDefinition, optional

    reference_curve_definition : ZcCurveDefinition, optional

    risk_type : RiskType, optional

    currency : str, optional
        The currency code of the interest rate curve
    discounting_tenor : str, optional
        Mono currency discounting tenor
    id : str, optional
        Id of the curve definition
    name : str, optional
        The name of the interest rate curve
    source : str, optional

    """

    def __init__(
        self,
        index_name: OptStr = None,
        index_tenors: Strings = None,
        main_constituent_asset_class: Optional[AssetClass] = None,
        pivot_curve_definition: Optional[ZcCurveDefinition] = None,
        reference_curve_definition: Optional[ZcCurveDefinition] = None,
        risk_type: Optional[RiskType] = None,
        currency: OptStr = None,
        discounting_tenor: OptStr = None,
        id: OptStr = None,
        name: OptStr = None,
        source: OptStr = None,
    ) -> None:
        super().__init__()
        self.index_name = index_name
        self.index_tenors = index_tenors
        self.main_constituent_asset_class = main_constituent_asset_class
        self.pivot_curve_definition = pivot_curve_definition
        self.reference_curve_definition = reference_curve_definition
        self.risk_type = risk_type
        self.currency = currency
        self.discounting_tenor = discounting_tenor
        self.id = id
        self.name = name
        self.source = source

    def __repr__(self):
        return create_str_definition(
            self,
            middle_path="content.ipa.curves",
            end_path="zc_curve",
            name_class=self.__class__.__name__,
        )

    @property
    def index_tenors(self):
        """
        Defines expected rate surface tenor/slices Defaults to the tenors available,
        based on provided market data
        :return: list string
        """
        return self._get_list_parameter(str, "indexTenors")

    @index_tenors.setter
    def index_tenors(self, value):
        self._set_list_parameter(str, "indexTenors", value)

    @property
    def main_constituent_asset_class(self):
        """
        :return: enum AssetClass
        """
        return self._get_enum_parameter(AssetClass, "mainConstituentAssetClass")

    @main_constituent_asset_class.setter
    def main_constituent_asset_class(self, value):
        self._set_enum_parameter(AssetClass, "mainConstituentAssetClass", value)

    @property
    def pivot_curve_definition(self):
        """
        :return: object ZcCurveDefinition
        """
        return self._get_object_parameter(ZcCurveDefinition, "pivotCurveDefinition")

    @pivot_curve_definition.setter
    def pivot_curve_definition(self, value):
        self._set_object_parameter(ZcCurveDefinition, "pivotCurveDefinition", value)

    @property
    def reference_curve_definition(self):
        """
        :return: object ZcCurveDefinition
        """
        return self._get_object_parameter(ZcCurveDefinition, "referenceCurveDefinition")

    @reference_curve_definition.setter
    def reference_curve_definition(self, value):
        self._set_object_parameter(ZcCurveDefinition, "referenceCurveDefinition", value)

    @property
    def risk_type(self):
        """
        :return: enum RiskType
        """
        return self._get_enum_parameter(RiskType, "riskType")

    @risk_type.setter
    def risk_type(self, value):
        self._set_enum_parameter(RiskType, "riskType", value)

    @property
    def currency(self):
        """
        The currency code of the interest rate curve
        :return: str
        """
        return self._get_parameter("currency")

    @currency.setter
    def currency(self, value):
        self._set_parameter("currency", value)

    @property
    def discounting_tenor(self):
        """
        Mono currency discounting tenor
        :return: str
        """
        return self._get_parameter("discountingTenor")

    @discounting_tenor.setter
    def discounting_tenor(self, value):
        self._set_parameter("discountingTenor", value)

    @property
    def id(self):
        """
        Id of the curve definition
        :return: str
        """
        return self._get_parameter("id")

    @id.setter
    def id(self, value):
        self._set_parameter("id", value)

    @property
    def index_name(self):
        """
        :return: str
        """
        return self._get_parameter("indexName")

    @index_name.setter
    def index_name(self, value):
        self._set_parameter("indexName", value)

    @property
    def name(self):
        """
        The name of the interest rate curve
        :return: str
        """
        return self._get_parameter("name")

    @name.setter
    def name(self, value):
        self._set_parameter("name", value)

    @property
    def source(self):
        """
        :return: str
        """
        return self._get_parameter("source")

    @source.setter
    def source(self, value):
        self._set_parameter("source", value)

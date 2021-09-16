# coding: utf8

__all__ = ["SwapZcCurveDefinition"]

from typing import Optional

from .._object_definition import ObjectDefinition
from ._enums import AssetClass, RiskType
from ..._types import Strings, OptStr
from ....tools import create_str_definition


class SwapZcCurveDefinition(ObjectDefinition):
    """
    Parameters
    ----------
    index_name : str, optional

    index_tenors : string, optional
        Defines expected rate surface tenor/slices defaults to the tenors available,
        based on provided market data
    main_constituent_asset_class : MainConstituentAssetClass, optional

    risk_type : RiskType, optional

    currency : str, optional

    discounting_tenor : str, optional

    id : str, optional
        Id of the curve definition to get
    market_data_location : str, optional

    name : str, optional

    source : str, optional

    """

    def __init__(
        self,
        index_name: OptStr = None,
        index_tenors: Strings = None,
        main_constituent_asset_class: Optional[AssetClass] = None,
        risk_type: Optional[RiskType] = None,
        currency: OptStr = None,
        discounting_tenor: OptStr = None,
        id: OptStr = None,
        market_data_location: OptStr = None,
        name: OptStr = None,
        source: OptStr = None,
    ) -> None:
        super().__init__()
        self.index_name = index_name
        self.index_tenors = index_tenors
        self.main_constituent_asset_class = main_constituent_asset_class
        self.risk_type = risk_type
        self.currency = currency
        self.discounting_tenor = discounting_tenor
        self.id = id
        self.market_data_location = market_data_location
        self.name = name
        self.source = source

    def __repr__(self):
        return create_str_definition(
            self,
            middle_path="content.ipa.curves",
            end_path="forward_curve",
            name_class=self.__class__.__name__,
        )

    @property
    def index_tenors(self):
        """
        Defines expected rate surface tenor/slices defaults to the tenors available,
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
        :return: str
        """
        return self._get_parameter("currency")

    @currency.setter
    def currency(self, value):
        self._set_parameter("currency", value)

    @property
    def discounting_tenor(self):
        """
        :return: str
        """
        return self._get_parameter("discountingTenor")

    @discounting_tenor.setter
    def discounting_tenor(self, value):
        self._set_parameter("discountingTenor", value)

    @property
    def id(self):
        """
        Id of the curve definition to get
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
    def market_data_location(self):
        """
        :return: str
        """
        return self._get_parameter("marketDataLocation")

    @market_data_location.setter
    def market_data_location(self, value):
        self._set_parameter("marketDataLocation", value)

    @property
    def name(self):
        """
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

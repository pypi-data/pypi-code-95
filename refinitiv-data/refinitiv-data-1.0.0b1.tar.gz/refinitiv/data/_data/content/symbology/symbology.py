# coding: utf8

__all__ = ["Symbology"]

from typing import Union, Iterable

from .symbol_type import SymbolTypes, SYMBOL_TYPE_VALUES
from .symbol_conversion.asset_state import AssetState
from .symbol_conversion.asset_class import AssetClass
from .symbol_conversion.country_code import CountryCode
from ..search.lookup import Lookup
from ..search import SearchViews


search_all_category_by_asset_class = {
    AssetClass.COMMODITIES: "Commodities",
    AssetClass.EQUITY_OR_INDEX_OPTIONS: "Options",
    AssetClass.BOND_AND_STIR_FUTURES_AND_OPTIONS: "Exchange-Traded Rates",
    AssetClass.EQUITIES: "Equities",
    AssetClass.EQUITY_INDEX_FUTURES: "Futures",
    AssetClass.FUNDS: "Funds",
    AssetClass.BONDS: "Bond Pricing",
    AssetClass.FX_AND_MONEY: "FX & Money",
}

rcsasset_category_genealogy_by_asset_class = {
    AssetClass.WARRANTS: "A:AA",
    AssetClass.CERTIFICATES: "A:6N",
    AssetClass.INDICES: "I:17",
    AssetClass.RESERVE_CONVERTIBLE: "A:LE",
    AssetClass.MINI_FUTURE: "A:P6",
}


class Symbology(object):
    SymbolTypes = SymbolTypes

    def __init__(self, session=None, on_response=None):
        from ...core.session import get_default

        if session is None:
            session = get_default()

        if session is None:
            raise AttributeError("A Session must be started")

        self._on_response_cb = on_response
        self._data = None
        self._lookup = Lookup(session=session, onResponseCallbackFunc=self._on_response)

    @property
    def data(self):
        return self._data

    @property
    def status(self):
        if self._data:
            return self._data.status
        return {}

    def _on_response(self, endpoint, data):
        self._data = data
        if self._on_response_cb:
            self._on_response_cb(self, data)

    @staticmethod
    def convert(
        symbols,
        from_symbol_type=None,
        to_symbol_types=None,
        on_response=None,
        closure=None,
    ):
        symbology = Symbology(on_response=on_response)
        response = symbology._convert(
            symbols=symbols,
            from_symbol_type=from_symbol_type,
            to_symbol_types=to_symbol_types,
            closure=closure,
        )
        return response

    @staticmethod
    async def convert_async(
        symbols,
        from_symbol_type=None,
        to_symbol_types=None,
        on_response=None,
        closure=None,
    ):
        symbology = Symbology(on_response=on_response)
        response = await symbology._convert_async(
            symbols=symbols,
            from_symbol_type=from_symbol_type,
            to_symbol_types=to_symbol_types,
            closure=closure,
        )
        return response

    def _convert(
        self,
        symbols,
        from_symbol_type=None,
        to_symbol_types=None,
        closure=None,
        extended_params=None,
        preferred_country_code=None,
        asset_class=None,
        asset_state=None,
    ):
        return self._lookup._endpoint.session._loop.run_until_complete(
            self._convert_async(
                symbols=symbols,
                from_symbol_type=from_symbol_type,
                to_symbol_types=to_symbol_types,
                closure=closure,
                extended_params=extended_params,
                preferred_country_code=preferred_country_code,
                asset_class=asset_class,
                asset_state=asset_state,
            )
        )

    async def _convert_async(
        self,
        symbols,
        from_symbol_type=None,
        to_symbol_types=None,
        closure=None,
        extended_params=None,
        preferred_country_code=None,
        asset_class=None,
        asset_state=None,
    ):
        return await self.__convert(
            symbols=symbols,
            from_symbol_type=from_symbol_type,
            to_symbol_types=to_symbol_types,
            closure=closure,
            extended_params=extended_params,
            preferred_country_code=preferred_country_code,
            asset_class=asset_class,
            asset_state=asset_state,
        )

    def _transform_to_string(self, values: Iterable, category: dict) -> str:
        string_of_values = ""
        for value in values:
            request_value = category[value]
            string_of_values = f"{string_of_values} '{request_value}'"
        return string_of_values

    def _create_asset_class_request_strings(self, asset_class: list) -> tuple:
        search_all_category_values = filter(
            lambda x: x in search_all_category_by_asset_class, asset_class
        )
        rcs_asset_category_values = filter(
            lambda x: x in rcsasset_category_genealogy_by_asset_class, asset_class
        )

        search_all_category_string_values = self._transform_to_string(
            search_all_category_values, search_all_category_by_asset_class
        )

        search_all_rcs_asset_category_string_values = self._transform_to_string(
            rcs_asset_category_values, rcsasset_category_genealogy_by_asset_class
        )

        search_all_category_string = ""
        rcs_asset_category_string = ""

        if search_all_category_string_values:
            search_all_category_string = (
                f"SearchAllCategoryv3 in ({search_all_category_string_values})"
            )

        if search_all_rcs_asset_category_string_values:
            rcs_asset_category_string = f"RCSAssetCategoryGenealogy in ({search_all_rcs_asset_category_string_values})"

        return search_all_category_string, rcs_asset_category_string

    def _prepare_filter(
        self, asset_state: AssetState, asset_class: Union[list, AssetClass]
    ) -> str:
        asset_state = asset_state or AssetState.ACTIVE

        if asset_state is AssetState.ACTIVE:
            ret_val = "AssetState eq 'AC'"
        else:
            ret_val = "(AssetState ne 'AC' and AssetState ne null)"

        if asset_class and not isinstance(asset_class, list):
            asset_class = [asset_class]

        if asset_class:
            (
                search_all_category,
                rcs_asset_category,
            ) = self._create_asset_class_request_strings(asset_class)

            if search_all_category and rcs_asset_category:
                ret_val = (
                    f"{ret_val} and ({search_all_category} or {rcs_asset_category})"
                )
            else:
                ret_val = f"{ret_val} and ({search_all_category}{rcs_asset_category})"

        return ret_val

    async def __convert(
        self,
        symbols,
        from_symbol_type=None,
        to_symbol_types=None,
        closure=None,
        extended_params=None,
        preferred_country_code=None,
        asset_class=None,
        asset_state=None,
    ):
        filter = self._prepare_filter(asset_state, asset_class)

        if preferred_country_code:
            preferred_country_code = f"RCSExchangeCountry eq '{CountryCode.convert_to_str(preferred_country_code)}'"

        if from_symbol_type is None:
            from_symbol_type = "_AllUnique"
        else:
            from_symbol_type = SymbolTypes.convert_to_str(from_symbol_type)

        select = ["DocumentTitle"]

        if to_symbol_types is None:
            select += SYMBOL_TYPE_VALUES
        elif isinstance(to_symbol_types, list):
            select = map(SymbolTypes.convert_to_str, to_symbol_types)
        elif isinstance(to_symbol_types, str):
            select.append(to_symbol_types)

        select = ",".join(select)

        if isinstance(symbols, list):
            symbols = ",".join(symbols)

        response = await self._lookup._lookup_async(
            view=SearchViews.SEARCH_ALL,
            terms=symbols,
            scope=from_symbol_type,
            select=select,
            closure=closure,
            extended_params=extended_params,
            filter=filter,
            boost=preferred_country_code,
        )

        return response

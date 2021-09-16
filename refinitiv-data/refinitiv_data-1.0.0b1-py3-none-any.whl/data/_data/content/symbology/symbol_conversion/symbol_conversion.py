from typing import Union, Optional, Callable

__all__ = ["Definition"]

from refinitiv.data._data.core.session import Session

from .asset_class import AssetClass
from .country_code import CountryCode
from .asset_state import AssetState
from ..symbol_type import SymbolTypes
from ....tools._repr_definition import create_str_definition


class Definition:
    """
    This class describe parameters to retrieve data for symbol conversion.

    Parameters
    ----------
    symbols: str ot list of str
        Single instrument or list of instruments to convert.

    from_symbol_type: SymbolTypes value, optional
        Instrument code to convert from.
        Possible values: 'CUSIP', 'ISIN', 'SEDOL', 'RIC', 'ticker', 'lipperID', 'IMO'
        Default: '_AllUnique'

    to_symbol_types: string or list, optional
        Instrument code to convert to.
        Possible values: 'CUSIP', 'ISIN', 'SEDOL', 'RIC', 'ticker', 'lipperID', 'IMO', 'OAPermID'
        Default: None  (means all symbol types are requested)

    closure: str, optional
        Specifies the parameter that will be merged with the request

    extended_params: dict, optional
        Other parameters can be provided if necessary

    preferred_country_code: CountryCode value, optional
        Unique ISO 3166 code for country

    asset_class: AssetClass value, optional
        AssetClass value to build filter parameter

    asset_state: AssetState value, optional
        AssetState value to build filter parameter.

    Examples
    --------
    >>> from refinitiv.data.content import symbol_conversion
    >>> definition = symbol_conversion.Definition(
    >>>     symbols=["US5949181045", "US02079K1079"],
    >>>     from_symbol_type=symbol_conversion.SymbolTypes.ISIN,
    >>>     to_symbol_types=[symbol_conversion.SymbolTypes.RIC, symbol_conversion.SymbolTypes.OA_PERM_ID],
    >>>     preferred_country_code=symbol_conversion.CountryCode.USA,
    >>>     asset_class=[
    >>>        symbol_conversion.AssetClass.COMMODITIES,
    >>>        symbol_conversion.AssetClass.EQUITIES,
    >>>        symbol_conversion.AssetClass.WARRANTS
    >>>     ],
    >>>     asset_state=symbol_conversion.AssetState.INACTIVE)
    """

    def __init__(
        self,
        symbols: Union[list, str],
        from_symbol_type: Optional[SymbolTypes] = None,
        to_symbol_types: Union[list, str] = None,
        closure: Optional[str] = None,
        extended_params: Optional[dict] = None,
        preferred_country_code: Optional[CountryCode] = None,
        asset_class: Union[list, AssetClass] = None,
        asset_state: Optional[AssetState] = None,
    ):
        self._symbols = symbols
        self._from_symbol_type = from_symbol_type
        self._to_symbol_types = to_symbol_types
        self._closure = closure
        self._extended_params = extended_params
        self.preferred_country_code = preferred_country_code
        self.asset_class = asset_class
        self.asset_state = asset_state

    def get_data(self, session: Session = None, on_response: Callable = None):
        """
        Returns a response from the API to the library

        Parameters
        ----------
        session : Session, optional
            The Session defines the source where you want to retrieve your data
        on_response : Callable, optional
            Callable object to process retrieved data

        Returns
        -------
        EndpointResponse

        Raises
        ------
        AttributeError
            If user didn't set default session.

        Examples
        --------
        >>> from refinitiv.data.content import symbol_conversion
        >>> definition = symbol_conversion.Definition(symbols=["US5949181045", "US02079K1079"])
        >>> definition.get_data()
        """
        from ..symbology import Symbology

        symbology = Symbology(session=session, on_response=on_response)
        response = symbology._convert(
            symbols=self._symbols,
            from_symbol_type=self._from_symbol_type,
            to_symbol_types=self._to_symbol_types,
            closure=self._closure,
            extended_params=self._extended_params,
            preferred_country_code=self.preferred_country_code,
            asset_class=self.asset_class,
            asset_state=self.asset_state,
        )

        return response

    async def get_data_async(
        self, session: Session = None, on_response: Callable = None
    ):
        """
        Returns a response asynchronously from the API to the library

        Parameters
        ----------
        session : Session, optional
            The Session defines the source where you want to retrieve your data
        on_response : Callable, optional
            Callable object to process retrieved data

        Returns
        -------
        EndpointResponse

        Raises
        ------
        AttributeError
            If user didn't set default session.

        Examples
        --------
        >>> from refinitiv.data.content import symbol_conversion
        >>> definition = symbol_conversion.Definition(symbols=["US5949181045", "US02079K1079"])
        >>> await definition.get_data_async()
        """
        from ..symbology import Symbology

        symbology = Symbology(session=session, on_response=on_response)
        response = await symbology._convert_async(
            symbols=self._symbols,
            from_symbol_type=self._from_symbol_type,
            to_symbol_types=self._to_symbol_types,
            closure=self._closure,
            extended_params=self._extended_params,
            preferred_country_code=self.preferred_country_code,
            asset_class=self.asset_class,
            asset_state=self.asset_state,
        )

        return response

    def __repr__(self):
        return create_str_definition(
            self,
            middle_path="content",
            content=f"{{symbols='{self._symbols}'}}",
        )

from typing import Iterable, Union

from .._content_provider import ContentProviderLayer
from .._content_type import ContentType
from ...tools._repr_definition import create_str_definition


class Definition(ContentProviderLayer):
    """
    This class describe parameters to retrieve ESG basic data.

    Parameters
    ----------
    universe : str, list of str
        The Universe parameter allows the user to define the company they
        want content returned for, ESG content is delivered at the Company Level.

    closure : str, optional
        Specifies the parameter that will be merged with the request

    Examples
    --------
    >>> from refinitiv.data.content import esg
    >>> definition = esg.basic_overview.Definition("IBM.N")
    >>> response = definition.get_data()

    >>> response = await definition.get_data_async()
    """

    def __init__(
        self,
        universe: Union[str, Iterable[str]],
        closure: str = None,
    ):
        super().__init__(
            content_type=ContentType.ESG_BASIC_OVERVIEW,
            universe=universe,
            closure=closure,
        )

    def __repr__(self):
        return create_str_definition(
            self,
            middle_path="content.esg",
            content=f"{{universe='{self._kwargs.get('universe')}'}}",
        )

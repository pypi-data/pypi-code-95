from .._content_provider import ContentProviderLayer
from .._content_type import ContentType
from ...tools._repr_definition import create_str_definition


class Definition(ContentProviderLayer):
    """
    This class describe parameters to retrieve data for ESG universe.

    Parameters
    ----------
    closure : str, optional
        Specifies the parameter that will be merged with the request

    Examples
    --------
    >>> from refinitiv.data.content import esg
    >>> definition = esg.universe.Definition()
    >>> response = definition.get_data()

    >>> response = await definition.get_data_async()
    """

    def __init__(
        self,
        closure: str = None,
    ):
        super().__init__(
            content_type=ContentType.ESG_UNIVERSE,
            closure=closure,
        )

    def __repr__(self):
        return create_str_definition(
            self,
            middle_path="content.esg",
            content=f"{{closure='{self._kwargs.get('closure')}'}}",
        )

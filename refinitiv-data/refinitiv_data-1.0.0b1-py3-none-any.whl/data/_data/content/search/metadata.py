from typing import Callable

from .ViewMetadata import ViewMetadata
from .SearchViews import SearchViews
from refinitiv.data._data.core.session import Session
from ...tools._repr_definition import create_str_definition


class Definition:
    """
    This class describe parameters to retrieve data for search metadata.

    Parameters
    ----------

    view : SearchViews
        picks a subset of the data universe to search against. see SearchViews

    Examples
    --------
    >>> from refinitiv.data.content import search
    >>> definition = search.metadata.Definition(view = search.SearchViews.PEOPLE)
    """

    def __init__(self, view: SearchViews):
        self._view = view

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
        ViewMetadata.ViewMetadataData

        Raises
        ------
        AttributeError
            If user didn't set default session.

        Examples
        --------
        >>> from refinitiv.data.content import search
        >>> definition = search.metadata.Definition(view = search.SearchViews.PEOPLE)
        >>> response = definition.get_data()
        """

        return ViewMetadata.get_metadata(
            session=session, on_response=on_response, view=self._view
        )

    async def get_data_async(
        self, session: Session = None, on_response: Callable = None
    ):
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
        ViewMetadata.ViewMetadataData

        Raises
        ------
        AttributeError
            If user didn't set default session.

        Examples
        --------
        >>> from refinitiv.data.content import search
        >>> definition = search.metadata.Definition(view = search.SearchViews.PEOPLE)
        >>> response = await definition.get_data_async()
        """

        response = await ViewMetadata.get_metadata_async(
            session=session, view=self._view, on_response=on_response
        )
        return response

    def __repr__(self):
        return create_str_definition(
            self,
            middle_path="content.search",
            content=f"{{view='{self._view}'}}",
        )

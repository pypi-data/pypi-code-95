from datetime import timedelta, datetime, date
from typing import Union, Tuple, Callable, Optional

from .news_headlines import NewsHeadlines
from .sort_order import SortOrder
from ...core.session import get_default
from ...tools._repr_definition import create_str_definition
from refinitiv.data._data.core.session import Session


__all__ = ["Definition"]


class Definition:
    """
    This class describes parameters to retrieve data for news headlines.

    Parameters
    ----------
    query: str
        The user search query.

    count: int, optional
        Count to limit number of headlines. Min value is 0. Default: 10

    date_from: str or timedelta, optional
        Beginning of date range.
        String format is: '%Y-%m-%dT%H:%M:%S'. e.g. '2016-01-20T15:04:05'.

    date_to: str or timedelta, optional
        End of date range.
        String format is: '%Y-%m-%dT%H:%M:%S'. e.g. '2016-01-20T15:04:05'.

    sort_order: SortOrder
        Value from SortOrder enum. Default: SortOrder.new_to_old

    extended_params: dict, optional
        Other parameters can be provided if necessary

    Examples
    --------
    >>> from refinitiv.data.content import news
    >>> definition = news.headlines.Definition("Refinitiv",
    >>>                                      date_from="20.03.2021",
    >>>                                      date_to=timedelta(days=-4),
    >>>                                      count=3)
    """

    def __init__(
        self,
        query: str,
        count: int = 10,
        date_from: Union[str, timedelta, Tuple[datetime, date]] = None,
        date_to: Union[str, timedelta, Tuple[datetime, date]] = None,
        sort_order: SortOrder = SortOrder.new_to_old,
        extended_params: dict = None,
    ):
        self.query = query
        self.count = count
        self.date_from = date_from
        self.date_to = date_to
        self.sort_order = sort_order
        self.extended_params = extended_params

    def get_data(
        self,
        session: Session = None,
        on_response: Optional[Callable] = None,
        on_page_response: Optional[Callable] = None,
        closure: Optional[str] = None,
    ):
        """
        Returns a response from the API to the library

        Parameters
        ----------
        session : Session, optional
            The Session defines the source where you want to retrieve your data
        on_response : Callable, optional
            Callable object to process retrieved data
        on_page_response : Callable, optional
            Callable object to process retrieved data
        closure : str, optional
            Specifies the parameter that will be merged with the request

        Returns
        -------
        NewsHeadlines.NewsHeadlinesResponse

        Raises
        ------
        AttributeError
            If user didn't set default session.

        Examples
        --------
        >>> from refinitiv.data.content import news
        >>> definition = news.headlines.Definition("Refinitiv",
        >>>                                        date_from="20.03.2021",
        >>>                                        date_to=timedelta(days=-4),
        >>>                                        count=3)
        >>> response = definition.get_data()
        """
        if session is None:
            session = get_default()

        if session is None:
            raise AttributeError("Session must be defined")

        news_headlines = NewsHeadlines(session=session, on_response=on_response)
        response = news_headlines.get_headlines(
            query=self.query,
            count=self.count,
            date_from=self.date_from,
            date_to=self.date_to,
            sort_order=self.sort_order,
            on_page_response=on_page_response,
            closure=closure,
            extended_params=self.extended_params,
        )
        return response

    async def get_data_async(
        self,
        session: Session = None,
        on_response: Optional[Callable] = None,
        on_page_response: Optional[Callable] = None,
        closure: Optional[str] = None,
    ):
        """
        Returns a response asynchronously from the API to the library

        Parameters
        ----------
        session : Session, optional
            The Session defines the source where you want to retrieve your data
        on_response : Callable, optional
            Callable object to process retrieved data
        on_page_response : Callable, optional
            Callable object to process retrieved data
        closure : str, optional
            Specifies the parameter that will be merged with the request

        Returns
        -------
        NewsHeadlines.NewsHeadlinesResponse

        Raises
        ------
        AttributeError
            If user didn't set default session.

        Examples
        --------
        >>> from refinitiv.data.content import news
        >>> definition = news.headlines.Definition("Refinitiv",
        >>>                                        date_from="20.03.2021",
        >>>                                        date_to=timedelta(days=-4),
        >>>                                        count=3)
        >>> response = await definition.get_data_async()
        """

        if session is None:
            session = get_default()
        news_headlines = NewsHeadlines(session=session, on_response=on_response)
        response = await news_headlines.get_headlines_async(
            query=self.query,
            count=self.count,
            date_from=self.date_from,
            date_to=self.date_to,
            sort_order=self.sort_order,
            on_page_response=on_page_response,
            closure=closure,
            extended_params=self.extended_params,
        )
        return response

    def __repr__(self):
        return create_str_definition(
            self,
            middle_path="content.news",
            content=f"{{query='{self.query}'}}",
        )

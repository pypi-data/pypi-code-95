from typing import Callable, Optional

from .news_story import NewsStory
from ...core.session import get_default
from ...tools._repr_definition import create_str_definition
from refinitiv.data._data.core.session import Session


__all__ = ["Definition"]


class Definition:
    """
    This class describes parameters to retrieve data for news story.

    Parameters
    ----------
    story_id : str
        News Story ID.

    extended_params : dict, optional
        Other parameters can be provided if necessary

    Examples
    --------
    >>> from refinitiv.data.content import news
    >>> definition = news.story.Definition("urn:newsml:reuters.com:20201026:nPt6BSyBh")
    """

    def __init__(self, story_id: str, extended_params: dict = None):
        self.story_id = story_id
        self.extended_params = extended_params

    def get_data(
        self,
        session: Session = None,
        on_response: Callable = None,
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
        closure : str, optional
            Specifies the parameter that will be merged with the request

        Returns
        -------
        NewsStory.NewsStoryResponse

        Raises
        ------
        AttributeError
            If user didn't set default session.

        Examples
        --------
        >>> from refinitiv.data.content import news
        >>> response = news.story.Definition("urn:newsml:reuters.com:20201026:nPt6BSyBh").get_data()
        """
        if session is None:
            session = get_default()
        news_headlines = NewsStory(session=session, on_response=on_response)
        response = news_headlines.get_story(
            story_id=self.story_id,
            closure=closure,
            extended_params=self.extended_params,
        )
        return response

    async def get_data_async(
        self,
        session: Session = None,
        on_response: Callable = None,
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
        closure : str, optional
            Specifies the parameter that will be merged with the request

        Returns
        -------
        NewsStory.NewsStoryResponse

        Raises
        ------
        AttributeError
            If user didn't set default session.

        Examples
        --------
        >>> from refinitiv.data.content import news
        >>> response = await news.story.Definition("urn:newsml:reuters.com:20201026:nPt6BSyBh").get_data_async()
        """

        if session is None:
            session = get_default()
        news_headlines = NewsStory(session=session, on_response=on_response)
        response = await news_headlines.get_story_async(
            story_id=self.story_id,
            closure=closure,
            extended_params=self.extended_params,
        )
        return response

    def __repr__(self):
        return create_str_definition(
            self,
            middle_path="content.news",
            content=f"{{story_id='{self.story_id}'}}",
        )

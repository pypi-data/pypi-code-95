# coding: utf8

__all__ = ["NewsStory", "NewsStoryResponse"]

from ...tools._common import urljoin
from ...delivery.data import Endpoint
from .data_classes import Story


class NewsStoryResponse(Endpoint.EndpointResponse):
    def __init__(self, response):
        super().__init__(response)
        _raw_json = None
        if self.is_success:
            _raw_json = self.data.raw
        self._data = NewsStory.NewsStoryData(_raw_json)

    def __str__(self):
        if self._data and self._data.raw:
            return self._data.raw["newsItem"]["contentSet"]["inlineData"][0]["$"]
        else:
            return f"{self.status}"

    @property
    def html(self):
        if self._data and self._data.raw:
            return self._data.raw["newsItem"]["contentSet"]["inlineXML"][0]["$"]
        else:
            return None

    @property
    def text(self):
        if self._data and self._data.raw:
            return self._data.raw["newsItem"]["contentSet"]["inlineData"][0]["$"]
        else:
            return None


class NewsStory(object):
    NewsStoryResponse = NewsStoryResponse

    class NewsStoryData:
        def __init__(self, raw_json):
            self._story = None
            self._raw = raw_json

        @property
        def raw(self):
            return self._raw

        @property
        def story(self):
            if self._story is None:
                self._story = Story.create(self._raw)
            return self._story

    def __init__(self, session, on_response=None):
        from ...core.session import get_default

        if session is None:
            session = get_default()

        if session is None:
            raise AttributeError("Session must be defined")

        config = session._get_endpoint_config("data.news")
        base_url = config.get_str("url")
        stories_url = config.get_str("endpoints.stories")
        self._url = urljoin(base_url, stories_url, "/{story_id}")

        self._session = session
        self._on_response_cb = on_response

        self._data = None
        self._status_code = None
        self._error_message = None

        self._endpoint_story = Endpoint(
            session, self._url, on_response=self._on_response
        )

    def __str__(self):
        if self._data:
            return self._data.text

    @property
    def data(self):
        return self._data

    @property
    def status_code(self):
        return self.status()

    @property
    def error_message(self):
        return self._error_message

    def _on_response(self, endpoint, data):

        self._data = data

        if self._on_response_cb:
            _result = NewsStory.NewsStoryResponse(data._response)

            if not _result.is_success:
                self._endpoint_story.session.log(
                    1, f"News Story request failed: {_result.status}"
                )

            self._on_response_cb(self, _result)

    #####################################################
    #  methods to request news story synchronously      #
    #####################################################
    def get_story(self, story_id, closure=None, extended_params=None):
        return self._session._loop.run_until_complete(
            self.get_story_async(
                story_id,
                closure,
                extended_params,
            )
        )

    #####################################################
    #  methods to request news story asynchronously     #
    #####################################################
    async def get_story_async(
        self,
        story_id,
        closure=None,
        extended_params: dict = None,
    ):
        path_parameters = {"story_id": story_id}
        path_parameters.update(extended_params or {})

        _result = await self._endpoint_story.send_request_async(
            Endpoint.RequestMethod.GET,
            header_parameters={"Accept": "application/json"},
            path_parameters=path_parameters,
            closure=closure,
        )

        _story_result = NewsStory.NewsStoryResponse(_result._response)

        if not _story_result.is_success:
            self._endpoint_story.session.log(
                1, f"News Story request failed: {_story_result.status}"
            )

        return _story_result

    ######################################################
    #  methods to request historical data asynchronously #
    ######################################################

    @staticmethod
    def _get_headline_from_story(story):
        if story and story.get("newsItem"):
            if story.get("newsItem").get("contentMeta"):
                if story.get("newsItem").get("contentMeta").get("headline"):
                    return (
                        story.get("newsItem")
                        .get("contentMeta")
                        .get("headline")[0]
                        .get("$")
                    )

    @staticmethod
    def _get_text_from_story(story):
        if story and story.get("newsItem"):
            if story.get("newsItem").get("contentSet"):
                if story.get("newsItem").get("contentSet").get("inlineData"):
                    return (
                        story.get("newsItem")
                        .get("contentSet")
                        .get("inlineData")[0]
                        .get("$")
                    )

    @staticmethod
    def _get_html_from_story(story):
        if story and story.get("newsItem"):
            if story.get("newsItem").get("contentSet"):
                if story.get("newsItem").get("contentSet").get("inlineData"):
                    return (
                        story.get("newsItem")
                        .get("contentSet")
                        .get("inlineData")[0]
                        .get("$")
                    )

    @staticmethod
    def _convert_story_json_to_pandas(json_story_data):
        return None

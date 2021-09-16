from ...tools._datetime import to_datetime
from .urgency import Urgency


class NewsData(object):
    def __init__(
        self,
        title,
        creator,
        source,
        language,
        item_codes,
        urgency,
        creation_date,
        update_date,
        raw,
        news_type,
    ):
        from refinitiv.data._data.content.news.news_story import NewsStory

        self.title = title
        self.creator = creator
        self.source = source
        self.language = language
        self.item_codes = item_codes
        self.urgency = Urgency(urgency)
        self.creation_date = to_datetime(creation_date)
        self.update_date = to_datetime(update_date)

        if news_type == "story":
            self.content = NewsStory._get_text_from_story(raw)
            self.headline = NewsStory._get_headline_from_story(raw)
        elif news_type == "headline":
            self.story_id = raw["storyId"]


class Headline(NewsData):
    @staticmethod
    def create(datum):
        news_item = datum.get("newsItem")
        content_meta = news_item.get("contentMeta")
        item_meta = news_item.get("itemMeta")
        subject = content_meta.get("subject")
        headline = Headline(
            title=item_meta.get("title")[0].get("$"),
            creator=content_meta.get("creator")[0].get("_qcode"),
            source=content_meta.get("infoSource"),
            language=content_meta.get("language"),
            item_codes=[item.get("_qcode") for item in subject],
            urgency=content_meta.get("urgency").get("$"),
            creation_date=item_meta.get("firstCreated").get("$"),
            update_date=item_meta.get("versionCreated").get("$"),
            raw=datum,
            news_type="headline",
        )
        return headline


class Story(NewsData):
    @staticmethod
    def create(datum):
        news_item = datum.get("newsItem")
        content_meta = news_item.get("contentMeta")
        item_meta = news_item.get("itemMeta")
        subject = content_meta.get("subject")
        headline = Headline(
            title=item_meta.get("title")[0].get("$"),
            creator=content_meta.get("creator")[0].get("_qcode"),
            source=content_meta.get("infoSource"),
            language=content_meta.get("language"),
            item_codes=[item.get("_qcode") for item in subject],
            urgency=content_meta.get("urgency").get("$"),
            creation_date=item_meta.get("firstCreated").get("$"),
            update_date=item_meta.get("versionCreated").get("$"),
            raw=datum,
            news_type="story",
        )
        return headline

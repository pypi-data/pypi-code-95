from credmgr.models.utils import CachedProperty


class RedditAppMixin:
    _editableAttrs = []

    @CachedProperty
    def redditApp(self):
        if not self._fetched:
            self._fetch()
        redditApp = self._credmgr.redditApp(id=self.redditAppId)
        return redditApp

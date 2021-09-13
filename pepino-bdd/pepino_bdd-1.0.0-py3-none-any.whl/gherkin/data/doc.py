from ..location import GherkinLocation
from ...data import DocumentString


class GherkinDocString(GherkinLocation, DocumentString):

    def __init__(self, parsed):
        super(GherkinDocString, self).__init__(parsed)
        self._content = parsed["content"]

    @property
    def content(self):
        return self._content

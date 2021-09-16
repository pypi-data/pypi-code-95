from typing import Optional as _Optional

import attr


class PluginTable:
    def __str__(self):
        opts = ", ".join(k for k in self.__dict__)
        return f"PluginTable({opts})"

    def __repr__(self):
        opts = ", ".join(k for k in self.__dict__)
        return f"PluginTable({opts})"


class UserOptionsTable:
    def __str__(self):
        opts = ", ".join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"UserOptionsTable({opts})"

    def __repr__(self):
        opts = ", ".join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"UserOptionsTable({opts})"


@attr.s(auto_attribs=True)
class TaxonomyTable:
    key: str
    singular: _Optional[str] = None
    plural: _Optional[str] = None

    def __attrs_post_init__(self):
        if self.singular is None:
            self.singular = self.key
        if self.plural is None:
            self.plural = self.key


@attr.s(auto_attribs=True)
class Config:
    title: str = "MySite"
    url: str = "https://example.com"
    language: str = "en"
    pluginspath: str = "plugins"
    content: str = "content"
    output: str = "_output"
    readers: _Optional[list[str]] = ["markdown", "static"]
    generators: _Optional[list[str]] = ["macros", "markdown"]
    writers: _Optional[list[str]] = ["theme", "copy"]
    taxonomies: list[TaxonomyTable] = attr.ib(factory=list, init=False, repr=False)
    user: UserOptionsTable = attr.ib(factory=UserOptionsTable, repr=False)
    plugins: PluginTable = attr.ib(factory=PluginTable, init=False)

    def get(self, name, default=None):
        return getattr(self, name, default)

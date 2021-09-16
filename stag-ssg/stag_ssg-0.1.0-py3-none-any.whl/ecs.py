from __future__ import annotations

import os
from collections import UserDict, defaultdict
from datetime import date as _date_t
from datetime import datetime as _datetime_t

from typing import Union as _Union
from typing import Optional as _Optional
from typing import Any as _Any
from collections.abc import Mapping as _Mapping

from stag.config import TaxonomyTable as _TaxonomyTable

import attr
from dateutil.parser import parse as _parse_dt


# sentinel used for parameters for which None is a valid value
_ANY = "_ANY"


def _urlize(url):
    url = url.strip("/")
    return f"/{url}"


@attr.s(auto_attribs=True, frozen=True)
class Path:
    path: str
    root_dir: str

    @property
    def relpath(self):
        return self.path[len(self.root_dir) :].strip("/")

    @property
    def ext(self):
        return os.path.splitext(self.path)[1][len(os.extsep) :]

    @property
    def filebase(self):
        return os.path.splitext(self.basename)[0]

    @property
    def basename(self):
        return os.path.basename(self.path)

    @property
    def reldirname(self):
        return os.path.dirname(self.relpath)


@attr.s(auto_attribs=True)
class Content:
    type: str
    content: _Any = attr.ib(None, repr=False)


class Metadata(UserDict):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._normalize_data()

    def _normalize_data(self):
        title = self.data.get("title", "")
        date = self.data.get("date")
        if date:
            if isinstance(date, (int, str, float)):
                self.data["date"] = _parse_dt(date)
            elif type(date) == _date_t:
                self.data["date"] = _datetime_t.fromordinal(date.toordinal())
            self.data["timestamp"] = self.data["date"].timestamp()

        self.__dict__.update(self.data)


def _terms_factory():
    return defaultdict(set)


@attr.s(auto_attribs=True)
class Taxonomy:
    key: str
    singular: str
    plural: str
    terms: _Mapping[str, set[Page]] = attr.ib(factory=_terms_factory, repr=False)

    def __getitem__(self, key):
        return self.terms[key]

    def __setitem__(self, key, val):
        self.terms[key] = val


@attr.s(auto_attribs=True, cmp=False, hash=False)
class Page:
    _url: str = attr.ib(converter=_urlize)
    metadata: _Optional[Metadata] = attr.ib(default=None, repr=False)
    source: _Optional[Path] = attr.ib(default=None, repr=False)
    input: _Optional[Content] = attr.ib(default=None, repr=False)
    output: _Optional[Content] = attr.ib(default=None, repr=False)
    taxonomy: _Optional[Taxonomy] = attr.ib(default=None, repr=False)
    list: _Optional[list[Page]] = attr.ib(default=None, repr=False)

    @property
    def url(self):
        return self._url

    def __hash__(self):
        return hash(self._url)

    def __eq__(self, other):
        return self._url == other._url

    def __lt__(self, other):
        return self._url < other._url


@attr.s(auto_attribs=True)
class Site:
    config: dict = attr.ib(repr=False)
    _pages: _Mapping[str, Page] = attr.ib(factory=dict, repr=False)
    taxonomies: _Optional[list[Taxonomy]] = attr.ib(None, repr=False)

    @property
    def pages(self):
        return list(self._pages.values())

    @property
    def ordinary_pages(self):
        for page in self._pages.values():
            if page.source and page.input and page.output and page.metadata:
                yield page

    def subpages_of(self, val):
        base = _urlize(val)
        for page in self.ordinary_pages:
            cmp, _, _ = page.url.rpartition("/")
            if cmp == base:
                yield page

    def add_page(self, page):
        if page.url in self._pages:
            raise ValueError(f"URL {page.url} for file {path} not unique")
        self._pages[page.url] = page

    def get_or_create_page(self, url):
        return self._pages.setdefault(_urlize(url), Page(url=url))

    def filter_pages(self, ptype=_ANY):
        for page in self.pages:
            if page.metadata is not None and ptype is _ANY:
                yield page
            elif page.metadata is not None and page.metadata.get("type", _ANY) == ptype:
                yield page

    def find(self, url):
        return self._pages.get(_urlize(url))

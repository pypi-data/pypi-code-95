from typing import Callable, Dict, List, Set
from urllib.parse import unquote

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _

from appchance_sections.cache import get_contents_cache, get_contents_cache_key, get_contents_cache_timeout


class Content:
    def __init__(
        self, slug, url, *, name=None, query_params=None, path_params=None, widgets=None, placements=None, prefix=None
    ):
        self.slug = slug
        self.name = name or slug
        self.url = url
        self.query_params = query_params or {}
        self.path_params = path_params or {}
        self.widgets = widgets or []
        self.placements = placements or []
        self.prefix = prefix

    def __str__(self):
        return self.slug

    def get_url(self, section=None, **kwargs):
        url = reverse(self.url, kwargs=self._get_path_params(**kwargs))
        query_string = urlencode(self._get_query_params(section))
        if query_string:
            return f"{url}?{query_string}"
        return url

    def _get_path_params(self, **kwargs):
        path_params = {}
        for key, val in self.path_params.items():
            if key in kwargs and kwargs[key] is not None:
                val = kwargs[key]
            elif not val:
                val = "{%s}" % key
            path_params[key] = val
        return path_params

    def _get_query_params(self, section):
        query_params = self.query_params
        if section and section.num_items > 0:
            query_params["page_size"] = section.num_items
        return query_params


class DynamicContentAbstract(models.Model):
    URL = ""
    QUERY_PARAMS: Dict[str, str] = {}
    WIDGETS: List[str] = []
    PLACEMENTS: List[str] = []
    PREFIX = ""
    NAME_FIELD = ""
    FILTER_ATTRIBUTE = ""

    name = models.CharField(_("Name"), max_length=255, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.pk}"

    @property
    def content_slug(self):
        return f"{self.__class__.__name__}-{self.id}"

    @property
    def name_field(self):
        return getattr(self, self.NAME_FIELD) if self.NAME_FIELD and hasattr(self, self.NAME_FIELD) else str(self)

    @classmethod
    def get_cache_key(cls):
        return f"section_dynamic_content_{cls.__name__}"

    @classmethod
    def get_all_objects(cls):
        return cls.objects.all()


class SectionAbstract(models.Model):
    _contents: Dict[str, Content] = {}
    _content_callbacks: Set[Callable] = set()

    name = models.CharField(_("Name"), max_length=255, blank=True, null=True)

    content_slug = models.CharField(_("Content"), max_length=255)

    num_items = models.PositiveIntegerField(_("Number of items"), default=1)

    widget = models.CharField(_("Widget"), max_length=64, null=True, blank=True)
    placement = models.CharField(_("Placement"), max_length=64, null=True, blank=True)
    order = models.PositiveSmallIntegerField(_("Order"), default=0)

    is_active = models.BooleanField(_("Is active"), default=True)

    class Meta:
        abstract = True
        verbose_name = _("Section")
        verbose_name_plural = _("Sections")
        ordering = ["placement", "order"]

    def __str__(self):
        return f"id {self.id}"

    @classmethod
    def get_contents(cls) -> Dict[str, Content]:
        cache = get_contents_cache()
        key = get_contents_cache_key()
        timeout = get_contents_cache_timeout()
        contents = cache.get(key)
        if not contents:
            dynamic_contents = {}
            for callback in cls._content_callbacks:
                items = callback()
                for item in items:
                    dynamic_contents[item.slug] = item
            contents = {**cls._contents, **dynamic_contents}
            cache.set(key, contents, timeout)
        return contents

    @classmethod
    def get_widgets(cls):
        widgets: List[str] = []
        for content in cls.get_contents().values():
            widgets += content.widgets
        return list(set(widgets))

    @classmethod
    def get_placements(cls):
        placements: List[str] = []
        for content in cls.get_contents().values():
            placements += content.placements
        return list(set(placements))

    @property
    def content(self):
        return self.get_contents()[self.content_slug]

    def clean(self):
        error_dict = {}
        try:
            if self.widget not in self.content.widgets:
                error_dict["widget"] = ValidationError(
                    _("Can not set `%s` widget for `%s` content.") % (self.widget, self.content_name)
                )

            if self.placement not in self.content.placements:
                error_dict["placement"] = ValidationError(
                    _("Can not set `%s` placement for `%s` content.") % (self.placement, self.content_name)
                )

            if self.placement and self.widget:
                placement_prefix, *_ignore = self.placement.split("_")
                widget_prefix, *_ignore = self.widget.split("_")

                if placement_prefix != widget_prefix:
                    error_dict["widget"] = ValidationError(
                        _("Can not set `%s` widget for `%s` placement (`%s` is not equal `%s`).")
                        % (self.widget, self.placement, widget_prefix, placement_prefix)
                    )
        except KeyError:
            pass

        if error_dict:
            raise ValidationError(error_dict)

    @property
    def content_name(self):
        return self.content.name

    @property
    def content_url(self):
        return unquote(self.content.get_url(section=self))

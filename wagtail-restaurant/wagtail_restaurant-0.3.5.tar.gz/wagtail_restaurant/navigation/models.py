from django.db import models
from django_extensions.db.fields import AutoSlugField

from wagtail.admin.edit_handlers import MultiFieldPanel, InlinePanel, FieldPanel, PageChooserPanel
from wagtail.snippets.models import register_snippet
from wagtail.core.models import Orderable
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

class NavigationItem(Orderable):
    title = models.CharField(blank=True, null=True, max_length=50)
    url = models.CharField(blank=True, null=True, max_length=100,)
    page = models.ForeignKey("wagtailcore.Page", null=True, blank=True, related_name="+", on_delete=models.CASCADE,)
    target_new = models.BooleanField(default=False, blank=True)
    navigation = ParentalKey("Navigation", related_name="navigation_items")

    panels = [
        FieldPanel("title"),
        FieldPanel("url"),
        PageChooserPanel("page"),
        FieldPanel("target_new"),
    ]

    @property
    def link(self):
        if self.page:
            return self.page.url
        elif self.url:
            return self.url
        return '#'


@register_snippet
class Navigation(ClusterableModel):
    title = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from="title", editable=True)

    panels = [
        MultiFieldPanel([
            FieldPanel("title"),
            FieldPanel("slug"),
        ], heading="Navigation"),
        InlinePanel("navigation_items", label="Navigation Item")
    ]

    def __str__(self):
        return self.title
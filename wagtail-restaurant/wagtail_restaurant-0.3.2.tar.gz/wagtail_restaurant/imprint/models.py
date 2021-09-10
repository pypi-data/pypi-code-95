from django.db import models

from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.core.fields import StreamField

from wagtail.core.models import Page

from .blocks import ImprintData

import pathlib
resolve_path = pathlib.Path(__file__).resolve().parent # Resolve current directory for template

class ImprintPage(Page): 
    
    template = 'imprint/imprint_page.html'
    imprint_data = StreamField([("imprint_data", ImprintData())], null=True, blank=True)

    content_panels = Page.content_panels + [
        StreamFieldPanel("imprint_data"),
    ]


    class Meta:  # noqa
        verbose_name = "Imprint Page"
        verbose_name_plural = "Imprint Pages"
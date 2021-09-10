from django.db import models

from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core import blocks as streamfield_blocks
from wagtail.core.models import Page
from .blocks import PageHeroBlock, HomeMenuHead, MenuBlock, MenuFlatBlock, MenuColumnBlock

import pathlib
resolve_path = pathlib.Path(__file__).resolve().parent # Resolve current directory for template

class MenuPage(Page):

    template = 'menu/menu_page.html'
    hero = StreamField([("page_hero", PageHeroBlock())],null=True,blank=True,)
    home_menu_head = StreamField([("home_menu_head", HomeMenuHead())],null=True,blank=True,)
    menu = StreamField([("menu", MenuBlock())], null=True, blank=True)
    menu_flat = StreamField([("menu_flat", MenuFlatBlock())], null=True, blank=True)
    menu_column = StreamField([("menu_column", MenuColumnBlock())], null=True, blank=True)


    content_panels = Page.content_panels + [
        StreamFieldPanel("hero"),
        StreamFieldPanel("home_menu_head"),
        StreamFieldPanel("menu"),
        StreamFieldPanel("menu_flat"),
        StreamFieldPanel("menu_column"),
    ]

    class Meta:
        verbose_name = "Menu Page"
        verbose_name_plural = "Menu Pages"

    def get_sitemap_urls(self, obj):
        return [
            {
                'location': self.full_url,
                'lastmod': self.latest_revision_created_at,
                'changefreq': 'monthly',
                'priority': 1,
                
            }
        ]


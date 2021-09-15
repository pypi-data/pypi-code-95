from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.core.templatetags.wagtailcore_tags import richtext

class PageHeroBlock(blocks.StructBlock):
    image = ImageChooserBlock()

    class Meta:  # noqa
        template = "simple/blocks/hero.html"
        icon = "edit"
        label = "Page Hero"

class PageGallery (blocks.StructBlock):
    title = blocks.CharBlock(required=False, help_text="Add your title")
    image = ImageChooserBlock(required=False)

    class Meta:  # noqa
        template = "simple/blocks/gallery.html"
        icon = "placeholder"
        label = "Gallery"
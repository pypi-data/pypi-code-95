from wagtail.core import blocks
from wagtail.core.templatetags.wagtailcore_tags import richtext
from wagtail.images.blocks import ImageChooserBlock

class PageHeroBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True, help_text="Add your title")
    sub_title = blocks.CharBlock(required=False, help_text="Add subtitle")
    description = blocks.RichTextBlock(required=False, help_text="Add additional description")
    image = ImageChooserBlock()

    class Meta:  # noqa
        template = "menu/blocks/hero_block.html"
        icon = "edit"
        label = "Page Hero"



class HomeMenuHead (blocks.StructBlock):
    title = blocks.CharBlock(required=True, help_text="Add your title")
    description = blocks.RichTextBlock(required=False, help_text="Add additional description")
    image = ImageChooserBlock(required=False)

    class Meta:  # noqa
        template = "menu/blocks/home_menu_head_block.html"
        icon = "placeholder"
        label = "Home Menu Head"



class MenuBlock (blocks.StructBlock):
    title = blocks.CharBlock(required=True, help_text="Add your title")
    image = ImageChooserBlock(required=False)
    foods = blocks.ListBlock(
                blocks.StructBlock(
                    [

                        ("image", ImageChooserBlock(required=False)),
                        ("title", blocks.CharBlock(required=True, max_length=40)),
                        ("price", blocks.CharBlock(required=True, max_length=10)),
                        ("description", blocks.TextBlock(required=False, max_length=200)),
                    ]
                )
            )

    class Meta:  # noqa
        template = "menu/blocks/menu_block.html"
        icon = "placeholder"
        label = "Menu"



class MenuFlatBlock (blocks.StructBlock):
    title = blocks.CharBlock(required=True, help_text="Add your title")
    image = ImageChooserBlock(required=False)
    foods = blocks.ListBlock(
                blocks.StructBlock(
                    [
                        ("image", ImageChooserBlock(required=False)),
                        ("title", blocks.CharBlock(required=True, max_length=40)),
                        ("price", blocks.CharBlock(required=True, max_length=10)),
                        ("description", blocks.TextBlock(required=False, max_length=200)),
                    ]
                )
            )

    class Meta:  # noqa
        template = "menu/blocks/menu__flat_block.html"
        icon = "placeholder"
        label = "Menu Flat"

class MenuColumnBlock (blocks.StructBlock):
    title = blocks.CharBlock(required=True, help_text="Add your title")
    image = ImageChooserBlock(required=False)
    foods = blocks.ListBlock(
                blocks.StructBlock(
                    [
                        ("image", ImageChooserBlock(required=False)),
                        ("title", blocks.CharBlock(required=True, max_length=40)),
                        ("price", blocks.CharBlock(required=True, max_length=10)),
                        ("description", blocks.TextBlock(required=False, max_length=200)),
                    ]
                )
            )

    class Meta:  # noqa
        template = "menu/blocks/menu_column_block.html"
        icon = "placeholder"
        label = "Menu Column"
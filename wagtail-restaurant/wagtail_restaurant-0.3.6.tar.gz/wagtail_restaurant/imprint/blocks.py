from wagtail.core import blocks

class ImprintData(blocks.StructBlock):
    tax_id = blocks.CharBlock(required=True, help_text="Add your Tax ID")
    company_authority = blocks.CharBlock(required=True, help_text="Company Authority")
    non_warranty = blocks.CharBlock(required=True, help_text="Add your non warranty")
    description = blocks.RichTextBlock(required=False, help_text="Add additional description")

    class Meta:  # noqa
        template = "imprint/blocks/imprint.html"
        icon = "edit"
        label = "Page Imprint"
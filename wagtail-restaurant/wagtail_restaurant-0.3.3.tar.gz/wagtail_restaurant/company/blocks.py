from wagtail.core import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.core.templatetags.wagtailcore_tags import richtext



class CompanySettings(blocks.StructBlock):
    company_svg_logo = DocumentChooserBlock(required=False)
    company_jpg_logo = ImageChooserBlock(required=False)
    company_name = blocks.CharBlock(required=False, help_text="Company name")
    company_legal_name = blocks.CharBlock(required=False, help_text="Company legal name")
    company_description = blocks.CharBlock(required=False, help_text="Company description")
    cuisine = blocks.CharBlock(required=False, help_text="Cuisine (eg.türkisches,französische)")
    reservations = blocks.BooleanBlock(required=False, help_text="Reservations")
    currencies_accepted = blocks.CharBlock(required=False, help_text="Currencies Accepted (eg.EUR,USD)")
    payment_accepted = blocks.CharBlock(required=False, help_text="Payment Accepted (eg.Cash, Visa, Master Card)")
    price_range = blocks.CharBlock(required=False, help_text="Price Range (eg.€2 - €15)")

    class Meta:
        icon = "edit"
        label = "Contact Channels"

class CompanySales(blocks.StructBlock):
    title = blocks.CharBlock(required=False, help_text="Title For channel (eg.Lieferando)")
    slug = blocks.CharBlock(required=False, help_text="Slug For channel (eg.lieferando)")
    url = blocks.URLBlock(required=False,help_text="Sale Channel URL")
    class Meta:
        icon = "edit"
        label = "Company Sales"



class CompanyContact(blocks.StructBlock):
    phone = blocks.CharBlock(required=False, help_text="Company phone number (eg.+49-000-000-0000)")
    phone_short = blocks.CharBlock(required=False, help_text="Company short phone number (eg.000-0000)")
    phone_call = blocks.CharBlock(required=False, help_text="Company short phone number (eg.0000000)")
    fax = blocks.CharBlock(required=False, help_text="Company fax number")
    email = blocks.CharBlock(required=False, help_text="Company email address")

    class Meta:
        icon = "edit"
        label = "Contact Channels"


class CompanyAddress(blocks.StructBlock):
    country_code = blocks.CharBlock(required=False, help_text="Country Code (eg.DE)")
    city = blocks.CharBlock(required=False, help_text="City")
    region = blocks.CharBlock(required=False, help_text="Region")
    post_code = blocks.CharBlock(required=False, help_text="Post Code")
    street = blocks.CharBlock(required=False, help_text="Street / Number")
    class Meta:
        icon = "edit"
        label = "Company Address"


class CompanyGoogleMap(blocks.StructBlock):
    latitude = blocks.CharBlock(required=False, help_text="Address Latitude")
    longitude = blocks.CharBlock(required=False, help_text="Address Longitude")
    class Meta:
        icon = "edit"
        label = "Google Map"


class CompanySocialMedia(blocks.StructBlock):
    tripadvisor = blocks.URLBlock(required=False,help_text="Tripadvisor Url")
    lieferando = blocks.URLBlock(required=False,help_text="Lieferando Url")
    facebook = blocks.URLBlock(required=False,help_text="Facebook Url")
    instagram = blocks.URLBlock(required=False,help_text="Instagram Url")
    youtube = blocks.URLBlock(required=False,help_text="Youtube Url")
    twitter = blocks.URLBlock(required=False,help_text="Twitter Url")

    class Meta:
        icon = "edit"
        label = "Social Media"

class CompanyPromote(blocks.StructBlock):
    promote = blocks.RawHTMLBlock(required=False,help_text="Promote Text")
    class Meta:
        icon = "edit"
        label = "Promote"


class CompanyPhotos(blocks.StructBlock):
    company_photos = ImageChooserBlock(required=False)
    class Meta:
        icon = "edit"
        label = "Company Photos"







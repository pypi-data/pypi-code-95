from django.db import models

from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, TabbedInterface, ObjectList
from wagtail.contrib.settings.models import BaseSetting, register_setting

from wagtail.images.models import Image
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.documents.edit_handlers import DocumentChooserPanel 

from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core import blocks as streamfield_blocks
from .blocks import CompanySettings, CompanyContact, CompanyAddress, CompanyGoogleMap, CompanySocialMedia, CompanyPromote, CompanyPhotos, CompanySales


class OpeningHours(models.Model):
	
	'''Business Open Hour.'''
	WEEKDAYS = [
	  (0, ("Monday")),
	  (1, ("Tuesday")),
	  (2, ("Wednesday")),
	  (3, ("Thursday")),
	  (4, ("Friday")),
	  (5, ("Saturday")),
	  (6, ("Sunday")),
	]

	weekday = models.IntegerField(choices=WEEKDAYS)
	from_hour = models.TimeField(blank=True, null=True)
	to_hour = models.TimeField(blank=True, null=True)


	class Meta:
		ordering = ('weekday', 'from_hour')
		unique_together = ('weekday', 'from_hour', 'to_hour')


	open_hours = [
		FieldPanel('weekday'),
		FieldPanel('from_hour'),
		FieldPanel('to_hour')
		]

	def __str__(self):
		return str(self.weekday)

	def __unicode__(self):
		return u'%s: %s - %s' % (self.get_weekday_display(), self.from_hour, self.to_hour)

@register_setting
class CompanyInfo(BaseSetting):

	'''Models'''
	company_settings = StreamField([("company_settings", CompanySettings())],null=True,blank=True,)
	company_sales = StreamField([("company_sales", CompanySales())],null=True,blank=True,)
	company_contact = StreamField([("company_contact", CompanyContact())],null=True,blank=True,)
	company_address = StreamField([("company_address", CompanyAddress())],null=True,blank=True,)
	company_google_map = StreamField([("company_google_map", CompanyGoogleMap())],null=True,blank=True,)
	company_social_media = StreamField([("company_social_media", CompanySocialMedia())],null=True,blank=True,)
	company_promote = StreamField([("company_promote", CompanyPromote())],null=True,blank=True,)
	company_photos = StreamField([("company_photos", CompanyPhotos())],null=True,blank=True,)


	'''Handler Objects'''
	company_settings_obj = [StreamFieldPanel("company_settings")]
	company_sales_obj = [StreamFieldPanel("company_sales")]
	company_contact_obj = [StreamFieldPanel("company_contact")]
	company_address_obj = [StreamFieldPanel("company_address")]
	company_google_map_obj = [StreamFieldPanel("company_google_map")]
	company_social_media_obj = [StreamFieldPanel("company_social_media")]
	company_promote_obj = [StreamFieldPanel("company_promote"),]
	company_photos_obj = [StreamFieldPanel("company_photos")]

	# example_obj = [
	# 	ImageChooserPanel('company_photos1'),
	# 	ImageChooserPanel('company_photos2'),
	# 	ImageChooserPanel('company_photos3'),
	# 	ImageChooserPanel('company_photos4')
	# 	]


	'''Handlers'''
	edit_handler = TabbedInterface([
		ObjectList(company_settings_obj, heading='Company Settings'),
		ObjectList(company_contact_obj, heading='Contact'),
		ObjectList(company_address_obj, heading='Address'),
		ObjectList(company_sales_obj, heading='Sales'),
		ObjectList(company_google_map_obj, heading='Google Map'),
		ObjectList(company_social_media_obj, heading='Social Media'),
		ObjectList(company_promote_obj, heading='Promote'),
		ObjectList(company_photos_obj, heading='Restaurant Photos'),
		])


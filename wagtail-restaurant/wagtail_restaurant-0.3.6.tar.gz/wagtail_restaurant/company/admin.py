from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from .models import OpeningHours

class OpeningHoursAdmin(ModelAdmin):

	model = OpeningHours
	menu_label = 'Opening Hours'
	menu_icon = 'time'
	# menu_order = 2
	add_to_settings_menu = True
	exclude_from_axplorer = False
	list_display = ('weekday', 'from_hour', 'to_hour',)
modeladmin_register(OpeningHoursAdmin)

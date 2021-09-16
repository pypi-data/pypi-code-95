from datetime import datetime
from django import template

from ..models import OpeningHours
import calendar

register = template.Library()


@register.simple_tag()
def opening__hours(): 
	return OpeningHours.objects.all()


# Getting weekday from database as number
# turn numbers to weekdays in template > {% numtoday i.weekday %}
@register.simple_tag
def numtoday(numtoday):
	return calendar.day_name[numtoday]

# Getting current week day > {% current_weekday %}
@register.simple_tag 
def current_weekday(): 
	return datetime.today().weekday()


@register.simple_tag 
def get_iso_weekday():
	return opening__hours().get(weekday=datetime.today().weekday())


# Checking to_hour from if is empty {% is_holdiay i.weekday%}
@register.filter(name='is_holdiay')
def is_holdiay(is_holdiay):
	return opening__hours().get(weekday=is_holdiay).to_hour


@register.simple_tag 
def get_current_time(): 
	return datetime.now().strftime('%H:%M')


@register.simple_tag 
def get_from_hour():
	return get_iso_weekday().from_hour.strftime('%H:%M')


@register.simple_tag 
def get_to_hour():
	return get_iso_weekday().to_hour.strftime('%H:%M')


@register.simple_tag 
def is_open():
	if get_iso_weekday().from_hour == None:
		pass
	else:
		if get_from_hour() <= get_current_time() and get_to_hour() >= get_current_time():
			return True
		else:
			return False
from django import template
from ..models import Navigation

register = template.Library()

@register.simple_tag()
def get_navigation(slug):
	return Navigation.objects.filter(slug=slug).first()
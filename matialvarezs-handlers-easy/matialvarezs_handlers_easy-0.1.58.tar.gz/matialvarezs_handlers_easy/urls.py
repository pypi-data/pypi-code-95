from django import VERSION as DJANGO_VERSION

if DJANGO_VERSION >= (2, 0):
	from django.urls import include, path, re_path as url
else:
	from django.conf.urls import include, url

from . import views

app_name = "matialvarezs_handlers_easy"

urlpatterns = [
	url(r'^matialvarezs_handlers_easy/$', views.index, name = 'index'),		
]



from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView

from . import views

app_name = 'authentication'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(
        r'^account/login/$', 
        TemplateView.as_view(template_name='public/login.html'), 
        name='login'
    ),
    url(
        r'^account/characters/main/$',
        views.main_character_change,
        name='change_main_character'
    ),
    url(
        r'^account/characters/add/$', 
        views.add_character, 
        name='add_character'
    ),   
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
]

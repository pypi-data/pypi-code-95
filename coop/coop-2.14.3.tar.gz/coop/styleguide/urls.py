from django.conf.urls import url

from .views import styleguide

urlpatterns = [
    url('^$', styleguide, name='styleguide', kwargs={'page': 'index'}),
    url('^(?P<page>.*)/$', styleguide, name='styleguide'),
]

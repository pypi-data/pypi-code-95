# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from netseasy import views


urlpatterns = [
    url(r'^webhook/(?P<id>\d+)/$', views.webhook),
]

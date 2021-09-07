#
# Copyright (c) 2019, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
from django.urls import path
from textrank.views import index, groups, keywords, rank, weightform, samples

app_name = 'textrank'


urlpatterns = [
    path('', index, name='index'),
    path('groups/', groups, name='groups'),
    path('groups/<int:id>/', groups, name='group'),
    path('keywords/', keywords, name='keywords'),
    path('keywords/<int:id>/', keywords, name='keyword'),
    path('rank/', rank, name='rank'),
    path('rank/<str:format>/', rank, name='rank'),
    path('weightform/', weightform, name='add_weight'),
    path('weightform/<int:id>/', weightform, name='change_weight'),
    path('samples/', samples, name='samples'),
    path('samples/<int:id>/', samples, name='sample'),
]

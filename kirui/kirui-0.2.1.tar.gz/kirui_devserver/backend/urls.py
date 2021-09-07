from django.urls import path

from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('form/', views.form, name='form'),
    path('data/', views.data, name='data'),
    path('modal/', views.modal, name='modal'),
    path('table/', views.table, name='table'),
    path('panel/', views.panel, name='panel'),
    path('panel/data/', views.panel_data, name='panel-data'),
    path('vfs/poll/', views.poll_filesystem_changes, name='vfs-poll'),
]

app_name = 'backend'

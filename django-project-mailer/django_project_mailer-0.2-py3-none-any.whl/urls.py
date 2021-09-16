"""Email URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from rest_framework.routers import DefaultRouter
from .views import *
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register('register', EmailSettingAPIView, basename='')
router.register('email_reminder', EmailReminderView, basename='email_reminder')
router.register('push_reminder', PushReminderView, basename='push_reminder')
router.register('policy', PolicyView, basename='policy')
router.register('modules', ModuleView, basename='modules')
router.register('user',User,basename = "user")
urlpatterns = [
    path('project-mailer', include(router.urls)),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

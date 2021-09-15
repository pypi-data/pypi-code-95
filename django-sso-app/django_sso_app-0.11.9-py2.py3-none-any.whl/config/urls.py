from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.utils import timezone
from django.views import defaults as default_views
from django.views.decorators.http import last_modified
from django.contrib.flatpages.views import flatpage
from django.views.i18n import JavaScriptCatalog
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
# rpc
from rpc4django.views import serve_rpc_request
# sitemap
from django.contrib.sitemaps.views import sitemap
from django.contrib.flatpages.sitemaps import FlatPageSitemap

# django-sso-app
from ..urls import (urlpatterns as django_sso_app__urlpatterns,
                    api_urlpatterns as django_sso_app__api_urlpatterns,
                    i18n_urlpatterns as django_sso_app_i18n_urlpatterns)

from ..backend.views import set_language_from_url
from ..backend.api.views import StatsView, schema_view
from ..backend.pages.views import HomeView


last_modified_date = timezone.now()
js_info_dict = {}

urlpatterns = []
api_urlpatterns = []
_I18N_URLPATTERNS = []

urlpatterns += django_sso_app__urlpatterns
api_urlpatterns += django_sso_app__api_urlpatterns
_I18N_URLPATTERNS += django_sso_app_i18n_urlpatterns

urlpatterns += [
    # pai
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^jsi18n/$', last_modified(lambda req, **kw: last_modified_date)(JavaScriptCatalog.as_view()), js_info_dict,
        name='javascript-catalog'),

    # Django Admin, use -% url 'admin:index' %-
    path(settings.ADMIN_URL, admin.site.urls),

    # set language url
    url(r'^set_language/(?P<user_language>\w+)/$', set_language_from_url, name="set_language_from_url"),

    # flatpages sitemap
    path('sitemap.xml', sitemap, {'sitemaps': {'flatpages': FlatPageSitemap()}},
         name='django.contrib.sitemaps.views.sitemap'),
]

_I18N_URLPATTERNS += [
    path('', login_required(HomeView.as_view(template_name='pages/home.html')), name='home'),

    # flatpages
    path('about/', flatpage, {'url': '/about/'}, name='about'),
    path('privacy-policy/', flatpage, {'url': '/privacy-policy/'}, name='privacy-policy'),
    path('legal-notes/', flatpage, {'url': '/legal-notes/'}, name='legal-notes'),
    path('media-policy/', flatpage, {'url': '/media-policy/'}, name='media-policy'),
]

if settings.I18N_PATH_ENABLED:
    urlpatterns += i18n_patterns(
        *_I18N_URLPATTERNS
    )
else:
    urlpatterns += _I18N_URLPATTERNS


# Your stuff: custom urls includes go here
urlpatterns += [
    path('users/', include('django_sso_app.backend.users.urls', namespace='users')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            '400/',
            default_views.bad_request,
            kwargs={'exception': Exception('Bad Request!')},
        ),
        path(
            '403/',
            default_views.permission_denied,
            kwargs={'exception': Exception('Permission Denied')},
        ),
        path(
            '404/',
            default_views.page_not_found,
            kwargs={'exception': Exception('Page not Found')},
        ),
        path('500/', default_views.server_error),
    ]

    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]


api_urlpatterns += [
    url(r'^api/v1/_stats/$', StatsView.as_view(), name='stats'),

    url(r'^rpc/v2/$', serve_rpc_request),

    # your api here
]

# extra
from .extra_urls import api_urlpatterns as extra_api_urlpatterns
if len(extra_api_urlpatterns):
    api_urlpatterns += extra_api_urlpatterns

urlpatterns += api_urlpatterns

urlpatterns += [
    url(r'^api/v1/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^api/v1/(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    # url(r'^api/v1/redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# extra

from .extra_urls import urlpatterns as extra_urlpatterns
from .extra_urls import i18n_urlpatterns as extra_i18n_urlpatterns

if len(extra_urlpatterns) > 0:
    urlpatterns += extra_urlpatterns

if settings.I18N_PATH_ENABLED:
    if len(extra_i18n_urlpatterns) > 0:
        urlpatterns += i18n_patterns(extra_i18n_urlpatterns)  #  + [])
else:
    if len(extra_i18n_urlpatterns) > 0:
        urlpatterns += extra_i18n_urlpatterns  # + []

# flatpages
urlpatterns += [
    path('<path:url>', include('django.contrib.flatpages.urls')),
]

# print('URLPATTERNS', urlpatterns)

# -- coding: utf-8 --
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path
from django.views.generic.base import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

import compose.connectors.api as connector_api

urlpatterns = [
    path(
        "",
        RedirectView.as_view(url="/static/", permanent=True),
        name="index",
    ),
]

urlpatterns += [
    re_path("^api/token/auth/?$", TokenObtainPairView.as_view(), name="token_obtain"),
    re_path("^api/token/verify/?$", TokenVerifyView.as_view(), name="token_verify"),
    re_path("^api/token/refresh/?$", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/", include("rest_framework.urls", namespace="rest_framework")),
]

urlpatterns += [
    re_path(r"^api/get_config/?$", connector_api.get_config, name="get_config"),
    re_path(  # To not support anymore going forward, unused
        r"^api/get_namespaces/(?P<interface>[\w\-]+)/?$",
        connector_api.get_namespaces,
        name="get_namespaces",
    ),
]

urlpatterns += [
    path("api/editor/", include("compose.editor.urls", namespace="editor")),
]

urlpatterns += [
    path("connectors/v1/", include("compose.connectors.urls", namespace="connectors"))
]

urlpatterns += [
    path("desktop/", include("compose.connectors.urls_hue4", namespace="hue4-desktop")),
    path("notebook/api/", include("compose.editor.urls_hue4", namespace="hue4-editor")),
]


urlpatterns += [
    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

from django.conf.urls import url, include
from enrichapp.dashboard.control.urls import control_urlpatterns
from enrichapp.dashboard.audit.urls import audit_urlpatterns
from enrichapp.dashboard.catalog.urls import catalog_urlpatterns
from enrichapp.dashboard.persona.urls import persona_urlpatterns
from enrichapp.dashboard.filerenderer.urls import filerenderer_urlpatterns
from enrichapp.dashboard.marketplace.urls import marketplace_urlpatterns, get_marketplace_urls

from . import views

app_name = "APPNAME"

# => Base
urlpatterns = [
    url('^[/]?$', views.index, name="index"),

]

#from . import persona
#searchspec = persona.get_spec()
#urlpatterns += [
#    url(r'^persona/', include((persona_urlpatterns, "persona"),
#                               namespace="persona"),
#        {
#            'spec': searchspec
#        })
#]

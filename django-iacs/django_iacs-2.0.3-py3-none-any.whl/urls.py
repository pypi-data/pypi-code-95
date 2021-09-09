from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url
from rest_framework.routers import SimpleRouter

from .channels.consumer import MessageConsumer
from .viewsets.api import ApiViewSet
from .viewsets.group import PermissionGroupViewSet
from .viewsets.menus import MenuViewSet
from .viewsets.operation_log import OperationLogViewSet
from .viewsets.users import UserViewSet

URL_PREFIX = 'api/iacs'

router = SimpleRouter()

router.register(f'{URL_PREFIX}/user', UserViewSet)
router.register(f'{URL_PREFIX}/menu', MenuViewSet)
router.register(f'{URL_PREFIX}/api', ApiViewSet)
router.register(f'{URL_PREFIX}/group', PermissionGroupViewSet)
router.register(f'{URL_PREFIX}/operation_log', OperationLogViewSet)

urlpatterns = router.urls

route_groups = [
    {"name": "IACS", "routers": [router]}
]

# websocket路由
server_url = [
    url(r'server/$', MessageConsumer.as_asgi())
]

application = ProtocolTypeRouter({
    "websocket": URLRouter(server_url)
})

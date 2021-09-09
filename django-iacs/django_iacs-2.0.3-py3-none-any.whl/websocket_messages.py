from .channels.handlers import *
from .channels.messages.messages import *
from .channels.messages.router import DefaultRouter

router = DefaultRouter()

router.register(SnowFlakeRequest, SnowFlakeRequestHandler, SnowFlakeResponse)

# 服务器时间
router.register(ServerTimeRequest,
                ServerTimeRequestHandler,
                ServerTimeResponse)
# ping
router.register(UserPingRequest,
                UserPingRequestHandler,
                UserPingResponse)

routes = router.routes

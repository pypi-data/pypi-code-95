from channels.layers import get_channel_layer


class BaseHandler:

    def __init__(self, channel_name, channel_group_name, route):
        self.channel_name = channel_name
        self.channel_group_name = channel_group_name
        self.route = route
        self.response_serializer_class, self.response_handler_class = self.route[2:]
        self.channel_layer = get_channel_layer()

    async def do(self, *args, **kwargs):
        raise NotImplementedError()

    def get_response_serializer(self, **kwargs):
        s = self.response_serializer_class(data=kwargs)
        s.is_valid(raise_exception=True)
        return s

class MessageRouter:
    routes = {}

    def register(self, request_serializer_class=None,
                 request_handler_class=None,
                 response_serializer_class=None,
                 response_handler_class=None):
        if request_serializer_class is not None:
            request_type = request_serializer_class.Meta.MSG_TYPE

            # 将request和response的类型都作为key保存起来，方便使用
            self._register(request_type,
                           request_serializer_class,
                           request_handler_class,
                           response_serializer_class,
                           response_handler_class)

        if response_serializer_class is not None:
            response_type = response_serializer_class.Meta.MSG_TYPE
            self._register(response_type,
                           request_serializer_class,
                           request_handler_class,
                           response_serializer_class,
                           response_handler_class)

    def _register(self, _type, request_serializer_class,
                  request_handler_class=None,
                  response_serializer_class=None,
                  response_handler_class=None):
        if _type not in self.routes.keys():
            self.routes.update({
                _type: (
                    request_serializer_class,
                    request_handler_class,
                    response_serializer_class,
                    response_handler_class
                )
            })
        else:
            raise Exception(f'重复定义的消息类型, {_type}')


DefaultRouter = MessageRouter

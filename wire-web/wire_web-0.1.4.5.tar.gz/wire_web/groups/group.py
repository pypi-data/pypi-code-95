from wire_web.typings import CoroutineFunction


class Group:
    def __init__(self):
        self.routes: list = []

    def get(self, path: str):
        def wrapper(handler: CoroutineFunction) -> CoroutineFunction:
            self.routes.append((path, handler, "get"))
            return handler
        return wrapper

    def post(self, path: str):
        def wrapper(handler: CoroutineFunction) -> CoroutineFunction:
            self.routes.append((path, handler, "post"))
            return handler
        return wrapper

    def put(self, path: str):
        def wrapper(handler: CoroutineFunction) -> CoroutineFunction:
            self.routes.append((path, handler, "put"))
            return handler
        return wrapper

    def delete(self, path: str):
        def wrapper(handler: CoroutineFunction) -> CoroutineFunction:
            self.routes.append((path, handler, "delete"))
            return handler
        return wrapper

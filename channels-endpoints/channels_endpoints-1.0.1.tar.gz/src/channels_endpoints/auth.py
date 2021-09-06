class BasePermission:
    def __init__(self, request):
        self.request = request
        self.user = self.request.scope['user']
        self.path = f'{self.__class__.__module__}.{self.__class__.__name__}'

    async def check_perm(self):
        raise NotImplementedError

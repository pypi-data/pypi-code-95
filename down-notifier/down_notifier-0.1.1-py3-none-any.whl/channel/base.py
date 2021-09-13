class BaseChannel:
    def __init__(self, name: str, message: str, **kwargs) -> None:
        self.name = name
        self._message = message

    async def notify(self, url: str, status: int) -> None:
        raise NotImplementedError
